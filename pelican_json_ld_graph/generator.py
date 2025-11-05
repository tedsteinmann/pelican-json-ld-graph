"""
Generator module for JSON-LD graph creation
"""

import json
import os
import logging
from pelican import signals
from .utils import (
    load_mappings,
    get_entity_type,
    convert_metadata_to_jsonld,
    write_json_file,
    escape_json_for_html
)

logger = logging.getLogger(__name__)

# Global storage for entities across generators
_entities = []
_entity_map = {}
_settings = None
_output_path = None
_mappings = None


def initialize_jsonld(pelican):
    """Initialize JSON-LD generation for a Pelican instance."""
    global _settings, _output_path, _mappings, _entities, _entity_map

    _settings = pelican.settings
    _output_path = pelican.output_path
    _entities = []
    _entity_map = {}

    # Load mappings
    mappings_file = _settings.get('JSONLD_MAPPINGS_FILE', 'mappings.json')
    if not os.path.isabs(mappings_file):
        # Look for mappings.json in the Pelican path (project root)
        base_path = _settings.get('PATH', '')
        if base_path:
            parent_path = os.path.dirname(os.path.abspath(base_path))
            mappings_file = os.path.join(parent_path, mappings_file)

    _mappings = load_mappings(mappings_file)
    logger.info("JSON-LD Graph Generator initialized")


def process_content(content):
    """
    Process a single content item (article or page).

    Args:
        content: Pelican content object
    """
    global _entities, _entity_map, _settings, _mappings

    if not _settings or not _mappings:
        return

    # Skip content that doesn't have basic attributes
    if not hasattr(content, 'title') or not content.title:
        return
    
    # Skip content that doesn't have a slug (usually indicates malformed content)
    if not hasattr(content, 'slug') or not content.slug:
        return

    # Filter content based on status
    # Get allowed statuses from settings, default to only 'published'
    allowed_statuses = _settings.get('JSONLD_ALLOWED_STATUSES', ['published'])
    
    # Check if content has a status and if it's in the allowed list
    if hasattr(content, 'status'):
        content_status = str(content.status).lower()
        if content_status not in [status.lower() for status in allowed_statuses]:
            return
    elif hasattr(content, 'metadata') and content.metadata and 'status' in content.metadata:
        content_status = str(content.metadata['status']).lower()
        if content_status not in [status.lower() for status in allowed_statuses]:
            return
    else:
        # If no status is found, assume it's published (default Pelican behavior)
        if 'published' not in [status.lower() for status in allowed_statuses]:
            return

    try:
        # Get metadata
        metadata = {}

        # Extract relevant fields with safety checks
        if hasattr(content, 'title') and content.title:
            metadata['title'] = str(content.title)
        if hasattr(content, 'summary') and content.summary:
            metadata['summary'] = str(content.summary)
        if hasattr(content, 'tags') and content.tags:
            metadata['tags'] = [str(tag) for tag in content.tags]
        if hasattr(content, 'date') and content.date:
            metadata['date'] = content.date
        
        # Handle URL - check for custom URL in metadata first, then fall back to content.url
        url_value = None
        if hasattr(content, 'metadata') and content.metadata and 'url' in content.metadata:
            # Use custom URL from frontmatter if it exists
            url_value = str(content.metadata['url'])
        elif hasattr(content, 'url') and content.url:
            # Use generated Pelican URL
            url_value = str(content.url)
        
        if url_value:
            # If it's already a full URL (starts with http/https), use it as-is
            if url_value.startswith(('http://', 'https://')):
                metadata['url'] = url_value
            else:
                # Otherwise, prepend the site URL
                siteurl = _settings.get('SITEURL', '') or ''
                metadata['url'] = f"{siteurl}/{url_value}" if siteurl else url_value

        # Check for image in metadata
        if hasattr(content, 'metadata') and content.metadata:
            if 'image' in content.metadata and content.metadata['image']:
                image_value = str(content.metadata['image'])
                siteurl = _settings.get('SITEURL', '') or ''
                
                # Handle image URLs - make relative paths absolute
                if image_value.startswith('/'):
                    # It's a relative path from site root, make it absolute
                    metadata['image'] = f"{siteurl}{image_value}" if siteurl else image_value
                elif image_value.startswith(('http://', 'https://')):
                    # It's already a full URL, use as-is
                    metadata['image'] = image_value
                else:
                    # It's a relative path, assume it's from site root
                    metadata['image'] = f"{siteurl}/{image_value}" if siteurl else image_value

        # Determine entity type from category
        category_name = None
        if hasattr(content, 'category') and content.category and content.category.name:
            category_name = str(content.category.name)
        
        entity_type = get_entity_type(category_name, _mappings)

        # Convert to JSON-LD
        entity = convert_metadata_to_jsonld(metadata, entity_type, _mappings)

        # Store entity
        _entities.append(entity)

        # Map entity to slug for injection
        if hasattr(content, 'slug') and content.slug:
            _entity_map[str(content.slug)] = entity

        title = metadata.get('title', 'Untitled') or 'Untitled'
        entity_type_str = str(entity_type) if entity_type else 'Unknown'
        logger.debug(f"Processed {entity_type_str}: {title}")
    
    except Exception as e:
        # Add more detailed error information
        import traceback
        content_title = getattr(content, 'title', 'Unknown') if hasattr(content, 'title') else 'Unknown'
        content_slug = getattr(content, 'slug', 'Unknown') if hasattr(content, 'slug') else 'Unknown'
        logger.error(f"Error processing content '{content_title}' (slug: {content_slug}): {e}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Don't re-raise to prevent build failures


def write_jsonld_files(pelican):
    """Write JSON-LD files after all content is processed."""
    global _entities, _entity_map, _settings, _output_path

    if not _entities:
        logger.info("No entities to export")
        return

    logger.info(f"Starting JSON-LD graph generation with {len(_entities)} entities...")

    # Configuration
    jsonld_output_path = _settings.get('JSONLD_OUTPUT_PATH', 'jsonld')
    graph_filename = _settings.get('JSONLD_GRAPH_FILENAME', 'graph.jsonld')
    export_individual = _settings.get('JSONLD_EXPORT_INDIVIDUAL', True)

    # Write global graph
    graph = {
        "@context": "https://schema.org/",
        "@graph": _entities
    }

    output_dir = os.path.join(_output_path, jsonld_output_path)
    graph_path = os.path.join(output_dir, graph_filename)

    write_json_file(graph, graph_path, indent=2)
    logger.info(f"✅ Global graph written to {graph_path}")

    # Export individual entities if enabled
    if export_individual:
        count = 0
        for slug, entity in _entity_map.items():
            if slug:  # Only process if slug is not None
                entity_path = os.path.join(output_dir, f"{slug}.json")
                write_json_file(entity, entity_path, indent=2)
                count += 1

        logger.info(f"✅ Exported {count} individual entity files")


def inject_jsonld_into_content(content, content_path):
    """
    Inject JSON-LD script into HTML content.

    Args:
        content: HTML content string
        content_path: Path to the content file

    Returns:
        str: Modified HTML with JSON-LD injected
    """
    global _entity_map, _settings

    inject_enabled = _settings.get('JSONLD_INJECT', True)
    if not inject_enabled:
        return content

    # Extract slug from path
    slug = os.path.splitext(os.path.basename(content_path))[0]

    if slug not in _entity_map:
        return content

    entity = _entity_map[slug]

    # Generate JSON-LD script tag
    json_str = json.dumps(entity, indent=2, ensure_ascii=False)
    escaped_json = escape_json_for_html(json_str)
    script_tag = f'\n<script type="application/ld+json">\n{escaped_json}\n</script>\n'

    # Try to inject before </head>
    if '</head>' in content:
        content = content.replace('</head>', script_tag + '</head>', 1)
        logger.debug(f"Injected JSON-LD into <head> for {slug}")
    # Fallback to before </body>
    elif '</body>' in content:
        content = content.replace('</body>', script_tag + '</body>', 1)
        logger.debug(f"Injected JSON-LD into <body> for {slug}")

    return content


def content_written_handler(path, context):
    """Handle content_written signal to inject JSON-LD."""
    if not path or not path.endswith('.html'):
        return

    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        modified_content = inject_jsonld_into_content(content, path)

        if modified_content != content:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
    except Exception as e:
        logger.error(f"Error injecting JSON-LD into {path}: {e}")


def register():
    """Register plugin signals."""
    signals.initialized.connect(initialize_jsonld)
    signals.content_object_init.connect(process_content)
    signals.finalized.connect(write_jsonld_files)
    signals.content_written.connect(content_written_handler)
