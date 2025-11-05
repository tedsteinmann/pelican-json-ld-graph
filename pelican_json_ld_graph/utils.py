"""
Utility functions for JSON-LD generation
"""

import json
import os
import re
import logging

logger = logging.getLogger(__name__)

DEFAULT_MAPPINGS = {
    "categories": {
        "people": "Person",
        "organizations": "Organization",
        "experience": "WorkExperience",
        "projects": "CreativeWork",
        "certifications": "EducationalOccupationalCredential"
    },
    "fields": {
        "title": "name",
        "summary": "description",
        "tags": "keywords",
        "date": "dateCreated",
        "url": "url",
        "image": "image"
    }
}


def load_mappings(mappings_path=None):
    """
    Load mappings from mappings.json or return defaults.

    Args:
        mappings_path: Path to mappings.json file

    Returns:
        dict: Mapping configuration
    """
    if mappings_path and os.path.exists(mappings_path):
        try:
            with open(mappings_path, 'r', encoding='utf-8') as f:
                mappings = json.load(f)
                logger.info(f"Loaded mappings from {mappings_path}")
                return mappings
        except Exception as e:
            logger.warning(f"Failed to load mappings from {mappings_path}: {e}")
            logger.warning("Using default mappings")
    else:
        logger.info("No mappings.json found, using defaults")

    return DEFAULT_MAPPINGS


def get_entity_type(category_name, mappings):
    """
    Infer Schema.org entity type from Pelican category.

    Args:
        category_name: Category name from Pelican content (e.g., 'people', 'projects')
        mappings: Mapping configuration

    Returns:
        str: Schema.org type (e.g., 'Person', 'CreativeWork')
    """
    # Support both 'categories' (new) and 'folders' (deprecated) for backwards compatibility
    category_mappings = mappings.get('categories', mappings.get('folders', {}))

    if category_name:
        # Normalize category name to lowercase for case-insensitive matching
        category_key = category_name.lower()
        entity_type = category_mappings.get(category_key)
        if entity_type:
            return entity_type

    # Default to Thing if no mapping found
    return "Thing"


def convert_metadata_to_jsonld(metadata, entity_type, mappings):
    """
    Convert article metadata to JSON-LD entity.

    Args:
        metadata: Article metadata dictionary
        entity_type: Schema.org entity type
        mappings: Mapping configuration

    Returns:
        dict: JSON-LD entity
    """
    field_mappings = mappings.get('fields', {})

    entity = {
        "@type": entity_type
    }

    # Map metadata fields to JSON-LD properties
    for source_field, target_field in field_mappings.items():
        if source_field in metadata:
            value = metadata[source_field]

            # Handle None values
            if value is None:
                continue

            # Handle special cases
            if source_field == 'date' and hasattr(value, 'isoformat'):
                value = value.isoformat()
            elif source_field == 'tags' and isinstance(value, list):
                # Keep as list for keywords
                pass
            elif isinstance(value, (list, tuple)) and source_field != 'tags':
                # Convert other lists to first item or comma-separated string
                value = value[0] if value else ""

            # Strip HTML tags from text fields
            if isinstance(value, str) and source_field in ('summary', 'description'):
                # Remove HTML tags
                value = re.sub(r'<[^>]+>', '', value).strip()
            
            # Ensure value is not None before adding to entity
            if value is not None:
                entity[target_field] = value

    return entity


def write_json_file(data, output_path, indent=2):
    """
    Write JSON data to file.

    Args:
        data: Data to write
        output_path: Output file path
        indent: JSON indentation level
    """
    dir_path = os.path.dirname(output_path)
    if dir_path:  # Only create directory if path contains a directory component
        os.makedirs(dir_path, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)

    logger.debug(f"Wrote JSON to {output_path}")


def escape_json_for_html(json_str):
    """
    Escape JSON string for safe HTML injection.

    Args:
        json_str: JSON string

    Returns:
        str: Escaped JSON string
    """
    # Escape closing script tags and other problematic characters
    return (json_str
            .replace('</', '<\\/')
            .replace('</script>', '<\\/script>'))
