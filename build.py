#!/usr/bin/env python3
"""
build.py - Python workflow for building PDFs and HTML from Jupyter notebooks and Jupyter Book.

- Reads notebooks.yaml for notebook list
- Calls update_toc.sh to sync _toc.yml
- Builds PDFs (only if needed) using nbconvert
- Builds full book PDF and HTML using Jupyter Book
- Copies/moves outputs to _build/latex and _build/html
- Gives clear output and errors

Usage:
    python build.py [--pdf] [--html]
    (default: both)
"""
import argparse
import subprocess
import sys
import os
import shutil
import yaml
from pathlib import Path

def run(cmd, **kwargs):
    print(f"[RUN] {' '.join(str(x) for x in cmd)}")
    result = subprocess.run(cmd, **kwargs)
    if result.returncode != 0:
        print(f"[ERROR] Command failed: {' '.join(str(x) for x in cmd)}", file=sys.stderr)
        sys.exit(result.returncode)

def parse_yaml_list(yaml_path):
    with open(yaml_path) as f:
        data = yaml.safe_load(f)
    # Expect a top-level list or dict with a key like 'notebooks'
    if isinstance(data, dict) and 'notebooks' in data:
        return [n for n in data['notebooks'] if n and not str(n).startswith('#')]
    elif isinstance(data, list):
        return [n for n in data if n and not str(n).startswith('#')]
    else:
        raise ValueError(f"Unexpected YAML structure in {yaml_path}")

def main():
    parser = argparse.ArgumentParser(description="Build PDFs, Markdown, DOCX, and HTML from Jupyter notebooks and Jupyter Book.")
    parser.add_argument('--pdf', action='store_true', help='Build PDFs only')
    parser.add_argument('--md', action='store_true', help='Build Markdown only')
    parser.add_argument('--docx', action='store_true', help='Build DOCX only')
    parser.add_argument('--latex', action='store_true', help='Build LaTeX only')
    parser.add_argument('--html', action='store_true', help='Build HTML only')
    args = parser.parse_args()

    # Directories
    repo_root = Path(__file__).parent.resolve()
    build_dir = repo_root / '_build'
    build_dir.mkdir(parents=True, exist_ok=True)  # Ensure _build exists
    chapters_dir = build_dir / 'latex'
    html_dir = build_dir / 'html'
    notebook_dir = repo_root / 'notebooks'
    notebooks_yaml = repo_root / 'notebooks.yaml'
    update_toc = repo_root / 'scripts' / 'update_toc.sh'

    import nbformat
    import requests
    import re
    import hashlib

    build_pdf = args.pdf or (not args.md and not args.docx and not args.latex and not args.html)
    build_md = args.md or (not args.pdf and not args.docx and not args.latex and not args.html)
    build_docx = args.docx or (not args.pdf and not args.md and not args.latex and not args.html)
    build_latex = args.latex or (not args.pdf and not args.md and not args.docx and not args.html)
    build_html = False  # HTML build disabled


    # Always generate _toc.yml from notebooks.yaml using Python (robust, no timestamp logic)
    toc_yml = repo_root / '_toc.yml'
    print(f"[INFO] Generating _toc.yml from {notebooks_yaml} using Python...")
    if not notebooks_yaml.exists():
        print(f"[ERROR] {notebooks_yaml} not found.", file=sys.stderr)
        sys.exit(1)
    notebooks = parse_yaml_list(notebooks_yaml)

    # --- Output build logic for LaTeX, PDF, DOCX, Markdown ---
    if build_latex:
        chapters_dir.mkdir(parents=True, exist_ok=True)
        print(f"[INFO] Building LaTeX files for notebooks in {notebook_dir} -> {chapters_dir}")
        for nb in notebooks:
            nb_path = notebook_dir / nb
            if not nb_path.exists():
                print(f"[WARN] Notebook not found: {nb_path}")
                continue
            tex_name = nb_path.with_suffix('.tex').name
            tex_path = chapters_dir / tex_name
            print(f"Converting {nb_path} to {tex_path}")
            run([
                'jupyter', 'nbconvert', '--to', 'latex', str(nb_path),
                '--output', tex_name, '--output-dir', str(chapters_dir)
            ])
        print(f"[INFO] All notebooks converted to LaTeX and saved in {chapters_dir}")

    if build_pdf:
        pdf_dir = build_dir / 'pdf'
        pdf_dir.mkdir(parents=True, exist_ok=True)
        print(f"[INFO] Building PDF files for notebooks in {notebook_dir} -> {pdf_dir}")
        for nb in notebooks:
            nb_path = notebook_dir / nb
            if not nb_path.exists():
                print(f"[WARN] Notebook not found: {nb_path}")
                continue
            pdf_name = nb_path.with_suffix('.pdf').name
            pdf_path = pdf_dir / pdf_name
            print(f"Converting {nb_path} to {pdf_path}")
            run([
                'jupyter', 'nbconvert', '--to', 'pdf', str(nb_path),
                '--output', pdf_name, '--output-dir', str(pdf_dir)
            ])
        print(f"[INFO] All notebooks converted to PDF and saved in {pdf_dir}")

    # DOCX is now always built from Markdown using Pandoc (see below)

    if build_md or build_docx:
        md_dir = build_dir / 'md'
        images_dir = md_dir / 'images'
        md_dir.mkdir(parents=True, exist_ok=True)
        images_dir.mkdir(parents=True, exist_ok=True)
        print(f"[INFO] Building Markdown files for notebooks in {notebook_dir} -> {md_dir}")
        for nb in notebooks:
            nb_path = notebook_dir / nb
            if not nb_path.exists():
                print(f"[WARN] Notebook not found: {nb_path}")
                continue
            md_name = nb_path.with_suffix('.md').name
            md_path = md_dir / md_name
            print(f"Converting {nb_path} to {md_path}")
            run([
                'jupyter', 'nbconvert', '--to', 'markdown', str(nb_path),
                '--output', md_name, '--output-dir', str(md_dir)
            ])
            # Post-process markdown to copy images and update paths
            with open(md_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            import re
            def copy_and_update(match):
                img_path = match.group(2)
                # Only process local images (not http/https)
                if img_path.startswith('http'):
                    return match.group(0)
                # Try to find the image in the notebook's folder or in the generated _build/md subfolders
                src_img = (nb_path.parent / img_path).resolve()
                if not src_img.exists():
                    # Try _build/md/<notebook_stem>_files/<img>
                    alt_img = md_dir / f"{nb_path.stem}_files" / os.path.basename(img_path)
                    if alt_img.exists():
                        src_img = alt_img
                    else:
                        print(f"[WARN] Image not found: {src_img}")
                        return match.group(0)
                flat_name = f"{nb_path.stem}_{os.path.basename(img_path)}"
                dst_img = images_dir / flat_name
                shutil.copy2(src_img, dst_img)
                return f"!{match.group(1)}(images/{flat_name})"
            # Update image links: ![alt](path)
            md_content_new = re.sub(r'(!\[[^\]]*\])\(([^)]+)\)', copy_and_update, md_content)
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content_new)
        print(f"[INFO] All notebooks converted to Markdown and images copied to {images_dir}")

    if build_docx:
        md_dir = build_dir / 'md'
        images_dir = md_dir / 'images'
        docx_dir = build_dir / 'docx'
        docx_dir.mkdir(parents=True, exist_ok=True)
        for nb in notebooks:
            md_name = Path(nb).with_suffix('.md').name
            md_path = md_dir / md_name
            docx_name = Path(nb).with_suffix('.docx').name
            docx_path = docx_dir / docx_name
            if not md_path.exists():
                print(f"[WARN] Markdown not found: {md_path}")
                continue
            print(f"Converting {md_path} to {docx_path} using pandoc with resource-path {md_dir}:{images_dir}")
            run([
                'pandoc', str(md_path), '-o', str(docx_path), '--resource-path', f"{md_dir}:{images_dir}"
            ], cwd=md_dir)
        print(f"[INFO] All markdown files converted to DOCX using pandoc and saved in {docx_dir}")

    # Always generate _toc.yml from notebooks.yaml using Python (robust, no timestamp logic)
    toc_yml = repo_root / '_toc.yml'
    print(f"[INFO] Generating _toc.yml from {notebooks_yaml} using Python...")
    if not notebooks_yaml.exists():
        print(f"[ERROR] {notebooks_yaml} not found.", file=sys.stderr)
        sys.exit(1)
    notebooks = parse_yaml_list(notebooks_yaml)
    toc_content = [
        "# Auto-generated _toc.yml from notebooks.yaml",
        "format: jb-book",
        "root: intro",
        "chapters:",
    ]
    for nb in notebooks:
        nb_path = Path(nb)
        toc_content.append(f"  - file: notebooks/{nb_path.stem}")
    # If intro.md does not exist, use the first notebook as root and the rest as chapters
    intro_md = repo_root / 'intro.md'
    if not intro_md.exists() and notebooks:
        toc_content = [
            "# Auto-generated _toc.yml from notebooks.yaml",
            "format: jb-book",
            f"root: notebooks/{Path(notebooks[0]).stem}",
            "chapters:",
        ]
        for nb in notebooks[1:]:
            nb_path = Path(nb)
            toc_content.append(f"  - file: notebooks/{nb_path.stem}")
    with open(toc_yml, 'w') as f:
        f.write('\n'.join(toc_content) + '\n')
    print(f"[INFO] _toc.yml generated with {len(notebooks)} chapters.")


    # Always fetch remote images and update references (Python implementation)
    print(f"[INFO] Fetching remote images and updating references in notebooks...")
    remote_image_pattern = re.compile(r'!\[[^\]]*\]\((https?://[^)]+)\)')
    for nb in notebooks:
        nb_path = notebook_dir / nb
        if not nb_path.exists():
            print(f"[WARN] Notebook not found: {nb_path}")
            continue
        try:
            nb_data = nbformat.read(str(nb_path), as_version=4)
        except Exception as e:
            print(f"[WARN] Could not read notebook {nb_path}: {e}")
            continue
        changed = False
        for cell in nb_data.cells:
            if cell.cell_type != 'markdown':
                continue
            def repl(match):
                url = match.group(1)
                # Create a flat, unique filename for the image
                hash_digest = hashlib.md5(url.encode('utf-8')).hexdigest()[:8]
                ext = os.path.splitext(url.split('?')[0])[1] or '.img'
                local_name = f"remote_{hash_digest}{ext}"
                local_path = nb_path.parent / local_name
                if not local_path.exists():
                    try:
                        resp = requests.get(url, timeout=10)
                        resp.raise_for_status()
                        with open(local_path, 'wb') as f:
                            f.write(resp.content)
                        print(f"[INFO] Downloaded {url} -> {local_path}")
                    except Exception as e:
                        print(f"[WARN] Failed to fetch {url}: {e}")
                        return match.group(0)
                else:
                    print(f"[INFO] Already downloaded {url} -> {local_path}")
                changed_local = match.group(0).replace(url, local_name)
                return changed_local
            new_src = remote_image_pattern.sub(repl, cell.source)
            if new_src != cell.source:
                cell.source = new_src
                changed = True
        if changed:
            try:
                nbformat.write(nb_data, str(nb_path))
                print(f"[INFO] Updated notebook with local images: {nb_path}")
            except Exception as e:
                print(f"[WARN] Could not write notebook {nb_path}: {e}")
    print(f"[INFO] Remote image fetch and update complete.")



    # HTML build disabled

    # Remove all folders in _build except latex, html, md, docx, pdf
    for f in build_dir.iterdir():
        if f.is_dir() and f.name not in {'latex', 'html', 'md', 'docx', 'pdf'}:
            try:
                shutil.rmtree(f)
                print(f"[INFO] Removed directory {f}")
            except Exception as e:
                print(f"[WARN] Could not remove directory {f}: {e}")
        elif f.is_file():
            try:
                f.unlink()
                print(f"[INFO] Removed {f}")
            except Exception as e:
                print(f"[WARN] Could not remove {f}: {e}")

if __name__ == '__main__':
    main()
