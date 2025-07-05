<div align="center">

# 📚 Modern Classical Mechanics

**An open, free, and ever-evolving set of notes and resources for learning and teaching classical mechanics.**

<br>
<strong>Author:</strong> Danny Caballero  
<strong>Contact:</strong> caball14@msu.edu  
<strong>Michigan State University</strong>

![Build](https://img.shields.io/badge/build-passing-brightgreen) ![License: CC BY-NC 4.0](https://img.shields.io/badge/license-CC--BY--NC%204.0-blue)

</div>

---

## 🌐 About & Webpage

**Modern Classical Mechanics** is an open-source, interactive, and reproducible book for PHY 321: Classical Mechanics 1 at Michigan State University, authored by Marcos D. Caballero.

- **Webpage:** [View the Book Online](https://dannycaballero.info/modern-classical-mechanics/)
- **GitHub Repo:** [github.com/dannycab/modern-classical-mechanics](https://github.com/dannycab/modern-classical-mechanics)
- **License:** CC BY-NC 4.0 (free for non-commercial use)
- **Contact:** caball14@msu.edu

All content is built from Jupyter notebooks and published automatically to the web. Contributions, issues, and pull requests are welcome!

---

## 🗂️ Project Structure (2025)

```
modern-classical-mechanics/
├── build.py              # Build script for PDF, DOCX, LaTeX, Markdown
├── build-web.py          # Build script for HTML website (docs/)
├── notebooks/            # Source Jupyter notebooks and images
│   ├── 01_notes.ipynb
│   ├── 02_notes.ipynb
│   ├── ...
│   └── images/
│       └── ...
├── static/
│   └── css/
│       └── book.css      # Custom CSS for the site
├── _build/
│   ├── html/             # HTML output (intermediate, not for deployment)
│   │   ├── images/
│   │   ├── css/
│   │   └── *.html
│   ├── pdf/              # PDF output
│   ├── docx/             # DOCX output
│   ├── latex/            # LaTeX output
│   └── md/               # Markdown output
│       └── images/
├── docs/                 # Final HTML website for GitHub Pages
│   ├── images/
│   ├── css/
│   └── *.html
└── .nojekyll             # Ensures GitHub Pages does not use Jekyll
```

---

## 🚀 Features

- **Notebook to HTML conversion** using `nbconvert` with custom template and CSS.
- **Admonition support:** Converts MyST/Markdown/nbconvert admonitions (e.g., `::: tip`, `!!! warning`, `{admonition} note`, and code-fence style) to HTML blocks.
- **Image handling:** Copies and renames images referenced in notebooks, including YouTube thumbnails (auto-fetched if referenced).
- **Multiple output formats:**
  - HTML (website, in `docs/`)
  - PDF (`_build/pdf/`)
  - DOCX (`_build/docx/`)
  - LaTeX (`_build/latex/`)
  - Markdown (`_build/md/`)
- **Automatic copying** of all outputs and assets to the `docs/` directory for GitHub Pages hosting.
- **Dark mode toggle** in the HTML output.

---

## 🏗️ How to Build Locally

1. **Clone the repo:**
   ```sh
   git clone https://github.com/dannycab/modern-classical-mechanics.git
   cd modern-classical-mechanics
   ```
2. **Set up Python environment:**
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Install Jupyter and Pandoc:**
   - Jupyter: `pip install jupyter nbconvert`
   - Pandoc: [Install from pandoc.org](https://pandoc.org/installing.html)
4. **Build all outputs:**
   ```sh
   python build.py --md --pdf --docx --latex
   python build-web.py
   ```
5. **View outputs:**
   - Website: `docs/index.html`
   - PDFs: `_build/pdf/`
   - DOCX: `_build/docx/`
   - LaTeX: `_build/latex/`
   - Markdown: `_build/md/`

---

## 🛠️ Admonition Syntax Supported

- `::: tip [Title]` ... `:::`
- `!!! warning [Title]` (with indented content)
- `{admonition} note [Title]` ... `{/admonition}`
- `{tip}` ... `{/tip}` (single-line)
- Code-fence style:
  
  ```
  ```{tip} Optional Title
  Content here
  ```
  ```

---

## 🖼️ Images & YouTube Handling

- All images referenced in notebooks are copied and renamed for uniqueness.
- YouTube thumbnails are auto-downloaded if referenced by video ID or thumbnail URL.

---

## 🤖 Automated Builds (CI/CD)

- GitHub Actions automatically build the book and website on every push.
- All assets (notebooks, images, outputs) are kept in sync.
- Want to help improve the workflow? [Open an issue](https://github.com/dannycab/modern-classical-mechanics/issues) or [send a pull request](https://github.com/dannycab/modern-classical-mechanics/pulls)!

---

## 📝 License

This book and all its content are licensed under [Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/).

- **You are free to:** Share, adapt, and remix for non-commercial purposes, with attribution.
- **You may not:** Use for commercial purposes without permission.

See [LICENSE](LICENSE) for details.

---

## 💡 Contributing

**Everyone is welcome!**

- Found a typo? Have a suggestion? [Open an issue](https://github.com/dannycab/modern-classical-mechanics/issues)!
- Want to add a new example, fix a bug, or improve the build? [Send a pull request](https://github.com/dannycab/modern-classical-mechanics/pulls)!
- New to open source? Check out our [contributing guide](CONTRIBUTING.md) (coming soon) or just ask a question in the issues.

Let's make physics education better, together! 🚀

---

<div align="center">

*Made with 🧑‍🔬, ☕, and a love for teaching physics.*

</div>
