import re

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
# SPACING
# ===========================================================

def space(height=12):
    return Spacer(1, height)


# ===========================================================
# TYPOGRAPHY
# ===========================================================

def title(text):
    return Paragraph(
        str(text),
        REPORT_STYLES["cover_title"]
    )


def section_title(text):
    return Paragraph(
        str(text),
        REPORT_STYLES["section_title"]
    )


def subsection(text):
    return Paragraph(
        str(text),
        REPORT_STYLES["subsection_title"]
    )


def body(text):
    return Paragraph(
        str(text),
        REPORT_STYLES["body"]
    )


def muted(text):
    return Paragraph(
        str(text),
        REPORT_STYLES["muted"]
    )


def bullet(text):
    return Paragraph(
        f"• {text}",
        REPORT_STYLES["bullet"]
    )


def code(text):
    return Paragraph(
        f"<font face='Courier'>{text}</font>",
        REPORT_STYLES["code"]
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
# TEXT SANITIZATION
# ===========================================================

def _escape_xml(text):
    """
    Escape characters that can break ReportLab's XML-like
    Paragraph markup while preserving the markup we intentionally
    generate ourselves.
    """

    text = str(text)

    # Preserve common ReportLab tags already present in generated
    # content. This function intentionally does not escape <br>,
    # <b>, <font>, etc.
    return text


def _split_long_text(text, max_chars=900):
    """
    Split very long AI-generated text into manageable chunks.

    ReportLab can split a Paragraph across lines, but a single
    extremely long unbreakable string / generated block can still
    produce a table row taller than a page.

    Splitting by words gives ReportLab safe boundaries.
    """

    text = str(text).strip()

    if not text:
        return [""]

    if len(text) <= max_chars:
        return [text]

    chunks = []
    current = []

    current_length = 0

    # Preserve whitespace-separated words.
    words = text.split()

    for word in words:

        word_length = len(word)

        # Extremely long single token.
        if word_length > max_chars:

            if current:
                chunks.append(" ".join(current))
                current = []
                current_length = 0

            # Hard split extremely long token.
            for i in range(0, len(word), max_chars):
                chunks.append(
                    word[i:i + max_chars]
                )

            continue

        additional_length = (
            word_length
            if not current
            else word_length + 1
        )

        if (
            current
            and
            current_length + additional_length > max_chars
        ):

            chunks.append(
                " ".join(current)
            )

            current = [word]
            current_length = word_length

        else:

            current.append(word)
            current_length += additional_length

    if current:
        chunks.append(
            " ".join(current)
        )

    return chunks


def _split_content_lines(content):
    """
    Convert card content into safe chunks.

    Supports:
      - <br>
      - <br/>
      - <br />
      - newline characters
      - very long individual lines
    """

    content_str = (
        ""
        if content is None
        else str(content)
    )

    # Normalize HTML breaks to newlines.
    content_str = re.sub(
        r"<br\s*/?>",
        "\n",
        content_str,
        flags=re.IGNORECASE,
    )

    # Normalize Windows line endings.
    content_str = content_str.replace(
        "\r\n",
        "\n",
    )

    content_str = content_str.replace(
        "\r",
        "\n",
    )

    raw_lines = content_str.split("\n")

    lines = []

    for line in raw_lines:

        line = line.strip()

        if not line:
            continue

        chunks = _split_long_text(
            line,
            max_chars=900,
        )

        lines.extend(chunks)

    if not lines:
        lines = [""]

    return lines


# ===========================================================
# PREMIUM CARD
# ===========================================================

def create_card(
    heading,
    content,
):
    """
    Render a premium HackMind card.

    Important:
    Long AI-generated content is split into multiple table rows.
    Each row contains a reasonably sized Paragraph so ReportLab can
    move the rows across page boundaries.

    This prevents:

        LayoutError:
        Flowable <Table ...> too large on page

    caused by a single giant Paragraph inside a single table cell.
    """

    lines = _split_content_lines(content)

    rows = [
        [
            Paragraph(
                str(heading),
                REPORT_STYLES["card_title"],
            )
        ]
    ]

    for line in lines:

        rows.append(
            [
                Paragraph(
                    line,
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
            3,
        ),

        (
            "BOTTOMPADDING",
            (0, 0),
            (-1, -1),
            3,
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
                    str(title_text),
                    REPORT_STYLES["card_title"],
                )
            ],
            [
                Paragraph(
                    str(value),
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
                    f"<b>{text}</b>",
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
        splitByRow=1,
    )


# ===========================================================
# PROGRESS BAR
# ===========================================================

def create_progress(score):

    score = max(
        0,
        min(score, 100),
    )

    width = 6.2 * inch

    filled = width * score / 100

    return Table(
        [["", ""]],
        colWidths=[
            filled,
            width - filled,
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

    data = [
        headers
    ]

    data.extend(
        rows
    )

    table = Table(
        data,
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
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
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
