import re
import html

from reportlab.platypus import (
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)

from reportlab.lib import colors
from reportlab.lib.units import inch

from src.pdf.styles import (
    REPORT_STYLES,
    PRIMARY,
    PRIMARY_DARK,
    SUCCESS,
    BORDER,
    CARD_BG,
)


# ===========================================================
# CONSTANTS
# ===========================================================

# Keep these deliberately conservative.
# ReportLab Tables cannot split INSIDE a cell.
MAX_CARD_CHARS = 500
MAX_TABLE_CELL_CHARS = 300
MAX_TEXT_CHUNK_CHARS = 500


# ===========================================================
# SPACING
# ===========================================================

def space(height=12):
    return Spacer(1, height)


# ===========================================================
# SAFE TEXT
# ===========================================================

def safe_text(value):
    """
    Convert arbitrary AI-generated content into safe ReportLab text.

    AI output may contain:
        **bold**
        *italic*
        `code`
        ```code```
        <para>
        <font>
        HTML
        Markdown
        malformed tags

    ReportLab Paragraph is NOT a Markdown parser.
    """

    if value is None:
        return ""

    text = str(value)

    # -------------------------------------------------------
    # Normalize line endings
    # -------------------------------------------------------

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # -------------------------------------------------------
    # Escape ALL HTML first
    # -------------------------------------------------------

    text = html.escape(
        text,
        quote=False,
    )

    # -------------------------------------------------------
    # Remove fenced markdown code markers
    # -------------------------------------------------------

    text = text.replace("```", "")

    # -------------------------------------------------------
    # Markdown headings
    # -------------------------------------------------------

    text = re.sub(
        r"(?m)^\s*#{1,6}\s+",
        "",
        text,
    )

    # -------------------------------------------------------
    # Markdown bold
    # -------------------------------------------------------

    text = re.sub(
        r"\*\*(.+?)\*\*",
        r"<b>\1</b>",
        text,
        flags=re.DOTALL,
    )

    text = re.sub(
        r"__(.+?)__",
        r"<b>\1</b>",
        text,
        flags=re.DOTALL,
    )

    # -------------------------------------------------------
    # Markdown italic
    # -------------------------------------------------------

    text = re.sub(
        r"(?<!\*)\*([^*\n]+)\*(?!\*)",
        r"<i>\1</i>",
        text,
    )

    # -------------------------------------------------------
    # Inline code
    # -------------------------------------------------------

    text = re.sub(
        r"`([^`\n]+)`",
        r"<font name='Courier'>\1</font>",
        text,
    )

    # -------------------------------------------------------
    # Markdown bullets
    # -------------------------------------------------------

    text = re.sub(
        r"(?m)^\s*[-*+]\s+",
        "• ",
        text,
    )

    # -------------------------------------------------------
    # Markdown numbered lists
    # -------------------------------------------------------

    text = re.sub(
        r"(?m)^\s*(\d+)\.\s+",
        r"\1. ",
        text,
    )

    # -------------------------------------------------------
    # Remove dangerous ReportLab tags that may have come
    # from AI-generated content.
    # -------------------------------------------------------

    text = re.sub(
        r"</?para\b[^>]*>",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Remove all font tags from AI input.
    # We add our own font tags only when necessary.
    text = re.sub(
        r"</?font\b[^>]*>",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # -------------------------------------------------------
    # Remove unsupported HTML tags.
    #
    # Only these are allowed.
    # -------------------------------------------------------

    allowed_tags = {
        "b",
        "i",
        "u",
        "br",
    }

    def clean_tag(match):

        tag = match.group(0)

        name_match = re.match(
            r"<\s*/?\s*([a-zA-Z0-9]+)",
            tag,
        )

        if not name_match:
            return ""

        tag_name = (
            name_match.group(1)
            .lower()
        )

        if tag_name in allowed_tags:
            return tag

        return ""

    text = re.sub(
        r"<[^>]+>",
        clean_tag,
        text,
    )

    # -------------------------------------------------------
    # Remove control characters.
    # -------------------------------------------------------

    text = re.sub(
        r"[\x00-\x08\x0b\x0c\x0e-\x1f]",
        "",
        text,
    )

    # -------------------------------------------------------
    # Normalize whitespace.
    # -------------------------------------------------------

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()


# ===========================================================
# HARD TEXT CHUNKING
# ===========================================================

def hard_split(text, max_chars=MAX_TEXT_CHUNK_CHARS):
    """
    Guaranteed hard split.

    Unlike a word-based splitter, this function can NEVER return
    a chunk larger than max_chars.

    This is important because a single giant AI-generated token
    can otherwise create a ReportLab cell thousands of points high.
    """

    if not text:
        return [""]

    chunks = []

    start = 0

    while start < len(text):

        end = min(
            start + max_chars,
            len(text),
        )

        chunk = text[start:end]

        # Prefer breaking at whitespace.
        if end < len(text):

            last_space = max(
                chunk.rfind(" "),
                chunk.rfind("\n"),
            )

            if last_space > max_chars * 0.55:
                end = start + last_space
                chunk = text[start:end]

        chunk = chunk.strip()

        if chunk:
            chunks.append(chunk)

        # Guaranteed forward progress.
        start = max(
            end,
            start + 1,
        )

    return chunks or [""]


# ===========================================================
# SPLIT LONG TEXT
# ===========================================================

def split_long_text(
    text,
    max_chars=MAX_TEXT_CHUNK_CHARS,
):
    """
    Split arbitrary text into guaranteed-safe chunks.

    Every returned chunk is <= max_chars.

    This intentionally uses hard character limits because
    ReportLab Table cells cannot split vertically.
    """

    if text is None:
        return [""]

    text = safe_text(text)

    if not text:
        return [""]

    # If already small.
    if len(text) <= max_chars:
        return [text]

    chunks = []

    # First respect existing line breaks.
    paragraphs = re.split(
        r"\n+",
        text,
    )

    current = ""

    for paragraph in paragraphs:

        paragraph = paragraph.strip()

        if not paragraph:
            continue

        # ---------------------------------------------------
        # If one paragraph is already too large, hard split it.
        # ---------------------------------------------------

        if len(paragraph) > max_chars:

            # Flush existing content.
            if current:
                chunks.extend(
                    hard_split(
                        current,
                        max_chars,
                    )
                )
                current = ""

            chunks.extend(
                hard_split(
                    paragraph,
                    max_chars,
                )
            )

            continue

        # ---------------------------------------------------
        # Add paragraph to current chunk.
        # ---------------------------------------------------

        candidate = (
            f"{current}\n{paragraph}"
            if current
            else paragraph
        )

        if len(candidate) <= max_chars:

            current = candidate

        else:

            if current:
                chunks.append(
                    current.strip()
                )

            current = paragraph

    if current:
        chunks.append(
            current.strip()
        )

    # Final safety pass.
    final_chunks = []

    for chunk in chunks:

        if len(chunk) <= max_chars:
            final_chunks.append(chunk)

        else:
            final_chunks.extend(
                hard_split(
                    chunk,
                    max_chars,
                )
            )

    return final_chunks or [""]


# ===========================================================
# TABLE CELL SAFETY
# ===========================================================

def split_table_cell(value):

    if value is None:
        return ""

    text = safe_text(value)

    if not text:
        return ""

    chunks = split_long_text(
        text,
        MAX_TABLE_CELL_CHARS,
    )

    # Use explicit breaks inside the cell.
    return "<br/>".join(chunks)


# ===========================================================
# TYPOGRAPHY
# ===========================================================

def title(text):

    return Paragraph(
        safe_text(text),
        REPORT_STYLES["cover_title"],
    )


def section_title(text):

    return Paragraph(
        safe_text(text),
        REPORT_STYLES["section_title"],
    )


def subsection(text):

    return Paragraph(
        safe_text(text),
        REPORT_STYLES["subsection_title"],
    )


def body(text):

    return Paragraph(
        safe_text(text),
        REPORT_STYLES["body"],
    )


def muted(text):

    return Paragraph(
        safe_text(text),
        REPORT_STYLES["muted"],
    )


def bullet(text):

    return Paragraph(
        f"• {safe_text(text)}",
        REPORT_STYLES["bullet"],
    )


def code(text):

    safe = safe_text(text)

    return Paragraph(
        f"<font name='Courier'>{safe}</font>",
        REPORT_STYLES["code"],
    )


# ===========================================================
# DIVIDER
# ===========================================================

def divider():

    table = Table(
        [[""]],
        colWidths=[7.2 * inch],
        rowHeights=[2],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    PRIMARY,
                ),
            ]
        )
    )

    return table


# ===========================================================
# SECTION HEADER
# ===========================================================

def create_section_title(text):

    return KeepTogether(
        [
            divider(),
            space(10),
            section_title(text),
            space(4),
        ]
    )


# ===========================================================
# PREMIUM CARD
# ===========================================================

def create_card(
    heading,
    content,
):
    """
    Safe card renderer.

    CRITICAL:
    The card body is divided into MANY table rows.

    ReportLab can split a Table between rows.

    It cannot split a Table cell.

    Therefore we NEVER put the entire AI-generated response
    inside one table cell.
    """

    heading_text = safe_text(heading)

    content_text = (
        ""
        if content is None
        else str(content)
    )

    # -------------------------------------------------------
    # Normalize <br> variants.
    # -------------------------------------------------------

    content_text = re.sub(
        r"<br\s*/?>",
        "\n",
        content_text,
        flags=re.IGNORECASE,
    )

    # Handle escaped breaks.
    content_text = content_text.replace(
        "&lt;br/&gt;",
        "\n",
    )

    # -------------------------------------------------------
    # Split body aggressively.
    # -------------------------------------------------------

    chunks = split_long_text(
        content_text,
        MAX_CARD_CHARS,
    )

    # -------------------------------------------------------
    # Build rows.
    # -------------------------------------------------------

    rows = [
        [
            Paragraph(
                heading_text,
                REPORT_STYLES["card_title"],
            )
        ]
    ]

    for chunk in chunks:

        safe_chunk = safe_text(chunk)

        # Newlines become ReportLab breaks.
        safe_chunk = safe_chunk.replace(
            "\n",
            "<br/>",
        )

        # Extra final protection.
        if len(safe_chunk) > MAX_CARD_CHARS * 2:

            safe_parts = hard_split(
                safe_chunk,
                MAX_CARD_CHARS,
            )

            for part in safe_parts:

                rows.append(
                    [
                        Paragraph(
                            part,
                            REPORT_STYLES["body"],
                        )
                    ]
                )

        else:

            rows.append(
                [
                    Paragraph(
                        safe_chunk,
                        REPORT_STYLES["body"],
                    )
                ]
            )

    # -------------------------------------------------------
    # IMPORTANT:
    #
    # Do NOT use KeepTogether around this Table.
    #
    # The table itself must be allowed to split across pages.
    # -------------------------------------------------------

    table = Table(
        rows,
        colWidths=[7.0 * inch],
        repeatRows=1,
        splitByRow=1,
        hAlign="LEFT",
    )

    n_rows = len(rows)

    style_cmds = [

        (
            "BACKGROUND",
            (0, 0),
            (-1, -1),
            CARD_BG,
        ),

        (
            "BOX",
            (0, 0),
            (-1, -1),
            0.5,
            BORDER,
        ),

        (
            "LEFTPADDING",
            (0, 0),
            (-1, -1),
            16,
        ),

        (
            "RIGHTPADDING",
            (0, 0),
            (-1, -1),
            16,
        ),

        (
            "TOPPADDING",
            (0, 0),
            (-1, -1),
            4,
        ),

        (
            "BOTTOMPADDING",
            (0, 0),
            (-1, -1),
            4,
        ),

        # Card heading padding.
        (
            "TOPPADDING",
            (0, 0),
            (0, 0),
            14,
        ),

        # Last row padding.
        (
            "BOTTOMPADDING",
            (0, n_rows - 1),
            (0, n_rows - 1),
            14,
        ),

        (
            "VALIGN",
            (0, 0),
            (-1, -1),
            "TOP",
        ),
    ]

    table.setStyle(
        TableStyle(style_cmds)
    )

    return table


# ===========================================================
# KPI CARD
# ===========================================================

def create_metric_card(
    title_text,
    value,
):

    safe_title = safe_text(
        title_text
    )

    safe_value = safe_text(
        value
    )

    table = Table(
        [
            [
                Paragraph(
                    safe_title,
                    REPORT_STYLES["card_title"],
                )
            ],
            [
                Paragraph(
                    safe_value,
                    REPORT_STYLES["metric_value"],
                )
            ],
        ],
        colWidths=[2.2 * inch],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.white,
                ),

                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    BORDER,
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    18,
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    18,
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    14,
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    14,
                ),

                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER",
                ),
            ]
        )
    )

    return table


# ===========================================================
# KPI DASHBOARD
# ===========================================================

def create_metric_dashboard(cards):

    return Table(
        [cards],
        colWidths=[
            2.3 * inch
            for _ in cards
        ],
        style=TableStyle(
            [
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                )
            ]
        ),
    )


# ===========================================================
# TAG
# ===========================================================

def create_tag(text):

    safe = safe_text(text)

    table = Table(
        [
            [
                Paragraph(
                    f"<b>{safe}</b>",
                    REPORT_STYLES["muted"],
                )
            ]
        ]
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor("#DBEAFE"),
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, -1),
                    PRIMARY,
                ),

                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    PRIMARY,
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
            ]
        )
    )

    return table


# ===========================================================
# TAG GRID
# ===========================================================

def create_tag_grid(
    items,
    columns=4,
):

    if not items:
        return Table([[""]])

    rows = []
    row = []

    for item in items:

        row.append(
            create_tag(item)
        )

        if len(row) == columns:

            rows.append(row)
            row = []

    if row:

        while len(row) < columns:
            row.append("")

        rows.append(row)

    return Table(
        rows,
        colWidths=[
            1.7 * inch
            for _ in range(columns)
        ],
    )


# ===========================================================
# PROGRESS BAR
# ===========================================================

def create_progress(score):

    try:
        score = float(score)

    except (
        TypeError,
        ValueError,
    ):

        score = 0

    score = max(
        0,
        min(score, 100),
    )

    width = 6.2 * inch

    # Ensure both columns have a positive width.
    minimum_width = 0.01 * inch

    filled = max(
        minimum_width,
        width * score / 100,
    )

    remaining = max(
        minimum_width,
        width - filled,
    )

    return Table(
        [["", ""]],
        colWidths=[
            filled,
            remaining,
        ],
        rowHeights=[12],
        style=TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, 0),
                    SUCCESS,
                ),

                (
                    "BACKGROUND",
                    (1, 0),
                    (1, 0),
                    BORDER,
                ),

                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.3,
                    BORDER,
                ),
            ]
        ),
    )


# ===========================================================
# PREMIUM TABLE
# ===========================================================

def create_table(
    headers,
    rows,
):
    """
    Safe ReportLab table.

    Long cells are split into explicit <br/> chunks.
    Tables are allowed to split between rows.
    """

    if not headers:
        return Table([[""]])

    # -------------------------------------------------------
    # Headers
    # -------------------------------------------------------

    safe_headers = [
        safe_text(header)
        for header in headers
    ]

    header_row = [
        Paragraph(
            header,
            REPORT_STYLES["body"],
        )
        for header in safe_headers
    ]

    # -------------------------------------------------------
    # Body rows
    # -------------------------------------------------------

    safe_rows = []

    for row in rows or []:

        safe_row = []

        for value in row:

            text = split_table_cell(
                value
            )

            safe_row.append(
                Paragraph(
                    text,
                    REPORT_STYLES["body"],
                )
            )

        # Ensure row has correct number of columns.
        while len(safe_row) < len(headers):

            safe_row.append(
                Paragraph(
                    "",
                    REPORT_STYLES["body"],
                )
            )

        if len(safe_row) > len(headers):

            safe_row = safe_row[
                :len(headers)
            ]

        safe_rows.append(
            safe_row
        )

    data = [
        header_row,
        *safe_rows,
    ]

    # -------------------------------------------------------
    # Column widths
    # -------------------------------------------------------

    column_count = len(headers)

    available_width = 7.0 * inch

    if column_count <= 3:

        width = (
            available_width
            / column_count
        )

        col_widths = [
            width
            for _ in range(column_count)
        ]

    elif column_count == 4:

        col_widths = [
            1.35 * inch,
            1.45 * inch,
            1.55 * inch,
            2.65 * inch,
        ]

    elif column_count == 5:

        col_widths = [
            0.8 * inch,
            1.0 * inch,
            1.5 * inch,
            1.85 * inch,
            1.85 * inch,
        ]

    else:

        width = (
            available_width
            / column_count
        )

        col_widths = [
            width
            for _ in range(column_count)
        ]

    # -------------------------------------------------------
    # Table
    # -------------------------------------------------------

    table = Table(
        data,
        colWidths=col_widths,
        repeatRows=1,
        splitByRow=1,
        hAlign="LEFT",
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    PRIMARY_DARK,
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.25,
                    BORDER,
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    return table


# ===========================================================
# BACKWARD COMPATIBILITY ALIASES
# ===========================================================

section = create_section_title

subheading = subsection

metric_card = create_metric_card

progress = create_progress

simple_table = create_table

info_table = create_table

badge_grid = create_tag_grid
