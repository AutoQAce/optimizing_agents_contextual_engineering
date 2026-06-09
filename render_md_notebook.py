"""
Reads context_engineering.md, converts image references to base64-embedded
inline images, and inserts the content as a markdown cell at position 1
(right after the title cell) in the notebook.
"""

import base64, re, json
from pathlib import Path

NOTEBOOK = Path(__file__).parent / "optimizing_agents_contextual_engineering.ipynb"
MD_FILE  = Path(__file__).parent / "context_engineering.md"
IMG_DIR  = Path(__file__).parent / "images"


def image_to_base64_html(match: re.Match) -> str:
    """Replace ![alt](path) with inline <img> using base64 data URI."""
    alt_text = match.group(1)
    img_path = IMG_DIR.parent / match.group(2)  # relative to .md location
    if not img_path.exists():
        return match.group(0)  # leave as-is if file not found

    suffix = img_path.suffix.lstrip(".").lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "gif": "image/gif", "webp": "image/webp"}.get(suffix, "image/png")

    b64 = base64.b64encode(img_path.read_bytes()).decode()
    return f'<img src="data:{mime};base64,{b64}" alt="{alt_text}" style="max-width:100%;">'


def convert_github_alerts(md: str) -> str:
    """Convert > [!TYPE] alert blocks to bold-styled HTML that Jupyter renders."""
    alert_styles = {
        "NOTE":      ("ℹ️", "#1f6feb", "#1a2332"),
        "TIP":       ("💡", "#238636", "#1a2e1a"),
        "IMPORTANT": ("❗", "#8957e5", "#2a1f3d"),
        "WARNING":   ("⚠️", "#d29922", "#2e2a1a"),
        "CAUTION":   ("🔴", "#da3633", "#2e1a1a"),
    }

    def replace_alert(m: re.Match) -> str:
        alert_type = m.group(1).upper()
        body = m.group(2).strip()
        # Un-quote each continuation line
        body = re.sub(r"^>\s?", "", body, flags=re.MULTILINE).strip()
        emoji, border_color, bg_color = alert_styles.get(alert_type, ("", "#888", "#222"))
        return (
            f'\n<blockquote style="border-left:4px solid {border_color}; '
            f'background:{bg_color}; padding:12px 16px; margin:16px 0; border-radius:6px;">\n'
            f'<strong>{emoji} {alert_type}</strong><br/>\n'
            f'{body}\n'
            f'</blockquote>\n'
        )

    pattern = r">\s*\[!(\w+)\]\s*\n((?:>.*\n?)*)"
    return re.sub(pattern, replace_alert, md)


def main():
    md_content = MD_FILE.read_text(encoding="utf-8")

    # Convert image references to inline base64
    md_content = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", image_to_base64_html, md_content)

    # Convert GitHub-style alerts to styled HTML blockquotes
    md_content = convert_github_alerts(md_content)

    # Split into lines for the notebook cell source array
    lines = md_content.split("\n")
    source_lines = [line + "\n" for line in lines[:-1]]  # add \n to all but last
    if lines:
        source_lines.append(lines[-1])  # last line without trailing \n

    # Build the new markdown cell
    new_cell = {
        "cell_type": "markdown",
        "metadata": {},
        "source": source_lines
    }

    # Read existing notebook
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))

    # Remove any previously inserted render cell (idempotent)
    nb["cells"] = [c for c in nb["cells"]
                   if not (c.get("cell_type") == "markdown"
                           and any("Context Engineering: Managing What LLMs Pay Attention To" in s
                                   for s in c.get("source", [])))]

    # Insert as the second cell (after the title)
    nb["cells"].insert(1, new_cell)

    NOTEBOOK.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"[OK] Inserted rendered markdown cell into {NOTEBOOK.name}")
    print(f"   -> {len(source_lines)} lines, images embedded as base64")


if __name__ == "__main__":
    main()
