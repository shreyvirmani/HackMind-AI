import re
from xml.sax.saxutils import escape

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
# SAFE TEXT
# ===========================================================

def safe_text(text):
    """
    Safely convert arbitrary AI-generated text into content that
    ReportLab Paragraph can parse.

    AI-generated content may contain malformed HTML/XML such as:

        <font size="18"></para>

    or:

        <something>

    ReportLab treats Paragraph content as XML-like markup, so raw
    AI output must be escaped before being passed to Paragraph.
    """

    if text is None:
        return ""

    return escape(str(text))


# ===========================================================
# TEXT CHUNKING
# ===========================================================

def split_text_into_chunks(
    text,
    max_chars=900,
):
    """
    Split long AI-generated text into reasonably sized chunks.

    This is critical because ReportLab Tables can split BETWEEN
    rows but cannot recover when a single cell becomes taller than
    the available page.

    Example:

        5000-character AI response
                ↓
        900-character chunks
                ↓
        multiple table rows
                ↓
        ReportLab can flow them across pages
    """

    if text is None:
        return [""]

    text = str(text).strip()

    if not text:
        return [""]

    # Already small enough.
    if len(text) <= max_chars:
        return [text]

    words = text.split()

    chunks = []
    current = ""

    for word in words:

        # Extremely long individual word/URL.
        if len(word) > max_chars:

            if current:
                chunks.append(current)
                current = ""

            # Hard split the oversized word.
            for i in range(
                0,
                len(word),
                max_chars,
            ):
                chunks.append(
                    word[i:i + max_chars]
                )

            continue

        candidate = (
            word
            if not current
            else f"{current} {word}"
        )

        if len(candidate) <= max_chars:

            current = candidate

        else:

            if current:
                chunks.append(current)

            current = word

    if current:
        chunks.append(current)

    return chunks or [""]


# ===========================================================
# SPACING
# ===========================================================

def space(height=12):
    return Spacer(1, height)


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
    return Paragraph(
        f"<font name='Courier'>{safe_text(text)}</font>",
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
    Create a page-safe premium card.

    Important:

    ReportLab cannot split a single table cell if the cell itself
    becomes taller than the page.

    AI-generated project descriptions can easily become thousands
    of characters long.

    Therefore:

        AI content
            ↓
        split on <br/>
            ↓
        split long lines into chunks
            ↓
        one chunk per table row
            ↓
        table can safely flow across pages
    """

    content_str = (
        ""
        if content is None
        else str(content)
    )

    # -------------------------------------------------------
    # Split HTML-style line breaks.
    # -------------------------------------------------------

    lines = re.split(
        r"<br\s*/?>",
        content_str,
        flags=re.IGNORECASE,
    )

    # -------------------------------------------------------
    # Convert every line into safe chunks.
    # -------------------------------------------------------

    chunks = []

    for line in lines:

        line = line.strip()

        if not line:
            continue

        chunks.extend(
            split_text_into_chunks(
                line,
                max_chars=900,
            )
        )

    if not chunks:
        chunks = [""]

    # -------------------------------------------------------
    # Build rows.
    # -------------------------------------------------------

    rows = [
        [
            Paragraph(
                safe_text(heading),
                REPORT_STYLES["card_title"],
            )
        ]
    ]

    for chunk in chunks:

        rows.append(
            [
                Paragraph(
                    safe_text(chunk),
                    REPORT_STYLES["body"],
                )
            ]
        )

    # -------------------------------------------------------
    # Create table.
    # -------------------------------------------------------

    table = Table(
        rows,
        colWidths=[7.0 * inch],
        repeatRows=1,
        splitByRow=1,
    )

    # -------------------------------------------------------
    # Style.
    # -------------------------------------------------------

    table.setStyle(
        TableStyle(
            [
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
                    5,
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),

                # Extra top padding for heading.
                (
                    "TOPPADDING",
                    (0, 0),
                    (0, 0),
                    14,
                ),

                # Extra bottom padding for final row.
                (
                    "BOTTOMPADDING",
                    (0, -1),
                    (-1, -1),
                    14,
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
            ]
        )
    )

    return table


# ===========================================================
# KPI CARD
# ===========================================================

def create_metric_card(
    title_text,
    value,
):

    table = Table(
        [
            [
                Paragraph(
                    safe_text(title_text),
                    REPORT_STYLES["card_title"],
                )
            ],
            [
                Paragraph(
                    safe_text(value),
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

    table = Table(
        [
            [
                Paragraph(
                    f"<b>{safe_text(text)}</b>",
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

    # Keep both columns non-zero.
    minimum_width = 0.01

    filled = max(
        width * score / 100,
        minimum_width,
    )

    remaining = max(
        width - filled,
        minimum_width,
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
# TABLE CELL CONVERTER
# ===========================================================

def _table_cell_paragraphs(
    value,
    max_chars=700,
):
    """
    Convert one table cell into one or more safe Paragraphs.

    Multiple Paragraphs are returned so even very large AI-generated
    table content doesn't become one giant Paragraph.
    """

    if value is None:
        value = ""

    value = str(value)

    chunks = split_text_into_chunks(
        value,
        max_chars=max_chars,
    )

    return [
        Paragraph(
            safe_text(chunk),
            REPORT_STYLES["body"],
        )
        for chunk in chunks
    ]


# ===========================================================
# PREMIUM TABLE
# ===========================================================

def create_table(
    headers,
    rows,
):
    """
    Create a page-safe table.

    Features:

    - Sanitizes AI-generated content.
    - Splits large cells.
    - Repeats headers on every page.
    - Allows rows to split across pages.
    - Prevents huge Paragraph cells from crashing ReportLab.
    """

    # -------------------------------------------------------
    # Header
    # -------------------------------------------------------

    header_row = [
        Paragraph(
            safe_text(header),
            REPORT_STYLES["card_title"],
        )
        for header in headers
    ]

    data = [
        header_row
    ]

    # -------------------------------------------------------
    # Body
    # -------------------------------------------------------

    for row in rows:

        converted_row = []

        for cell in row:

            paragraphs = _table_cell_paragraphs(
                cell,
                max_chars=700,
            )

            # If there are multiple paragraphs in a single
            # cell, ReportLab can stack them vertically.
            converted_row.append(
                paragraphs
            )

        data.append(
            converted_row
        )

    # -------------------------------------------------------
    # Table
    # -------------------------------------------------------

    table = Table(
        data,
        repeatRows=1,
        splitByRow=1,
    )

    # -------------------------------------------------------
    # Style
    # -------------------------------------------------------

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
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
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
