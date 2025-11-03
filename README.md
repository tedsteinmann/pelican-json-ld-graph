# Pelican Plugin: JSON-LD Graph Generator

A lightweight Pelican plugin that scans Markdown frontmatter across your content folders and automatically generates structured **JSON-LD metadata** for SEO, AI enrichment, and semantic indexing.

The plugin builds a global Schema.org graph (`graph.jsonld`) and optionally injects per-entity `<script type="application/ld+json">` tags into your rendered HTML pages.

---

## 🧭 Features

- 🔍 **Automatic JSON-LD generation** from Markdown frontmatter  
- 🧱 **Folder-based type inference** (e.g., `people/` → `Person`, `projects/` → `CreativeWork`)  
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

```
your-site/
├── content/
│   ├── people/
│   ├── projects/
│   ├── organizations/
│   ├── experience/
│   └── certifications/
├── mappings.json
├── pelicanconf.py
└── plugins/
    └── pelican-jsonld-graph-generator/
        ├── __init__.py
        ├── generator.py
        ├── utils.py
        └── README.md
```

---

## 🧩 Example `mappings.json`

```json
{
  "folders": {
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
