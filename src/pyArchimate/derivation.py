"""Derived-relationship computation (spec 015-derived-relationships, GitHub issue
#140; generalized to chains of any length by spec 016-derivation-n-hop,
GitHub issue #173).

Provides a read-only scan for explicit relationships that duplicate what a
relationship chain already implies, and an on-demand query for the
relationship implied between two elements, per the ArchiMate derivation
rules (DR2, DR3, DR5, DR7, DR8) in ArchiMate 3.2 Specification, Appendix B
("Relationships (Normative)"), Section B.2 ("Derivation Rules for Valid
Relationships"), verified against a primary copy of the specification.
Nothing here ever writes to a Model, a Relationship, or a view: every
result is a transient dataclass.

A chain may be any length of two or more relationships: the ArchiMate
derivation rule itself is not inherently limited to two hops - folding is
defined pairwise and can be applied repeatedly along a path of any length
(see :func:`_fold_chain_type`). This module's original two-step-only
behavior (spec 015) was this project's own deliberate scope decision, not a
reflection of a two-hop ceiling in the specification. ``max_chain_length``
(default ``2``, see :func:`find_chains`) controls how far every entry point
below searches; raising it opts into longer-chain discovery without
changing a single default-settings call's result (SC-003).

Scope is restricted to the "certain" (valid, not merely potential)
derivation rules for the seven relationship types the issue named:
Composition, Aggregation, Assignment, Realization (the four *structural*
relationships, ArchiMate §5.1), Serving (one of the four *dependency*
relationships, §5.2 - Access/Influence/Association are excluded from this
feature's scope), and Triggering/Flow (the two *dynamic* relationships,
§5.3). Specialization (§5.4, "other") is excluded per the issue. Only
"in-line" chains are considered (each leg's target is the next leg's
source, i.e. a -> b -> c -> ... in the same direction) since that is the
only chain shape this feature discovers (see find_chains) - the
specification's "opposing" rules (DR4, DR6, where the second leg points
*into* the intermediate element instead of out of it) do not apply to this
chain shape and are out of scope.

The rules implemented (leg1: a->b, leg2: b->c, both forward):

- DR2 (both legs structural): derive the weaker of the two, using the
  strength order Composition (strongest) > Aggregation > Assignment >
  Realization (weakest) given on ArchiMate 3.2 Spec p.128.
- DR3 (structural then Serving): derive Serving. (p.129)
- DR5 (structural then a dynamic relationship): derive that dynamic type
  (Triggering or Flow). (p.130)
- DR7 (Triggering then structural): derive Triggering. (p.130) Note this is
  *not* symmetric with Flow: the specification defines no equivalent
  "Flow then structural, in line" valid derivation (Flow only combines
  with structural relationships via the "opposing" DR6, which is out of
  scope here), so Flow-then-structural correctly yields no derivation.
- DR8 (Triggering then Triggering): derive Triggering, transitively.
  (p.131) Note this is *not* generalized to any other dynamic-dynamic
  pairing: the specification defines no "certain" rule for Flow+Flow,
  Flow+Triggering, or Triggering+Flow, so those correctly yield no
  derivation (they would only be reachable, if at all, via the lower-
  certainty "potential" derivation rules in Section B.3, which this
  feature does not implement).

Every other combination of the seven supported types yields no derivation,
by design, matching what Appendix B actually specifies rather than
generalizing beyond it.

Opt-in extended scope (GitHub issue #146): every chain-discovery and
derivation entry point below also accepts ``include_dependency: bool =
False``. When ``True``, Access, Influence, and Association become eligible
to participate in chains (per ArchiMate 3.2 §5.2's remaining dependency
relationships, all excluded by default above), and one additional,
best-effort rule from Appendix B.3 ("potential" derivation, a lower
certainty tier than the B.2 rules this module otherwise implements) is
applied: Influence-then-structural, forward, in-line derives Influence -
e.g. ``A -Influence-> B -Realization-> C`` implies ``A -Influence-> C``.
This generalizes the issue's named Influence-then-Realization case to any
structural second leg, on the same precedent as DR7 (Triggering-then-
structural). Access and Association become chainable but deliberately
yield no derivation of their own even when opted in: Access has
direction/type variants with no documented "certain" or "potential" rule to
generalize, and neither Influence nor Association has a formal strength
ordering, so no DR2-style weakest-link rule is invented for them. Default
behavior (flag unset/False) is completely unchanged from the above.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .element import Element
    from .model import Model
    from .relationship import Relationship

# Strongest to weakest (ArchiMate 3.2 Spec, Appendix B.2.2, p.128). Only the
# four structural relationships participate in this ordering - Serving is a
# *dependency* relationship (§5.2), not structural, despite earlier drafts of
# this module treating it as the "weakest structural" type.
_STRUCTURAL_STRENGTH_ORDER: tuple[str, ...] = (
    "Composition",
    "Aggregation",
    "Assignment",
    "Realization",
)
_STRUCTURAL_INDEX: dict[str, int] = {name: i for i, name in enumerate(_STRUCTURAL_STRENGTH_ORDER)}

# The one dependency relationship (of Serving/Access/Influence/Association)
# this feature is in scope for, per the issue's explicit scope statement.
_DEPENDENCY_TYPES_IN_SCOPE: frozenset[str] = frozenset({"Serving"})

_DYNAMIC_TYPES: frozenset[str] = frozenset({"Triggering", "Flow"})

SUPPORTED_RELATIONSHIP_TYPES: frozenset[str] = (
    frozenset(_STRUCTURAL_STRENGTH_ORDER) | _DEPENDENCY_TYPES_IN_SCOPE | _DYNAMIC_TYPES
)

# Issue #146 opt-in scope: the remaining three dependency relationships
# (§5.2), excluded from SUPPORTED_RELATIONSHIP_TYPES by default. Only
# Influence actually produces a derivation (see module docstring); Access
# and Association are included here purely for chaining eligibility.
_EXTENDED_DEPENDENCY_TYPES: frozenset[str] = frozenset({"Access", "Influence", "Association"})

# Spec 016-derivation-n-hop: the default longest chain (in relationships) a
# caller may request via max_chain_length before explicitly overriding this
# ceiling via allow_exceeding_default_ceiling=True.
#
# Cost-growth rationale (FR-013): find_chains() explores every qualifying
# path with a worklist, extending one leg at a time and pruning the moment a
# pair fails to fold (derive_pair_type returns None) or an element is
# revisited. For a model where each qualifying element has, on average, b
# outgoing qualifying relationships ("branching factor"), the worst-case
# number of partial paths explored grows roughly as O(b^max_chain_length) -
# each additional hop multiplies the search by another factor of b. In
# practice derive_pair_type's None-pruning (FR-003) and the no-revisit rule
# (FR-004) cut this down sharply well before the worst case, but the
# worst-case growth is still exponential in max_chain_length, not linear.
# DEFAULT_MAX_CHAIN_LENGTH_CEILING=6 was chosen as a value that comfortably
# covers realistic chain lengths in practice while keeping that exponential
# growth bounded by default; see tests/performance/test_performance_benchmarks.py
# (SC-004) for a measured comparison at max_chain_length=2 vs. a longer
# opted-in value on a ~1,000-element model. A caller raising
# allow_exceeding_default_ceiling=True should expect scan time to grow
# noticeably, not just proportionally, for each additional hop requested
# beyond this ceiling, especially in densely-connected models.
DEFAULT_MAX_CHAIN_LENGTH_CEILING: int = 6


def _enforce_chain_length_ceiling(max_chain_length: int, allow_exceeding_default_ceiling: bool) -> None:
    """
    Raise if a caller's requested chain length exceeds the documented default
    ceiling without an explicit opt-in (FR-011).

    :param max_chain_length: the caller's requested longest chain, in relationships
    :type max_chain_length: int
    :param allow_exceeding_default_ceiling: explicit acknowledgement of the
        performance tradeoff of exceeding DEFAULT_MAX_CHAIN_LENGTH_CEILING
    :type allow_exceeding_default_ceiling: bool
    :raises ValueError: if max_chain_length exceeds the ceiling and the
        override was not given
    """
    if max_chain_length > DEFAULT_MAX_CHAIN_LENGTH_CEILING and not allow_exceeding_default_ceiling:
        raise ValueError(
            f"max_chain_length={max_chain_length} exceeds the default ceiling of "
            f"{DEFAULT_MAX_CHAIN_LENGTH_CEILING}. Pass allow_exceeding_default_ceiling=True "
            "to search longer chains, accepting the performance tradeoff documented "
            "alongside DEFAULT_MAX_CHAIN_LENGTH_CEILING in this module."
        )


def derive_pair_type(leg1_type: str, leg2_type: str, include_dependency: bool = False) -> str | None:
    """
    Compute the relationship type implied by two relationships in sequence.

    Implements exactly DR2, DR3, DR5, DR7, and DR8 from ArchiMate 3.2
    Specification Appendix B.2 (see module docstring for page references and
    the deliberate asymmetries this preserves). Any pair not covered by one
    of those rules yields None - this function does not generalize beyond
    what the specification states as a "certain" (valid) derivation, unless
    ``include_dependency=True`` opts into the one additional best-effort
    rule described in the module docstring (issue #146).

    :param leg1_type: type of the first leg (A to intermediate)
    :type leg1_type: str
    :param leg2_type: type of the second leg (intermediate to C)
    :type leg2_type: str
    :param include_dependency: opt into the Influence-then-structural
        best-effort rule (default: False, matching the strict Appendix B.2
        scope)
    :type include_dependency: bool
    :return: the derived relationship type, or None if this pair does not
             yield a defined derivation
    :rtype: str | None
    """
    leg1_structural = leg1_type in _STRUCTURAL_INDEX
    leg2_structural = leg2_type in _STRUCTURAL_INDEX

    if leg1_structural and leg2_structural:  # DR2
        weaker_index = max(_STRUCTURAL_INDEX[leg1_type], _STRUCTURAL_INDEX[leg2_type])
        return _STRUCTURAL_STRENGTH_ORDER[weaker_index]
    if leg1_structural and leg2_type in _DEPENDENCY_TYPES_IN_SCOPE:  # DR3
        return leg2_type
    if leg1_structural and leg2_type in _DYNAMIC_TYPES:  # DR5
        return leg2_type
    if leg1_type == "Triggering" and leg2_structural:  # DR7
        return "Triggering"
    if leg1_type == "Triggering" and leg2_type == "Triggering":  # DR8
        return "Triggering"
    if include_dependency and leg1_type == "Influence" and leg2_structural:  # issue #146
        return "Influence"
    return None


@dataclass(frozen=True)
class RelationshipChain:
    """
    Two or more existing, explicit relationships, each sharing an
    intermediate element with the next ("N-Hop Relationship Path" in
    spec 016-derivation-n-hop; generalizes the original exactly-two-leg
    chain from spec 015).

    :param legs: the ordered relationships making up the chain, from the
        source-most leg to the target-most leg
    :type legs: list[Relationship]
    """

    legs: list["Relationship"]

    def __post_init__(self) -> None:
        if len(self.legs) < 2:
            raise ValueError("RelationshipChain requires at least two legs")

    @property
    def leg1(self) -> "Relationship":
        """The first (source-most) leg - preserved for spec 015 callers."""
        return self.legs[0]

    @property
    def leg2(self) -> "Relationship":
        """The last (target-most) leg - preserved for spec 015 callers.

        For a two-leg chain this is the same relationship spec 015 callers
        already expect; for a longer chain it is the final leg, matching
        the generalized leg1/leg2 "endpoints" convention.
        """
        return self.legs[-1]

    @property
    def intermediate(self) -> "Element | list[Element]":
        """
        The shared element(s) between consecutive legs.

        Returns a single :class:`Element` when this chain has exactly two
        legs (byte-for-byte compatible with every spec 015 caller that
        reads ``chain.intermediate`` as a scalar), or a list of the
        ``len(legs) - 1`` intermediate elements for a longer chain.
        """
        raw_intermediates = [leg.target for leg in self.legs[:-1]]
        intermediates: list[Element] = []
        for element in raw_intermediates:
            # Invariant guaranteed by find_chains(): every leg's target is
            # only ever used to build a chain after being confirmed present
            # in model.elems_dict, so this always resolves to a real Element.
            assert element is not None, "chain invariant violated: a leg has no resolvable target"
            intermediates.append(element)
        if len(intermediates) == 1:
            return intermediates[0]
        return intermediates


def _qualifies_for_chaining(rel: "Relationship", model: "Model", include_dependency: bool = False) -> bool:
    """
    True when a relationship's type and endpoints are eligible to form a chain leg.

    Factored out of :func:`find_chains` so both the index-building and the
    outer-leg scan share one FR-008/FR-011 check instead of repeating it.

    :param rel: the relationship to test
    :type rel: Relationship
    :param model: the model the relationship belongs to
    :type model: Model
    :param include_dependency: also accept the issue #146 opt-in scope
        (Access, Influence, Association)
    :type include_dependency: bool
    :return: whether the relationship may participate as either leg
    :rtype: bool
    """
    supported = SUPPORTED_RELATIONSHIP_TYPES
    if include_dependency:
        supported = supported | _EXTENDED_DEPENDENCY_TYPES
    if rel.type not in supported:
        return False
    if rel._source not in model.elems_dict:
        return False
    return rel._target in model.elems_dict


def _index_qualifying_by_source(
    relationships: list["Relationship"], model: "Model", include_dependency: bool = False
) -> dict[str, list["Relationship"]]:
    """Group relationships eligible for chaining by their source element uuid."""
    by_source: dict[str, list[Relationship]] = {}
    for rel in relationships:
        if _qualifies_for_chaining(rel, model, include_dependency):
            by_source.setdefault(rel._source, []).append(rel)
    return by_source


def _fold_chain_type(legs: list["Relationship"], include_dependency: bool = False) -> str | None:
    """
    Compute the fully-folded relationship type implied by a chain of any
    length, by applying :func:`derive_pair_type` repeatedly, left to right
    (spec 016-derivation-n-hop FR-002): the result of legs 1+2 becomes the
    running type combined with leg 3, and so on. Never invents a new
    combination rule - this is purely repeated application of the existing,
    unmodified two-leg table.

    :param legs: the chain's relationships, source-most to target-most
    :type legs: list[Relationship]
    :param include_dependency: opt into the issue #146 extended scope
    :type include_dependency: bool
    :return: the fully-folded type, or None the moment any adjacent pair
             (original or already-folded) has no defined rule (FR-003)
    :rtype: str | None
    """
    running_type: str = legs[0].type
    for leg in legs[1:]:
        folded = derive_pair_type(running_type, leg.type, include_dependency)
        if folded is None:
            return None
        running_type = folded
    return running_type


def find_chains(
    model: "Model",
    include_dependency: bool = False,
    max_chain_length: int = 2,
    *,
    allow_exceeding_default_ceiling: bool = False,
) -> list[RelationshipChain]:
    """
    Discover every qualifying relationship chain in a model, up to
    max_chain_length relationships long.

    A chain qualifies when: every leg references elements present in the
    model (FR-008), the chain does not revisit any element it has already
    passed through, for chains of any length (FR-004), every leg uses a
    relationship type from the supported subset (FR-008), and the chain
    folds successfully end to end via repeated application of
    :func:`derive_pair_type` (FR-002, FR-003) - a path is abandoned the
    moment any adjacent pair (original or already-folded) has no defined
    rule, rather than being discovered as an unfoldable "chain" a caller
    would have to filter out themselves (research.md Decision 1, "fused
    pruning").

    :param model: the model to scan
    :type model: Model
    :param include_dependency: opt into the issue #146 extended scope
        (Access, Influence, Association also eligible as chain legs;
        default: False, matching the strict Appendix B.2 scope)
    :type include_dependency: bool
    :param max_chain_length: the longest chain, in relationships, to
        discover; default of 2 reproduces exactly the pre-spec-016
        two-step-only behavior (FR-010)
    :type max_chain_length: int
    :param allow_exceeding_default_ceiling: required True to pass
        max_chain_length above DEFAULT_MAX_CHAIN_LENGTH_CEILING (FR-011)
    :type allow_exceeding_default_ceiling: bool
    :return: every qualifying, fully-foldable chain found, each two legs
             or longer
    :rtype: list[RelationshipChain]
    :raises ValueError: if max_chain_length exceeds the default ceiling
        without the explicit override
    """
    _enforce_chain_length_ceiling(max_chain_length, allow_exceeding_default_ceiling)
    relationships = list(model.rels_dict.values())
    by_source = _index_qualifying_by_source(relationships, model, include_dependency)

    chains: list[RelationshipChain] = []
    # Worklist of in-progress partial paths: (legs so far, visited element
    # uuids, running folded type). Explicit iterative worklist rather than
    # recursion, since a caller may raise max_chain_length well past typical
    # recursion-depth comfort (FR-011).
    worklist: list[tuple[list[Relationship], set[str], str]] = _seed_chain_worklist(
        relationships, model, include_dependency
    )

    while worklist:
        legs, visited, running_type = worklist.pop()
        if len(legs) >= 2:
            chains.append(RelationshipChain(legs=list(legs)))
        if len(legs) >= max_chain_length:
            continue
        worklist.extend(_extend_chain(legs, visited, running_type, by_source, include_dependency))

    return chains


def _seed_chain_worklist(
    relationships: list["Relationship"], model: "Model", include_dependency: bool
) -> list[tuple[list["Relationship"], set[str], str]]:
    """Build the initial one-leg worklist entries for :func:`find_chains`."""
    worklist: list[tuple[list[Relationship], set[str], str]] = []
    for leg1 in relationships:
        if _qualifies_for_chaining(leg1, model, include_dependency):
            worklist.append(([leg1], {leg1._source, leg1._target}, leg1.type))
    return worklist


def _extend_chain(
    legs: list["Relationship"],
    visited: set[str],
    running_type: str,
    by_source: dict[str, list["Relationship"]],
    include_dependency: bool,
) -> list[tuple[list["Relationship"], set[str], str]]:
    """Compute the next-hop worklist entries reachable from a partial chain."""
    extensions: list[tuple[list[Relationship], set[str], str]] = []
    last_target = legs[-1]._target
    for next_leg in by_source.get(last_target, []):
        if next_leg._target in visited:
            continue  # FR-004: no element revisited, for chains of any length
        folded_type = derive_pair_type(running_type, next_leg.type, include_dependency)
        if folded_type is None:
            continue  # FR-003: abandon the path, no partial result
        extensions.append((legs + [next_leg], visited | {next_leg._target}, folded_type))
    return extensions


@dataclass(frozen=True)
class DerivedRelationship:
    """
    A transient relationship implied by a qualifying :class:`RelationshipChain`.

    Deliberately not a :class:`~pyArchimate.relationship.Relationship`
    subclass and never registered in a model's dictionaries, so it can never
    be persisted or mistaken for a modeled relationship (FR-006, FR-007).

    :param source: the chain's starting element
    :type source: Element
    :param target: the chain's ending element
    :type target: Element
    :param type: the derived ArchiMate relationship type
    :type type: str
    :param chain: the chain that produced this result
    :type chain: RelationshipChain
    """

    source: "Element"
    target: "Element"
    type: str
    chain: RelationshipChain
    is_derived: bool = True

    def __str__(self) -> str:
        src = getattr(self.source, "name", None) or self.source
        tgt = getattr(self.target, "name", None) or self.target
        return f"«derived» {src} -{self.type}-> {tgt}"

    def __repr__(self) -> str:
        # Overridden (rather than left as the dataclass default) so the
        # "always marked as derived" guarantee (FR-007/SC-003) holds for
        # repr() output too, e.g. when a caller inspects a list of results
        # in a REPL or includes one in a larger structure's repr.
        return f"<{self.__class__.__name__} {self}>"


def derive_between(
    model: "Model",
    source: Any,
    target: Any,
    include_dependency: bool = False,
    max_chain_length: int = 2,
    *,
    allow_exceeding_default_ceiling: bool = False,
) -> list[DerivedRelationship]:
    """
    Compute the relationship(s) implied between two elements, without persisting them.

    :param model: the model to search for qualifying chains
    :type model: Model
    :param source: source Element or its uuid
    :type source: Element | str
    :param target: target Element or its uuid
    :type target: Element | str
    :param include_dependency: opt into the issue #146 extended scope
        (Access, Influence, Association; default: False, matching the
        strict Appendix B.2 scope)
    :type include_dependency: bool
    :param max_chain_length: longest chain, in relationships, to consider;
        default of 2 reproduces exactly the pre-spec-016 behavior (FR-010)
    :type max_chain_length: int
    :param allow_exceeding_default_ceiling: required True to pass
        max_chain_length above DEFAULT_MAX_CHAIN_LENGTH_CEILING (FR-011)
    :type allow_exceeding_default_ceiling: bool
    :return: zero or more DerivedRelationship results, one per independently
             qualifying chain connecting source to target (FR-005, FR-010)
    :rtype: list[DerivedRelationship]
    :raises ValueError: if source or target does not resolve to an element in
        the model, or max_chain_length exceeds the ceiling without the override
    """
    source_uuid = source if isinstance(source, str) else getattr(source, "uuid", None)
    target_uuid = target if isinstance(target, str) else getattr(target, "uuid", None)
    if source_uuid not in model.elems_dict:
        raise ValueError(f'Invalid source reference "{source_uuid}"')
    if target_uuid not in model.elems_dict:
        raise ValueError(f'Invalid target reference "{target_uuid}"')

    results: list[DerivedRelationship] = []
    chains = find_chains(
        model,
        include_dependency,
        max_chain_length,
        allow_exceeding_default_ceiling=allow_exceeding_default_ceiling,
    )
    for chain in chains:
        if chain.leg1._source != source_uuid or chain.leg2._target != target_uuid:
            continue
        derived_type = _fold_chain_type(chain.legs, include_dependency)
        if derived_type is None:
            continue
        chain_source, chain_target = chain.leg1.source, chain.leg2.target
        # Invariant guaranteed by find_chains(): both endpoints were
        # confirmed present in model.elems_dict before the chain was built.
        assert chain_source is not None, "chain invariant violated: leg1 has no resolvable source"
        assert chain_target is not None, "chain invariant violated: leg2 has no resolvable target"
        results.append(
            DerivedRelationship(
                source=chain_source,
                target=chain_target,
                type=derived_type,
                chain=chain,
            )
        )
    return results


@dataclass(frozen=True)
class DuplicateFinding:
    """
    An explicit relationship that duplicates what one or more chains already imply.

    :param relationship: the existing, explicit, modeled relationship being flagged
    :type relationship: Relationship
    :param implying_chains: the chain(s) whose derived result matches it exactly
    :type implying_chains: list[RelationshipChain]
    """

    relationship: "Relationship"
    implying_chains: list[RelationshipChain]


def find_duplicate_relationships(
    model: "Model",
    include_dependency: bool = False,
    max_chain_length: int = 2,
    *,
    allow_exceeding_default_ceiling: bool = False,
) -> list[DuplicateFinding]:
    """
    Scan a model for explicit relationships that duplicate an implied chain.

    :param model: the model to scan
    :type model: Model
    :param include_dependency: opt into the issue #146 extended scope
        (Access, Influence, Association; default: False, matching the
        strict Appendix B.2 scope)
    :type include_dependency: bool
    :param max_chain_length: longest chain, in relationships, to consider;
        default of 2 reproduces exactly the pre-spec-016 behavior (FR-010)
    :type max_chain_length: int
    :param allow_exceeding_default_ceiling: required True to pass
        max_chain_length above DEFAULT_MAX_CHAIN_LENGTH_CEILING (FR-011)
    :type allow_exceeding_default_ceiling: bool
    :return: one DuplicateFinding per explicit relationship found to be a
             duplicate, each citing every chain that independently implies it
    :rtype: list[DuplicateFinding]
    :raises ValueError: if max_chain_length exceeds the ceiling without the override
    """
    chains = find_chains(
        model,
        include_dependency,
        max_chain_length,
        allow_exceeding_default_ceiling=allow_exceeding_default_ceiling,
    )
    implying_by_key: dict[tuple[str, str, str], list[RelationshipChain]] = {}
    for chain in chains:
        derived_type = _fold_chain_type(chain.legs, include_dependency)
        if derived_type is None:
            continue
        key = (chain.leg1._source, chain.leg2._target, derived_type)
        implying_by_key.setdefault(key, []).append(chain)

    findings: list[DuplicateFinding] = []
    for rel in model.rels_dict.values():
        key = (rel._source, rel._target, rel.type)
        implying_chains = implying_by_key.get(key)
        if implying_chains:
            findings.append(DuplicateFinding(relationship=rel, implying_chains=implying_chains))
    return findings
