"""Derived-relationship computation (spec 015-derived-relationships, GitHub issue #140).

Provides a read-only scan for explicit relationships that duplicate what a
two-step relationship chain already implies, and an on-demand query for the
relationship implied between two elements, per the ArchiMate weakest-link
derivation rule. Nothing here ever writes to a Model, a Relationship, or a
view: every result is a transient dataclass.

Scope is restricted to the seven relationship types the rule's semantics are
unambiguous for: Composition, Aggregation, Assignment, Realization, Serving
(the "structural" subgroup) and Triggering, Flow (the "dynamic" subgroup).
Access, Influence, Specialization, and Association are intentionally left to
a human reviewer (see spec.md and research.md Decision 1).
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .element import Element
    from .model import Model
    from .relationship import Relationship

# Strongest to weakest. The derived type from two structural legs in sequence
# is always the weaker (higher-index) of the two - a total order, no undefined
# cells. See research.md Decision 1 for the sources this was cross-checked
# against.
_STRUCTURAL_STRENGTH_ORDER: tuple[str, ...] = (
    "Composition",
    "Aggregation",
    "Assignment",
    "Realization",
    "Serving",
)
_STRUCTURAL_INDEX: dict[str, int] = {name: i for i, name in enumerate(_STRUCTURAL_STRENGTH_ORDER)}

_DYNAMIC_TYPES: frozenset[str] = frozenset({"Triggering", "Flow"})

SUPPORTED_RELATIONSHIP_TYPES: frozenset[str] = frozenset(_STRUCTURAL_STRENGTH_ORDER) | _DYNAMIC_TYPES


def derive_pair_type(leg1_type: str, leg2_type: str) -> str | None:
    """
    Compute the relationship type implied by two relationships in sequence.

    :param leg1_type: type of the first leg (A to intermediate)
    :type leg1_type: str
    :param leg2_type: type of the second leg (intermediate to C)
    :type leg2_type: str
    :return: the derived relationship type, or None if this pair does not
             yield a defined derivation (either leg is outside the supported
             subset, or the legs come from different subgroups)
    :rtype: str | None
    """
    if leg1_type in _STRUCTURAL_INDEX and leg2_type in _STRUCTURAL_INDEX:
        weaker_index = max(_STRUCTURAL_INDEX[leg1_type], _STRUCTURAL_INDEX[leg2_type])
        return _STRUCTURAL_STRENGTH_ORDER[weaker_index]
    if leg1_type in _DYNAMIC_TYPES and leg2_type in _DYNAMIC_TYPES:
        if leg1_type == "Triggering" and leg2_type == "Triggering":
            return "Triggering"
        return "Flow"
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
    chains: list[RelationshipChain] = []
    relationships = list(model.rels_dict.values())

    by_source: dict[str, list[Relationship]] = {}
    for rel in relationships:
        if rel.type not in SUPPORTED_RELATIONSHIP_TYPES:
            continue
        if rel._source not in model.elems_dict or rel._target not in model.elems_dict:
            continue
        by_source.setdefault(rel._source, []).append(rel)

    for leg1 in relationships:
        if leg1.type not in SUPPORTED_RELATIONSHIP_TYPES:
            continue
        if leg1._source not in model.elems_dict or leg1._target not in model.elems_dict:
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
