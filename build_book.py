#!/usr/bin/env python3
"""
Python: Kezdőtől a Mesterfokig - Automatikus Könyv és PDF Generáló Script
Markdown forrásokból szintaxiskiemelt, számozott, borítóval ellátott nyomdakész PDF-et készít.
"""

import os
import subprocess
import glob
import base64
import io
import re
import html as html_lib
from datetime import datetime
import markdown
from pypdf import PdfReader, PdfWriter
from pygments.formatters import HtmlFormatter
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

PROJECT_DIR = "/home/alphaws/Dev/Projects/csharp-kezdotol-a-mesterig"
CHAPTERS_DIR = os.path.join(PROJECT_DIR, "fejezetek")
COVER_PATH = os.path.join(PROJECT_DIR, "cover", "cover_design_1.jpg")
OUTPUT_HTML = os.path.join(PROJECT_DIR, "konyv_teljes.html")
OUTPUT_PDF = os.path.join(PROJECT_DIR, "CSharp_Kezdotol_a_Mesterfokig.pdf")
RAW_PDF = OUTPUT_PDF + ".raw.pdf"
HEADER_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
HEADER_FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def get_cover_base64():
    if os.path.exists(COVER_PATH):
        with open(COVER_PATH, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            return f"data:image/jpeg;base64,{encoded}"
    return None


def _normalise(text: str) -> str:
    return " ".join(text.split()).casefold()


def header_title_matches(title: str, page_text: str) -> bool:
    """Matches headings even when PDF layout inserts a hyphenated line break."""
    compact_title = re.sub(r"[\s-]+", "", title.casefold())
    compact_page_text = re.sub(r"[\s-]+", "", page_text.casefold())
    return compact_title in compact_page_text


def _toc_label(anchor_body: str) -> str:
    plain = re.sub(r"<[^>]+>", "", anchor_body)
    return html_lib.unescape(plain).strip()


def build_toc_html(toc_html: str, page_numbers: dict[str, int] | None = None) -> str:
    """Adds fixed-width page numbers and dotted leaders to Markdown's TOC."""
    page_numbers = page_numbers or {}

    def replace_anchor(match: re.Match[str]) -> str:
        opening, body, closing = match.group(1), match.group(2), match.group(3)
        label = _toc_label(body)
        page = page_numbers.get(_normalise(label), 0)
        page_text = str(page) if page else "—"
        return (
            f'{opening}<span class="toc-label">{body}</span>'
            f'<span class="toc-leader"></span>'
            f'<span class="toc-page-number">{page_text}</span>{closing}'
        )

    return re.sub(
        r'(<a\s+href="#[^"]+">)(.*?)(</a>)',
        replace_anchor,
        toc_html,
        flags=re.DOTALL,
    )


def extract_toc_page_numbers(pdf_path: str, toc_html: str) -> dict[str, int]:
    """Finds heading pages in the rendered PDF, excluding the cover and TOC."""
    reader = PdfReader(pdf_path)
    page_texts = [page.extract_text() or "" for page in reader.pages]
    content_start = 0
    for index, text in enumerate(page_texts):
        if "mérnökinformatikus" in _normalise(text) or "mérnök-informatikus" in _normalise(text):
            content_start = index
            break

    entries = re.findall(r'<a\s+href="#[^"]+">(.*?)</a>', toc_html, flags=re.DOTALL)
    result: dict[str, int] = {}
    for body in entries:
        label = _toc_label(body)
        key = _normalise(label)
        for page_index in range(content_start, len(page_texts)):
            if header_title_matches(label, page_texts[page_index]):
                result[key] = page_index + 1
                break
    return result


def add_index_page_numbers(html_body: str, pdf_path: str) -> str:
    """Adds rendered PDF page references to the final index table."""
    reader = PdfReader(pdf_path)
    page_texts = [page.extract_text() or "" for page in reader.pages]
    marker = '<h1 id="targymutato">'
    if marker not in html_body:
        return html_body
    before, index_body = html_body.split(marker, 1)
    table_match = re.search(r"<table>(.*?)</table>", index_body, flags=re.DOTALL)
    if not table_match:
        return html_body

    def replace_row(match: re.Match[str]) -> str:
        row = match.group(0)
        cells = re.findall(r"<td>(.*?)</td>", row, flags=re.DOTALL)
        if len(cells) != 2:
            return row
        term = html_lib.unescape(re.sub(r"<[^>]+>", "", cells[0])).strip()
        # A több szinonimát tartalmazó indexcím első fogalma legyen a keresési kulcs.
        needle = _normalise(term.split(",", 1)[0]).replace("`", "")
        pages = [
            str(index + 1)
            for index, text in enumerate(page_texts)
            if index > 1
            and "tárgymutató" not in _normalise(text)
            and needle
            and needle in _normalise(text).replace("`", "")
        ]
        page_label = ", ".join(pages) if pages else "—"
        return row.replace(cells[1], f"{cells[1]}<br><small>oldalak: {page_label}</small>")

    table = table_match.group(0)
    numbered_table = re.sub(r"<tr>.*?</tr>", replace_row, table, flags=re.DOTALL)
    index_body = index_body.replace(table, numbered_table, 1)
    return before + marker + index_body


def render_pdf(html_path: str, raw_pdf_path: str) -> None:
    cmd = [
        "google-chrome-stable",
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--no-pdf-header-footer",
        f"--print-to-pdf={raw_pdf_path}",
        html_path,
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)


def get_chapter_titles(chapter_files: list[str]) -> list[str]:
    titles = []
    for fpath in chapter_files:
        with open(fpath, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("# "):
                    titles.append(line[2:].strip())
                    break
    return titles


def fit_header_font_size(text: str, font_name: str, max_width: float) -> float:
    """Shrinks the complete chapter title instead of truncating it."""
    font_size = 8.5
    while font_size > 6.0 and pdfmetrics.stringWidth(text, font_name, font_size) > max_width:
        font_size -= 0.25
    return font_size


def add_running_headers(input_pdf: str, output_pdf: str, chapter_files: list[str]) -> None:
    """Adds book/chapter headers and a timestamp only to the final page."""
    pdfmetrics.registerFont(TTFont("BookHeader", HEADER_FONT))
    pdfmetrics.registerFont(TTFont("BookHeaderBold", HEADER_FONT_BOLD))
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    titles = get_chapter_titles(chapter_files)
    current_title = "Tartalomjegyzék"
    content_started = False
    timestamp = datetime.now().strftime("%Y. %m. %d. %H:%M")

    for page_number, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        normalised_text = _normalise(text)
        if "mérnökinformatikus" in normalised_text or "mérnök-informatikus" in normalised_text:
            content_started = True
        if content_started:
            for title in titles:
                if header_title_matches(title, text):
                    current_title = title
                    break

        if page_number > 0:
            width = float(page.mediabox.width)
            height = float(page.mediabox.height)
            overlay_buffer = io.BytesIO()
            canvas = Canvas(overlay_buffer, pagesize=(width, height))
            canvas.setFillColor(HexColor("#64748b"))
            header_font_size = fit_header_font_size(
                current_title,
                "BookHeader",
                width - 102,
            )
            canvas.setFont("BookHeader", header_font_size)
            canvas.drawCentredString(width / 2, height - 24, current_title)
            if page_number == len(reader.pages) - 1:
                canvas.setFont("BookHeader", 7.5)
                canvas.drawRightString(width - 51, 24, f"Generálva: {timestamp}")
            canvas.setStrokeColor(HexColor("#cbd5e1"))
            canvas.setLineWidth(0.5)
            canvas.line(51, height - 34, width - 51, height - 34)
            canvas.save()
            overlay_buffer.seek(0)
            overlay_page = PdfReader(overlay_buffer).pages[0]
            writer.add_page(page)
            writer.pages[-1].merge_page(overlay_page)
        else:
            writer.add_page(page)

    with open(output_pdf, "wb") as f:
        writer.write(f)

def build_book():
    print("[1/4] Markdown fejezetek összegyűjtése...")
    chapter_files = sorted(glob.glob(os.path.join(CHAPTERS_DIR, "*.md")))
    if not chapter_files:
        print("Hiba: Nem találhatók .md fejezetek a fejezetek mappában!")
        return

    md_content = []
    for fpath in chapter_files:
        print(f"  + Betöltés: {os.path.basename(fpath)}")
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read().strip()
            md_content.append(content)

    combined_md = "\n\n<div class=\"chapter-break\"></div>\n\n".join(md_content)

    print("[2/4] Markdown konvertálása HTML-re és Pygments szintaxiskiemelés generálása...")
    extensions = [
        'extra',
        'codehilite',
        'toc',
        'tables',
        'fenced_code'
    ]
    extension_configs = {
        'codehilite': {
            'linenums': False,
            'css_class': 'highlight',
            'guess_lang': False
        },
        'toc': {
            'toc_depth': '1-2'
        }
    }

    md = markdown.Markdown(
        extensions=extensions,
        extension_configs=extension_configs,
    )
    html_body = md.convert(combined_md)
    toc_html = md.toc
    book_toc_html = build_toc_html(toc_html)

    pygments_css = HtmlFormatter(style='friendly').get_style_defs('.highlight')
    cover_data_url = get_cover_base64()

    cover_html = ""
    if cover_data_url:
        cover_html = f"""
        <div class="cover-page">
            <img src="{cover_data_url}" alt="Borító" class="cover-img" />
        </div>
        """

    toc_page_html = f"""
    <section class="toc-page">
        <h1>Tartalomjegyzék</h1>
        {book_toc_html}
    </section>
    """

    full_html = f"""<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <title>Python: Kezdőtől a Mesterfokig</title>
    <style>
        @page {{
            size: A4;
            margin: 20mm 18mm 22mm 18mm;
            @bottom-center {{
                content: counter(page);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 9pt;
                color: #666;
            }}
        }}

        @page:first {{
            margin: 0;
            @bottom-center {{ content: normal; }}
        }}

        body {{
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', Helvetica, Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.65;
            color: #1e293b;
            background-color: #ffffff;
            margin: 0;
            padding: 0;
        }}

        .cover-page {{
            width: 100vw;
            height: 100vh;
            margin: 0;
            padding: 0;
            page-break-after: always;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: #0c1527;
        }}

        .cover-img {{
            width: 100%;
            height: 100%;
            object-fit: contain;
        }}

        .page-break {{
            page-break-after: always;
            break-after: page;
        }}

        .toc-page {{
            break-before: page;
            break-after: page;
        }}

        .toc-page .toc {{
            font-size: 10.5pt;
            line-height: 1.35;
        }}

        .toc-page .toc ul {{
            list-style: none;
            padding-left: 0;
        }}

        .toc-page .toc ul ul {{
            padding-left: 22px;
        }}

        .toc-page .toc li {{
            margin-bottom: 5px;
            break-inside: avoid;
        }}

        .toc-page .toc a {{
            display: flex;
            width: 100%;
            color: #1e293b;
            text-decoration: none;
        }}

        .toc-page .toc .toc-label {{
            flex: 0 1 auto;
        }}

        .toc-page .toc .toc-leader {{
            flex: 1 1 auto;
            min-width: 12px;
            margin: 0 7px;
            border-bottom: 1px dotted #94a3b8;
            height: 1em;
        }}

        .toc-page .toc .toc-page-number {{
            flex: 0 0 28px;
            text-align: right;
            color: #475569;
        }}

        h1, h2, h3, h4 {{
            color: #0f172a;
            font-weight: 700;
            line-height: 1.3;
        }}

        h1 {{
            font-size: 24pt;
            border-bottom: 2px solid #3b82f6;
            padding-bottom: 8px;
            margin-top: 0;
            margin-bottom: 24px;
            break-before: avoid;
        }}

        .chapter-break {{
            break-before: page;
            height: 0;
        }}

        h2 {{
            font-size: 16pt;
            margin-top: 28px;
            margin-bottom: 14px;
            border-left: 4px solid #3b82f6;
            padding-left: 10px;
        }}

        h3 {{
            font-size: 13pt;
            margin-top: 20px;
            margin-bottom: 10px;
            color: #1e3a8a;
        }}

        p {{
            margin-bottom: 14px;
            text-align: justify;
        }}

        blockquote {{
            margin: 18px 0;
            padding: 12px 18px;
            background-color: #f1f5f9;
            border-left: 4px solid #f59e0b;
            font-style: italic;
            color: #334155;
            border-radius: 0 6px 6px 0;
        }}

        code {{
            font-family: 'DejaVu Sans Mono', 'Liberation Mono', 'Ubuntu Mono', 'Courier New', monospace;
            background-color: #f1f5f9;
            color: #0f172a;
            padding: 2px 5px;
            border-radius: 4px;
            font-size: 9.5pt;
        }}

        pre {{
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 12px 14px;
            overflow-x: hidden;
            white-space: pre-wrap;
            word-break: break-word;
            margin: 18px 0;
            font-size: 9pt;
            line-height: 1.45;
        }}

        pre code {{
            background-color: transparent;
            padding: 0;
            border-radius: 0;
            white-space: pre-wrap;
            word-break: break-word;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 10.5pt;
        }}

        th, td {{
            border: 1px solid #cbd5e1;
            padding: 6px 10px;
            text-align: left;
        }}

        th {{
            background-color: #f8fafc;
            font-weight: 600;
        }}

        ul, ol {{
            margin-top: 6px;
            margin-bottom: 16px;
            padding-left: 24px;
        }}

        li {{
            margin-bottom: 6px;
        }}

        hr {{
            border: 0;
            border-top: 1px solid #e2e8f0;
            margin: 28px 0;
        }}

        /* Pygments Syntax Styling */
        {pygments_css}
    </style>
</head>
<body>
    {cover_html}
    {toc_page_html}
    <div class="content">
        {html_body}
    </div>
</body>
</html>
"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"  -> HTML összeállítva: {OUTPUT_HTML}")

    try:
        print("[3/4] PDF renderelése Google Chrome Headless motorral...")
        render_pdf(OUTPUT_HTML, RAW_PDF)
        page_numbers = extract_toc_page_numbers(RAW_PDF, toc_html)
        numbered_toc_html = build_toc_html(toc_html, page_numbers)
        numbered_index_body = add_index_page_numbers(html_body, RAW_PDF)
        numbered_toc_page_html = f"""
    <section class="toc-page">
        <h1>Tartalomjegyzék</h1>
        {numbered_toc_html}
    </section>
    """
        full_html = full_html.replace(html_body, numbered_index_body, 1)
        full_html = full_html.replace(
            f"""    <section class="toc-page">
        <h1>Tartalomjegyzék</h1>
        {book_toc_html}
    </section>
    """,
            numbered_toc_page_html,
        )
        with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
            f.write(full_html)
        render_pdf(OUTPUT_HTML, RAW_PDF)
        add_running_headers(RAW_PDF, OUTPUT_PDF, chapter_files)
        os.remove(RAW_PDF)
        print(f"[4/4] SIKER! A könyv PDF sikeresen előállt:")
        print(f"  -> {OUTPUT_PDF}")
    except subprocess.CalledProcessError as e:
        print(f"Hiba történt a PDF generálása közben: {e.stderr.decode()}")

if __name__ == "__main__":
    build_book()
