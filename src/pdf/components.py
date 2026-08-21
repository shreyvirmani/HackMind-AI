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

MAX_CARD_CHARS = 900
MAX_LINE_CHARS = 450
TABLE_CELL_MAX_CHARS = 500


# ===========================================================
# SPACING
# ===========================================================

def space(height=12):
    return Spacer(1, height)


# ===========================================================
# SAFE TEXT / HTML HELPERS
# ===========================================================

def safe_text(value):
    """
    Convert arbitrary AI-generated content into safe text.

    ReportLab's Paragraph parser is NOT a Markdown parser.
    AI output can contain:
        **bold**
        __bold__
        # headings
        ```code```
        malformed HTML
        <para>
        <font>
        etc.

    This function prevents malformed markup from breaking PDF generation.
    """

    if value is None:
        return ""

    text = str(value)

    # Normalize line endings.
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Escape HTML first.
    text = html.escape(text, quote=False)

    # Convert Markdown-style bold to ReportLab-safe bold.
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

    # Convert Markdown italic.
    text = re.sub(
        r"(?<!\*)\*([^*\n]+)\*(?!\*)",
        r"<i>\1</i>",
        text,
    )

    # Convert inline code.
    text = re.sub(
        r"`([^`\n]+)`",
        r"<font name='Courier'>\1</font>",
        text,
    )

    # Remove fenced code markers.
    text = text.replace("```", "")

    # Convert markdown headings to bold text.
    text = re.sub(
        r"(?m)^\s*#{1,6}\s+",
        "",
        text,
    )

    # Convert markdown bullet markers.
    text = re.sub(
        r"(?m)^\s*[-*+]\s+",
        "• ",
        text,
    )

    # Convert numbered markdown lists.
    text = re.sub(
        r"(?m)^\s*(\d+)\.\s+",
        r"\1. ",
        text,
    )

    # Remove any remaining dangerous/unwanted ReportLab tags.
    text = re.sub(
        r"</?para\b[^>]*>",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Remove malformed font tags that AI may generate.
    text = re.sub(
        r"</?font\b[^>]*>",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Remove unsupported HTML tags.
    allowed_tags = {
        "b",
        "i",
        "u",
        "br",
    }

    def clean_tag(match):
        tag = match.group(0)

        tag_name_match = re.match(
            r"<\s*/?\s*([a-zA-Z0-9]+)",
            tag,
        )

        if not tag_name_match:
            return ""

        tag_name = tag_name_match.group(1).lower()

        if tag_name in allowed_tags:
            return tag

        return ""

    text = re.sub(
        r"<[^>]+>",
        clean_tag,
        text,
    )

    # Collapse excessive whitespace while preserving newlines.
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


def split_long_text(text, max_chars=MAX_CARD_CHARS):
    """
    Split very large AI-generated text into safe chunks.

    This is the important fix for the ReportLab LayoutError.

    Even if the AI returns one giant paragraph without <br/>,
    this guarantees that no individual Table row contains an
    enormous Paragraph.
    """

    if not text:
        return [""]

    text = safe_text(text)

    if len(text) <= max_chars:
        return [text]

    chunks = []

    # First split by existing line breaks.
    paragraphs = re.split(
        r"\n+",
        text,
    )

    current = ""

    for paragraph in paragraphs:

        paragraph = paragraph.strip()

        if not paragraph:
            continue

        # If this paragraph itself is huge, split it further.
        if len(paragraph) > max_chars:

            words = paragraph.split()

            for word in words:

                candidate = (
                    f"{current} {word}".strip()
                )

                if len(candidate) > max_chars:

                    if current:
                        chunks.append(
                            current.strip()
                        )

                    current = word

                else:
                    current = candidate

        else:

            candidate = (
                f"{current}\n{paragraph}"
                if current
                else paragraph
            )

            if len(candidate) > max_chars:

                if current:
                    chunks.append(
                        current.strip()
                    )

                current = paragraph

            else:
                current = candidate

    if current:
        chunks.append(
            current.strip()
        )

    return chunks or [""]


def split_table_cell(value):
    """
    Prevent gigantic table cells.

    Returns a safe string with explicit <br/> separators.
    """

    if value is None:
        return ""

    text = safe_text(value)

    if len(text) <= TABLE_CELL_MAX_CHARS:
        return text

    chunks = split_long_text(
        text,
        TABLE_CELL_MAX_CHARS,
    )

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
    Creates a safe PDF card.

    IMPORTANT:
    Never put an arbitrary AI-generated giant string into a single
    ReportLab Table cell.

    The content is split into multiple rows so ReportLab can
    paginate the card safely.
    """

    heading_text = safe_text(heading)

    content_str = (
        ""
        if content is None
        else str(content)
    )

    # Normalize all line-break variants.
    content_str = re.sub(
        r"<br\s*/?>",
        "\n",
        content_str,
        flags=re.IGNORECASE,
    )

    # Convert HTML breaks that may have been escaped.
    content_str = content_str.replace(
        "&lt;br/&gt;",
        "\n",
    )

    # Split the content into manageable chunks.
    raw_chunks = split_long_text(
        content_str,
        MAX_CARD_CHARS,
    )

    if not raw_chunks:
        raw_chunks = [""]

    rows = [
        [
            Paragraph(
                heading_text,
                REPORT_STYLES["card_title"],
            )
        ]
    ]

    for chunk in raw_chunks:

        # Convert newlines inside the chunk to ReportLab breaks.
        chunk = safe_text(chunk)

        chunk = chunk.replace(
            "\n",
            "<br/>",
        )

        rows.append(
            [
                Paragraph(
                    chunk,
                    REPORT_STYLES["body"],
                )
            ]
        )

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

        (
            "TOPPADDING",
            (0, 0),
            (0, 0),
            14,
        ),

        (
            "BOTTOMPADDING",
            (0, n_rows - 1),
            (0, n_rows - 1),
            14,
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

    if not rows:
        return Table([[""]])

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

    filled = width * score / 100

    # Prevent zero-width table columns.
    minimum_width = 0.01

    filled = max(
        minimum_width,
        filled,
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
    Safe table renderer.

    Every cell is converted into a Paragraph and long content
    gets explicit line breaks.

    This prevents huge AI-generated API/database/architecture
    fields from creating impossible table rows.
    """

    safe_headers = [
        safe_text(header)
        for header in headers
    ]

    safe_rows = []

    for row in rows:

        safe_row = []

        for value in row:

            text = split_table_cell(
                value
            )

            # Paragraphs are much safer than raw strings for
            # ReportLab tables containing long text.
            safe_row.append(
                Paragraph(
                    text,
                    REPORT_STYLES["body"],
                )
            )

        safe_rows.append(
            safe_row
        )

    header_row = [
        Paragraph(
            header,
            REPORT_STYLES["body"],
        )
        for header in safe_headers
    ]

    data = [
        header_row,
        *safe_rows,
    ]

    # Determine sensible column widths.
    column_count = len(headers)

    if column_count <= 3:

        available_width = 7.0 * inch

        col_width = (
            available_width
            / max(column_count, 1)
        )

        col_widths = [
            col_width
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

        available_width = 7.0 * inch

        col_width = (
            available_width
            / column_count
        )

        col_widths = [
            col_width
            for _ in range(column_count)
        ]

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
