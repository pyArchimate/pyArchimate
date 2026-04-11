"""
Exception hierarchy for Archimate model operations.

This module defines all custom exception types used throughout pyArchimate,
including domain-specific validation errors.

No external pyArchimate imports - this is a Layer 1 base module.
"""

try:  # pragma: no cover - exercised implicitly in compatibility tests
    from ._legacy import ArchimateConceptTypeError as LegacyArchimateConceptTypeError  # type: ignore
except Exception:  # ImportError or circular import safety
    LegacyArchimateConceptTypeError = None


class ArchimateError(Exception):
    """
    Base exception for all Archimate-related errors.
    """
    pass


class ArchimateRelationshipError(ArchimateError):
    """
    Raised when a relationship constraint is violated or an invalid relationship
    operation is attempted.
    """
    pass


class ArchimateConceptTypeError(ArchimateError):
    """
    Raised when an invalid or unsupported Archimate concept type is encountered.
    """

# Keep legacy compatibility by subclassing legacy type when present without
# importing it eagerly in downstream modules.
if LegacyArchimateConceptTypeError:
    ArchimateConceptTypeError.__bases__ = (LegacyArchimateConceptTypeError, ArchimateError)
