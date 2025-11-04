# Pelican Plugin: JSON-LD Graph Generator

A lightweight Pelican plugin that scans Markdown frontmatter across your content folders and automatically generates structured **JSON-LD metadata** for SEO, AI enrichment, and semantic indexing.

The plugin builds a global Schema.org graph (`graph.jsonld`) and optionally injects per-entity `<script type="application/ld+json">` tags into your rendered HTML pages.

---

## 🧭 Features

- 🔍 **Automatic JSON-LD generation** from Markdown frontmatter  
- 🏷️ **Category-based type inference** (e.g., `Category: people` → `Person`, `Category: projects` → `CreativeWork`)  
- 🧩 **Custom field mapping** via `mappings.json`  
- 🧾 **Global JSON-LD graph export** at build time  
- 💡 **Optional HTML injection** for per-page JSON-LD blocks  
- 🪶 Compatible with [Pelican 4.x+](https://docs.getpelican.com/)

---

## ⚙️ Installation

Clone the plugin into your Pelican project:

```bash
git clone https://github.com/tedsteinmann/pelican-jsonld-graph-generator.git plugins/pelican-jsonld-graph-generator
```

Then add it to your `pelicanconf.py`:

```python
PLUGIN_PATHS = ['plugins']
PLUGINS = ['pelican-jsonld-graph-generator']

# Optional configuration
JSONLD_OUTPUT_PATH = 'jsonld'
JSONLD_GRAPH_FILENAME = 'graph.jsonld'
JSONLD_EXPORT_INDIVIDUAL = True
JSONLD_INJECT = True
```

---

## 📁 Directory Structure

Your content can be organized in any folder structure. The plugin uses Pelican's built-in `Category` metadata field to determine entity types:

```
your-site/
├── content/
│   ├── articles/
│   │   ├── person1.md        # Category: people
│   │   ├── project1.md       # Category: projects
│   │   └── org1.md           # Category: organizations
│   ├── pages/
│   │   └── about.md          # Category: people
│   └── posts/
│       ├── work-exp.md       # Category: experience
│       └── cert.md           # Category: certifications
├── mappings.json
├── pelicanconf.py
└── plugins/
    └── pelican-jsonld-graph-generator/
        ├── __init__.py
        ├── generator.py
        ├── utils.py
        └── README.md
```

Each Markdown file should specify a category in its frontmatter:

```markdown
Title: Ted Steinmann
Date: 2024-01-15
Category: people
Summary: Builder, systems thinker, and strategist

Content goes here...
```

---

## 🧩 Example `mappings.json`

The `mappings.json` file maps Pelican categories to Schema.org types:

```json
{
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
```

**Note**: Category names in the mapping are case-insensitive. For backward compatibility, the plugin also supports `"folders"` as a key name (deprecated).

---

## 🚀 Usage

### Generate your Pelican site with JSON-LD

```bash
pelican content -o output -s pelicanconf.py
```

### View the exported graph

```bash
cat output/jsonld/graph.jsonld | jq .
```

### Example output (`graph.jsonld`)

```json
{
  "@context": "https://schema.org/",
  "@graph": [
    {
      "@type": "Person",
      "name": "Ted Steinmann",
      "description": "Builder, systems thinker, and strategist focused on high-ROI software.",
      "keywords": ["Product Management", "Automation", "Leadership"],
      "url": "https://ted.steinmann.me"
    },
    {
      "@type": "CreativeWork",
      "name": "Static Embeddings Agent",
      "description": "Generates JSON-LD metadata for Pelican static sites.",
      "keywords": ["Pelican", "SEO", "JSON-LD"]
    }
  ]
}
```

---

## 📦 Migration from Folder-Based to Category-Based Approach

If you're upgrading from a previous version that used folder structure for entity type detection, follow these steps:

### 1. Update your `mappings.json`

Change `"folders"` to `"categories"`:

```json
{
  "categories": {
    "people": "Person",
    ...
  }
}
```

**Note**: For backward compatibility, the old `"folders"` key still works, but `"categories"` is recommended.

### 2. Add category metadata to your content files

For each Markdown file, add a `Category:` field in the frontmatter:

```markdown
Title: Your Article Title
Date: 2024-01-15
Category: people
Summary: Your summary here

Your content...
```

### 3. Benefits of the new approach

- ✅ **Flexible organization**: Content can be organized in any folder structure
- ✅ **Pelican native**: Uses Pelican's built-in category system
- ✅ **Better SEO**: Categories are also used for site navigation and organization
- ✅ **Easier management**: Change entity types without moving files

---

## 🧪 Validation

Validate your structured data here:
- [Schema.org Validator](https://validator.schema.org/)
- [Google Rich Results Test](https://search.google.com/test/rich-results)

---

## 🛠 Development Setup

```bash
# (Optional) Create a venv
python3 -m venv .venv
source .venv/bin/activate

# Install Pelican if not present
pip install pelican

# Run the build
pelican content -o output -s pelicanconf.py
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🤝 Contributing

Pull requests are welcome!  
If you find bugs or have ideas for improvements, open an issue or PR on GitHub.

---

## ✨ Credits

Created by [Ted Steinmann](https://ted.steinmann.me)  
Designed for flexible JSON-LD integration in static-site workflows.
