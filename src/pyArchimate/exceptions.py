"""
Exception hierarchy for Archimate model operations.

This module defines all custom exception types used throughout pyArchimate,
including domain-specific validation errors.

No external pyArchimate imports - this is a Layer 1 base module.
"""

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
