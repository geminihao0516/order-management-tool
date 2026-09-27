"""A4 雙欄 PDF 與逐頁 PNG 列印檔。"""

from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

import fitz


A4_WIDTH, A4_HEIGHT = fitz.paper_size('a4')
MARGIN = 36
COLUMN_WIDTH = (A4_WIDTH - 2 * MARGIN) / 2
FONT_SIZE = 10.5
LINE_HEIGHT = 14
CELL_PADDING = 5
CJK_FONT_NAME = 'china-t'
LATIN_FONT_NAME = 'helv'
CJK_FONT = fitz.Font(fontname=CJK_FONT_NAME)
LATIN_FONT = fitz.Font(fontname=LATIN_FONT_NAME)


def _font_for(character):
    return LATIN_FONT if ord(character) < 128 else CJK_FONT


def _cell_lines(order):
    lines = [f"{order['index']}　{order['item']}　{order['main_person']}"]
    target = str(order.get('target_person', '')).strip()
    wish = str(order.get('wish', '')).strip()
    if target and target not in ('—', '-'):
        lines.append(target)
    if wish:
        lines.append(wish)
    return lines


def _wrap_lines(lines):
    wrapped = []
    available_width = COLUMN_WIDTH - 2 * CELL_PADDING
    for line in lines:
        current = ''
        current_width = 0
        for character in line:
            character_width = _font_for(character).text_length(character, fontsize=FONT_SIZE)
            if current and current_width + character_width > available_width:
                wrapped.append(current)
                current = ''
                current_width = 0
            current += character
            current_width += character_width
        wrapped.append(current)
    return wrapped


def _draw_cell(page, x, y, lines):
    for index, line in enumerate(lines):
        baseline = y + CELL_PADDING + FONT_SIZE + index * LINE_HEIGHT
        cursor = x + CELL_PADDING
        run = ''
        run_font = None
        for character in line:
            font = _font_for(character)
            if run and font is not run_font:
                font_name = LATIN_FONT_NAME if run_font is LATIN_FONT else CJK_FONT_NAME
                page.insert_text((cursor, baseline), run, fontname=font_name, fontsize=FONT_SIZE)
                cursor += run_font.text_length(run, fontsize=FONT_SIZE)
                run = ''
            run += character
            run_font = font
        if run:
            font_name = LATIN_FONT_NAME if run_font is LATIN_FONT else CJK_FONT_NAME
            page.insert_text((cursor, baseline), run, fontname=font_name, fontsize=FONT_SIZE)


def _draw_row_border(page, y, row_height):
    left = MARGIN
    middle = MARGIN + COLUMN_WIDTH
    right = A4_WIDTH - MARGIN
    for x in (left, middle, right):
        page.draw_line((x, y), (x, y + row_height), color=(0, 0, 0), width=0.8)
    page.draw_line((left, y + row_height), (right, y + row_height), color=(0, 0, 0), width=0.8)


def build_printable_pdf(expanded_orders):
    """回傳 A4 雙欄、每格一支蠟燭的可列印 PDF bytes。"""
    with fitz.open() as document:
        page = document.new_page(width=A4_WIDTH, height=A4_HEIGHT)
        y = MARGIN
        page.draw_line(
            (MARGIN, y), (A4_WIDTH - MARGIN, y), color=(0, 0, 0), width=0.8
        )
        for offset in range(0, len(expanded_orders), 2):
            left_lines = _wrap_lines(_cell_lines(expanded_orders[offset]))
            right_lines = (
                _wrap_lines(_cell_lines(expanded_orders[offset + 1]))
                if offset + 1 < len(expanded_orders) else []
            )
            row_height = max(len(left_lines), len(right_lines)) * LINE_HEIGHT + 2 * CELL_PADDING
            if row_height > A4_HEIGHT - 2 * MARGIN:
                raise ValueError('單筆願望太長，無法排入一張 A4 紙')
            if y + row_height > A4_HEIGHT - MARGIN:
                page = document.new_page(width=A4_WIDTH, height=A4_HEIGHT)
                y = MARGIN
                page.draw_line(
                    (MARGIN, y), (A4_WIDTH - MARGIN, y), color=(0, 0, 0), width=0.8
                )
            _draw_cell(page, MARGIN, y, left_lines)
            _draw_cell(page, MARGIN + COLUMN_WIDTH, y, right_lines)
            _draw_row_border(page, y, row_height)
            y += row_height
        return document.tobytes(garbage=4, deflate=True)


def build_a4_png_zip(pdf_bytes, dpi=300):
    """將 PDF 每一頁轉成 A4 PNG，回傳 ZIP bytes。"""
    output = BytesIO()
    with fitz.open(stream=pdf_bytes, filetype='pdf') as document:
        with ZipFile(output, 'w', compression=ZIP_DEFLATED) as archive:
            for index, page in enumerate(document, start=1):
                pixmap = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72), alpha=False)
                archive.writestr(f'A4_第{index:02d}頁.png', pixmap.tobytes('png'))
    return output.getvalue()
