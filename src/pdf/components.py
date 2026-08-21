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
# SAFE TEXT / SANITIZATION
# ===========================================================

def safe_text(text):
    """
    Convert arbitrary/AI-generated text into ReportLab-safe text.

    ReportLab Paragraph uses XML-like markup. AI-generated content can
    occasionally contain malformed HTML such as:

        <font size="18"></para>

    or raw characters such as <, > and &.

    Escaping the content prevents malformed AI output from breaking
    PDF generation.
    """

    if text is None:
        return ""

    return escape(str(text))


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
    Create a ReportLab card that is safe for arbitrary AI-generated text.

    The content is split into separate rows using <br/> so that large
    AI-generated lists can split across pages.

    Every piece of content is escaped before being passed to Paragraph,
    preventing malformed AI HTML/XML from causing ReportLab ParseError.
    """

    content_str = "" if content is None else str(content)

    # Split common HTML line-break variants.
    lines = re.split(
        r"<br\s*/?>",
        content_str,
        flags=re.IGNORECASE,
    )

    # Remove empty lines.
    lines = [
        line.strip()
        for line in lines
        if line.strip()
    ]

    if not lines:
        lines = [""]

    # Card heading.
    rows = [
        [
            Paragraph(
                safe_text(heading),
                REPORT_STYLES["card_title"],
            )
        ]
    ]

    # Card content.
    for line in lines:

        rows.append(
            [
                Paragraph(
                    safe_text(line),
                    REPORT_STYLES["body"],
                )
            ]
        )

    table = Table(
        rows,
        colWidths=[7.0 * inch],
        splitByRow=1,
    )

    n_rows = len(rows)

    style_cmds = [

        # Background.
        (
            "BACKGROUND",
            (0, 0),
            (-1, -1),
            CARD_BG,
        ),

        # Border.
        (
            "BOX",
            (0, 0),
            (-1, -1),
            0.5,
            BORDER,
        ),

        # Horizontal padding.
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

        # Default vertical padding.
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

        # Card top padding.
        (
            "TOPPADDING",
            (0, 0),
            (0, 0),
            14,
        ),

        # Card bottom padding.
        (
            "BOTTOMPADDING",
            (0, n_rows - 1),
            (0, n_rows - 1),
            14,
        ),

        # Keep text at the top of cells.
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

    score = max(
        0,
        min(score, 100),
    )

    width = 6.2 * inch

    filled = width * score / 100

    # Prevent zero-width table columns.
    minimum_width = 0.01

    filled_width = max(
        filled,
        minimum_width,
    )

    remaining_width = max(
        width - filled_width,
        minimum_width,
    )

    return Table(
        [["", ""]],
        colWidths=[
            filled_width,
            remaining_width,
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
    Create a page-splittable table.

    All cell values are converted into Paragraphs and sanitized
    before ReportLab receives them.

    repeatRows=1 keeps the header visible when the table continues
    onto another page.
    """

    # -------------------------------------------------------
    # Header cells
    # -------------------------------------------------------

    header_data = [
        Paragraph(
            safe_text(header),
            REPORT_STYLES["card_title"],
        )
        for header in headers
    ]

    data = [
        header_data
    ]

    # -------------------------------------------------------
    # Body cells
    # -------------------------------------------------------

    for row in rows:

        sanitized_row = []

        for cell in row:

            if cell is None:
                cell = ""

            sanitized_row.append(
                Paragraph(
                    safe_text(cell),
                    REPORT_STYLES["body"],
                )
            )

        data.append(
            sanitized_row
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
    # Table styling
    # -------------------------------------------------------

    table.setStyle(
        TableStyle(
            [
                # Header background.
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    PRIMARY_DARK,
                ),

                # Header text.
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),

                # Grid.
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.25,
                    BORDER,
                ),

                # Vertical alignment.
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),

                # Padding.
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
