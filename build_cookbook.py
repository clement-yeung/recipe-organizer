#!/usr/bin/env python3
"""Merge recipe Markdown files and export one styled cookbook PDF."""

from pathlib import Path
import html
import re
import subprocess
import sys
import venv


ROOT = Path(__file__).resolve().parent
DISHES = ROOT / "dishes"
SUPPORT = ROOT / "_support"
EXPORT = ROOT / "export"

TITLE = "我的日常食譜本"


CSS = """
@page {
    size: A4;
    margin: 20mm 18mm 20mm;
}

* {
    box-sizing: border-box;
}

html,
body {
    margin: 0;
    padding: 0;
}

body {
    font-family:
        "PingFang TC",
        "Microsoft JhengHei",
        "Noto Sans CJK TC",
        sans-serif;
    font-size: 10.5pt;
    line-height: 1.48;
    color: #000000;
}

/*
 * PDF page margins define the content area.
 * The frame extends outward from that area into the page margins.
 *
 * A4 margins: top/bottom 20mm, left/right 18mm.
 * Frame offsets: top/bottom -12mm, left/right -10mm.
 * Result: frame approximately 8mm from the paper edges.
 */
.page-frame {
    position: fixed;
    top: -12mm;
    bottom: -12mm;
    left: -10mm;
    right: -10mm;
    border: 0.7pt solid #2457A7;
    pointer-events: none;
    z-index: 0;
}

.cover,
.recipe {
    position: relative;
    z-index: 1;
}

.cover {
    padding-top: 20mm;
}

.recipe {
    break-before: page;
}

h1,
h2,
h3,
h4,
h5,
h6,
p,
li,
strong {
    color: #000000;
}

h1 {
    font-size: 22pt;
    line-height: 1.25;
    margin: 0 0 12pt;
    padding: 0;
    border: none;
    break-after: avoid;
}

.cover h1 {
    font-size: 28pt;
    margin-bottom: 16pt;
}

h2 {
    font-size: 12pt;
    margin: 12pt 0 4pt;
    break-after: avoid;
}

h3,
h4,
h5,
h6 {
    margin: 10pt 0 4pt;
    break-after: avoid;
}

p {
    margin: 4pt 0;
    orphans: 2;
    widows: 2;
}

ul,
ol {
    margin: 4pt 0;
    padding-left: 1.6em;
}

li {
    margin: 3pt 0;
    break-inside: avoid;
}

a,
a:visited {
    color: #2457A7;
    text-decoration: none;
    overflow-wrap: anywhere;
}

.toc li {
    margin: 7pt 0;
}

.legend {
    margin-top: 18pt;
}

code {
    font-family: monospace;
}
"""


def render_inline(text):
    """Escape HTML and support links, bold, and inline code."""
    text = html.escape(text)

    # Temporarily protect generated links from other replacements.
    links = []

    def save_link(match):
        label = match.group(1)
        url = match.group(2)
        token = f"\x00LINK{len(links)}\x00"
        links.append(f'<a href="{url}">{label}</a>')
        return token

    text = re.sub(
        r"\[([^\]]+)\]\((https?://[^\s)]+)\)",
        save_link,
        text,
    )
    text = re.sub(
        r"\*\*(.+?)\*\*",
        r"<strong>\1</strong>",
        text,
    )
    text = re.sub(
        r"`([^`]+)`",
        r"<code>\1</code>",
        text,
    )

    for index, link in enumerate(links):
        text = text.replace(f"\x00LINK{index}\x00", link)

    return text


def render_markdown(markdown):
    """
    Small renderer for this cookbook's recipe template.

    Supports:
    - Headings
    - Paragraphs
    - Single-level ordered/unordered lists
    - Bold, inline code, and HTTP(S) links

    Does not support full Markdown, tables, images, nested lists,
    or fenced code blocks.
    """
    output = []
    paragraph = []
    active_list = None

    def flush_paragraph():
        if paragraph:
            text = render_inline(" ".join(paragraph))
            output.append(f"<p>{text}</p>")
            paragraph.clear()

    def close_list():
        nonlocal active_list
        if active_list:
            output.append(f"</{active_list}>")
            active_list = None

    for raw_line in markdown.splitlines():
        line = raw_line.strip()

        if not line:
            flush_paragraph()
            close_list()
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        item = re.match(r"^([-*]|\d+\.)\s+(.+)$", line)

        if heading:
            flush_paragraph()
            close_list()

            level = len(heading.group(1))
            text = render_inline(heading.group(2))
            output.append(f"<h{level}>{text}</h{level}>")

        elif item:
            flush_paragraph()

            kind = (
                "ul"
                if item.group(1) in ("-", "*")
                else "ol"
            )

            if active_list != kind:
                close_list()
                output.append(f"<{kind}>")
                active_list = kind

            text = render_inline(item.group(2))
            output.append(f"<li>{text}</li>")

        else:
            close_list()
            paragraph.append(line)

    flush_paragraph()
    close_list()

    return "\n".join(output)


def load_recipes():
    if not DISHES.is_dir():
        raise RuntimeError(
            f"找不到食譜資料夾：{DISHES}"
        )

    paths = sorted(
        (
            path
            for path in DISHES.rglob("*")
            if path.is_file()
            and path.suffix.lower() == ".md"
        ),
        key=lambda path: (
            path.relative_to(DISHES)
            .as_posix()
            .casefold()
        ),
    )

    recipes = []

    for path in paths:
        markdown = path.read_text(
            encoding="utf-8-sig"
        ).strip()

        if not markdown:
            continue

        heading = re.search(
            r"^#\s+(.+)$",
            markdown,
            re.MULTILINE,
        )

        title = (
            heading.group(1).strip()
            if heading
            else path.stem
        )

        if not heading:
            markdown = f"# {title}\n\n{markdown}"

        recipes.append(
            {
                "title": title,
                "markdown": markdown,
                "path": path,
            }
        )

    if not recipes:
        raise RuntimeError(
            "dishes/ 裡沒有非空白的 Markdown 食譜。"
        )

    return recipes


def write_merged_markdown(recipes):
    contents = "\n".join(
        f"{index}. {recipe['title']}"
        for index, recipe in enumerate(recipes, 1)
    )

    body = "\n\n---\n\n".join(
        recipe["markdown"]
        for recipe in recipes
    )

    merged = (
        f"# {TITLE}\n\n"
        f"## 目錄\n\n"
        f"{contents}\n\n"
        f"{body}\n"
    )

    path = EXPORT / "cookbook.md"
    path.write_text(merged, encoding="utf-8")
    return path


def write_html(recipes):
    contents = "\n".join(
        (
            f'<li><a href="#recipe-{index}">'
            f'{html.escape(recipe["title"])}'
            "</a></li>"
        )
        for index, recipe in enumerate(recipes, 1)
    )

    sections = "\n".join(
        (
            f'<section class="recipe" '
            f'id="recipe-{index}">\n'
            f'{render_markdown(recipe["markdown"])}\n'
            "</section>"
        )
        for index, recipe in enumerate(recipes, 1)
    )

    document = f"""<!doctype html>
<html lang="zh-Hant">
<head>
    <meta charset="utf-8">
    <title>{html.escape(TITLE)}</title>
    <style>{CSS}</style>
</head>
<body>
    <div class="page-frame" aria-hidden="true"></div>

    <section class="cover">
        <h1>{html.escape(TITLE)}</h1>
        <p>簡單、實用、持續更新的家常配方</p>

        <h2>目錄</h2>
        <ol class="toc">
            {contents}
        </ol>

        <p class="legend">
            🟢 大同電鍋　
            🟠 烤箱　
            🔵 爐台
        </p>
        <p>
            器具以文字與圓點符號區分；
            藍色頁框僅為裝飾。
        </p>
    </section>

    {sections}
</body>
</html>
"""

    path = EXPORT / "cookbook.html"
    path.write_text(document, encoding="utf-8")
    return path


def write_pdf(html_path):
    from playwright.sync_api import sync_playwright

    pdf_path = EXPORT / "cookbook.pdf"

    footer = """
    <div style="
        font-size: 9px;
        width: 100%;
        text-align: center;
        color: #000000;
    ">
        <span class="pageNumber"></span>
        /
        <span class="totalPages"></span>
    </div>
    """

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()

        try:
            page = browser.new_page()

            page.goto(
                html_path.resolve().as_uri(),
                wait_until="load",
            )

            page.evaluate("document.fonts.ready")

            page.pdf(
                path=str(pdf_path.resolve()),
                print_background=True,
                prefer_css_page_size=True,
                display_header_footer=True,
                header_template="<span></span>",
                footer_template=footer,
            )

        finally:
            browser.close()

    if not pdf_path.exists() or not pdf_path.stat().st_size:
        raise RuntimeError("PDF 未成功產生或檔案為空。")

    return pdf_path


def build(merge_only=False):
    recipes = load_recipes()
    EXPORT.mkdir(parents=True, exist_ok=True)

    markdown_path = write_merged_markdown(recipes)
    html_path = write_html(recipes)

    print(f"已合併 {len(recipes)} 道食譜。")
    print(f"Markdown：{markdown_path}")
    print(f"HTML：{html_path}")

    if not merge_only:
        pdf_path = write_pdf(html_path)
        print(f"PDF：{pdf_path}")


def run_with_pdf_environment():
    """
    Keep dependencies inside _support/.venv,
    then rerun this script using that environment.
    """
    SUPPORT.mkdir(parents=True, exist_ok=True)

    environment = SUPPORT / ".venv"

    if sys.platform == "win32":
        python = environment / "Scripts" / "python.exe"
    else:
        python = environment / "bin" / "python"

    if not python.exists():
        print(
            "首次設定：建立專用 Python 環境……",
            flush=True,
        )
        venv.EnvBuilder(
            with_pip=True
        ).create(environment)

    check = subprocess.run(
        [
            str(python),
            "-c",
            "import playwright.sync_api",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    if check.returncode:
        requirements = SUPPORT / "requirements.txt"

        if not requirements.exists():
            requirements.write_text(
                "playwright>=1.40,<2\n",
                encoding="utf-8",
            )

        subprocess.check_call(
            [
                str(python),
                "-m",
                "pip",
                "install",
                "-r",
                str(requirements),
            ]
        )

    # Install Chromium if needed; existing installations are reused.
    subprocess.check_call(
        [
            str(python),
            "-m",
            "playwright",
            "install",
            "chromium",
        ]
    )

    return subprocess.call(
        [
            str(python),
            str(Path(__file__).resolve()),
            "--render",
        ]
    )


def main():
    try:
        if "--merge-only" in sys.argv:
            build(merge_only=True)
            return 0

        if "--render" in sys.argv:
            build()
            return 0

        return run_with_pdf_environment()

    except Exception as error:
        print(
            f"\n建立食譜集失敗：{error}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())