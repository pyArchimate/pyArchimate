"""Parsing utilities for Archi XML and data type conversions."""


def parse_bool(value: str | None) -> bool:
    """
    Parse string to boolean per W3C xsd:boolean semantics.

    Converts XML boolean string values to Python bool, handling various formats
    and case variations per the XML Schema specification.

    Args:
        value: String from XML ("true", "false", "1", "0", None, whitespace, etc.)

    Returns:
        True if value matches "true" or "1" (case-insensitive, whitespace trimmed)
        False otherwise (including None, empty string, invalid values)

    Examples:
        >>> parse_bool("true")
        True
        >>> parse_bool("false")
        False
        >>> parse_bool("TRUE")
        True
        >>> parse_bool("1")
        True
        >>> parse_bool("0")
        False
        >>> parse_bool(None)
        False
        >>> parse_bool("  true  ")
        True
        >>> parse_bool("")
        False
    """
    if value is None:
        return False
    normalized = str(value).lower().strip()
    return normalized in ("true", "1")


def extract_images_from_archimate(element) -> list[str]:
    """
    Extract base64-encoded image data from Archi XML element.

    Searches for image elements (graphics, diagram elements with embedded images)
    and extracts their base64-encoded data.

    Args:
        element: lxml Element from parsed Archi XML

    Returns:
        List of base64 strings in extraction order. Empty list if no images found.
    """
    images = []
    # Search for elements with image data (typically stored as base64 in attributes or text)
    for img_elem in element.findall(".//image"):
        data = img_elem.get("data")
        if data:
            images.append(data)
    # Also check for embedded image data in properties
    for prop_elem in element.findall(".//property[@key='image']"):
        data = prop_elem.get("value")
        if data:
            images.append(data)
    return images


def compare_image_data(data1: str | None, data2: str | None) -> bool:
    """
    Compare two base64-encoded image data strings for byte-for-byte equality.

    Args:
        data1: First base64 string
        data2: Second base64 string

    Returns:
        True if both strings are identical (byte-for-byte), False otherwise
    """
    if data1 is None and data2 is None:
        return True
    if data1 is None or data2 is None:
        return False
    return data1 == data2
