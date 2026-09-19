"""Derived-relationship computation (spec 015-derived-relationships, GitHub issue #140).

Provides a read-only scan for explicit relationships that duplicate what a
two-step relationship chain already implies, and an on-demand query for the
relationship implied between two elements, per the ArchiMate derivation
rules (DR2, DR3, DR5, DR7, DR8) in ArchiMate 3.2 Specification, Appendix B
("Relationships (Normative)"), Section B.2 ("Derivation Rules for Valid
Relationships"), verified against a primary copy of the specification.
Nothing here ever writes to a Model, a Relationship, or a view: every
result is a transient dataclass.

Scope is restricted to the "certain" (valid, not merely potential)
derivation rules for the seven relationship types the issue named:
Composition, Aggregation, Assignment, Realization (the four *structural*
relationships, ArchiMate §5.1), Serving (one of the four *dependency*
relationships, §5.2 - Access/Influence/Association are excluded from this
feature's scope), and Triggering/Flow (the two *dynamic* relationships,
§5.3). Specialization (§5.4, "other") is excluded per the issue. Only
"in-line" two-step chains are considered (leg1's target is leg2's source,
i.e. a -> b -> c in the same direction) since that is the only chain shape
this feature discovers (see find_chains) - the specification's "opposing"
rules (DR4, DR6, where the second leg points *into* the intermediate
element instead of out of it) do not apply to this chain shape and are out
of scope.

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


def derive_pair_type(leg1_type: str, leg2_type: str) -> str | None:
    """
    Compute the relationship type implied by two relationships in sequence.

    Implements exactly DR2, DR3, DR5, DR7, and DR8 from ArchiMate 3.2
    Specification Appendix B.2 (see module docstring for page references and
    the deliberate asymmetries this preserves). Any pair not covered by one
    of those rules yields None - this function does not generalize beyond
    what the specification states as a "certain" (valid) derivation.

    :param leg1_type: type of the first leg (A to intermediate)
    :type leg1_type: str
    :param leg2_type: type of the second leg (intermediate to C)
    :type leg2_type: str
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
    return None


@dataclass(frozen=True)
class RelationshipChain:
    """
    Two existing, explicit relationships sharing a common intermediate element.

    :param leg1: the A-to-intermediate relationship
    :type leg1: Relationship
    :param leg2: the intermediate-to-C relationship
    :type leg2: Relationship
    """

    leg1: "Relationship"
    leg2: "Relationship"

    @property
    def intermediate(self) -> "Element":
        """The shared element B between leg1's target and leg2's source."""
        intermediate = self.leg1.target
        # Invariant guaranteed by find_chains(): leg1._target is only ever
        # used to build a chain after being confirmed present in
        # model.elems_dict, so this always resolves to a real Element.
        assert intermediate is not None, "chain invariant violated: leg1 has no resolvable target"
        return intermediate


def _qualifies_for_chaining(rel: "Relationship", model: "Model") -> bool:
    """
    True when a relationship's type and endpoints are eligible to form a chain leg.

    Factored out of :func:`find_chains` so both the index-building and the
    outer-leg scan share one FR-008/FR-011 check instead of repeating it.

    :param rel: the relationship to test
    :type rel: Relationship
    :param model: the model the relationship belongs to
    :type model: Model
    :return: whether the relationship may participate as either leg
    :rtype: bool
    """
    if rel.type not in SUPPORTED_RELATIONSHIP_TYPES:
        return False
    if rel._source not in model.elems_dict:
        return False
    return rel._target in model.elems_dict


def _index_qualifying_by_source(relationships: list["Relationship"], model: "Model") -> dict[str, list["Relationship"]]:
    """Group relationships eligible for chaining by their source element uuid."""
    by_source: dict[str, list[Relationship]] = {}
    for rel in relationships:
        if _qualifies_for_chaining(rel, model):
            by_source.setdefault(rel._source, []).append(rel)
    return by_source


def find_chains(model: "Model") -> list[RelationshipChain]:
    """
    Discover every qualifying two-step relationship chain in a model.

    A chain qualifies when: both legs reference elements present in the
    model (FR-011), the chain is not a self-referencing cycle (FR-009), and
    both legs use a relationship type from the supported subset (FR-008).
    Whether the pair of types actually yields a defined derived type is left
    to the caller via :func:`derive_pair_type`.

    :param model: the model to scan
    :type model: Model
    :return: every qualifying chain found
    :rtype: list[RelationshipChain]
    """
    relationships = list(model.rels_dict.values())
    by_source = _index_qualifying_by_source(relationships, model)

    chains: list[RelationshipChain] = []
    for leg1 in relationships:
        if not _qualifies_for_chaining(leg1, model):
            continue
        for leg2 in by_source.get(leg1._target, []):
            if leg2._target == leg1._source:
                continue  # FR-009: no self-referencing A->B->A cycles
            chains.append(RelationshipChain(leg1, leg2))

    return chains


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


def derive_between(model: "Model", source: Any, target: Any) -> list[DerivedRelationship]:
    """
    Compute the relationship(s) implied between two elements, without persisting them.

    :param model: the model to search for qualifying chains
    :type model: Model
    :param source: source Element or its uuid
    :type source: Element | str
    :param target: target Element or its uuid
    :type target: Element | str
    :return: zero or more DerivedRelationship results, one per independently
             qualifying chain connecting source to target (FR-005, FR-010)
    :rtype: list[DerivedRelationship]
    :raises ValueError: if source or target does not resolve to an element in the model
    """
    source_uuid = source if isinstance(source, str) else getattr(source, "uuid", None)
    target_uuid = target if isinstance(target, str) else getattr(target, "uuid", None)
    if source_uuid not in model.elems_dict:
        raise ValueError(f'Invalid source reference "{source_uuid}"')
    if target_uuid not in model.elems_dict:
        raise ValueError(f'Invalid target reference "{target_uuid}"')

    results: list[DerivedRelationship] = []
    for chain in find_chains(model):
        if chain.leg1._source != source_uuid or chain.leg2._target != target_uuid:
            continue
        derived_type = derive_pair_type(chain.leg1.type, chain.leg2.type)
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


def find_duplicate_relationships(model: "Model") -> list[DuplicateFinding]:
    """
    Scan a model for explicit relationships that duplicate an implied chain.

    :param model: the model to scan
    :type model: Model
    :return: one DuplicateFinding per explicit relationship found to be a
             duplicate, each citing every chain that independently implies it
    :rtype: list[DuplicateFinding]
    """
    chains = find_chains(model)
    implying_by_key: dict[tuple[str, str, str], list[RelationshipChain]] = {}
    for chain in chains:
        derived_type = derive_pair_type(chain.leg1.type, chain.leg2.type)
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
