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
                    (0,0),
                    (-1,-1),
                    PRIMARY
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
    Renders a titled card with a background box and border.

    IMPORTANT: `content` is split into one Table row per line,
    splitting on EITHER "<br/>" (the convention used throughout this
    codebase for joining bullet lists) OR a plain newline. This is
    not just cosmetic -- ReportLab Tables can only split BETWEEN
    rows, never WITHIN a single cell's Paragraph. Putting the entire
    body in one giant Paragraph/row meant any unusually long
    AI-generated content (many roadmap tasks, a multi-line diagram
    definition, etc.) could produce a cell taller than a full page,
    which is unrecoverable and crashes PDF generation outright
    (LayoutError: "... too large on page ..."). Splitting into many
    small rows lets the table flow across page boundaries naturally,
    no matter how long the content gets -- and splitting on plain
    newlines too (not just <br/>) means this protection applies even
    to call sites that pass raw multi-line text directly, without
    remembering to join it with <br/> themselves first.
    """

    content_str = "" if content is None else str(content)

    # Split on <br/> (tolerating <br>, <br />, <BR/> etc.) OR a
    # plain newline -- either one starts a new row.
    lines = re.split(r"<br\s*/?>|\n", content_str, flags=re.IGNORECASE)
    lines = [line.strip() for line in lines if line.strip()]

    if not lines:
        lines = [""]

    rows = [
        [Paragraph(str(heading), REPORT_STYLES["card_title"])]
    ]

    for line in lines:
        rows.append([Paragraph(line, REPORT_STYLES["body"])])

    table = Table(
        rows,
        colWidths=[7.0 * inch],
    )

    n_rows = len(rows)

    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, -1), CARD_BG),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 16),
        # Tight padding between internal rows so multiple short lines
        # don't look like separate cards stacked together...
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        # ...but generous padding at the very top and very bottom of
        # the whole card, matching the original single-block look.
        ("TOPPADDING", (0, 0), (0, 0), 14),
        ("BOTTOMPADDING", (0, n_rows - 1), (0, n_rows - 1), 14),
    ]

    table.setStyle(TableStyle(style_cmds))

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
                    REPORT_STYLES["card_title"]
                )

            ],

            [

                Paragraph(
                    str(value),
                    REPORT_STYLES["metric_value"]
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
                    (0,0),
                    (-1,-1),
                    colors.white
                ),

                (
                    "BOX",
                    (0,0),
                    (-1,-1),
                    0.6,
                    BORDER
                ),

                (
                    "BOTTOMPADDING",
                    (0,0),
                    (-1,-1),
                    18
                ),

                (
                    "TOPPADDING",
                    (0,0),
                    (-1,-1),
                    18
                ),

                (
                    "LEFTPADDING",
                    (0,0),
                    (-1,-1),
                    14
                ),

                (
                    "RIGHTPADDING",
                    (0,0),
                    (-1,-1),
                    14
                ),

                (
                    "ALIGN",
                    (0,0),
                    (-1,-1),
                    "CENTER"
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
                    (0,0),
                    (-1,-1),
                    8
                )

            ]

        )

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
                    REPORT_STYLES["muted"]
                )
            ]
        ]

    )


    table.setStyle(

        TableStyle(

            [

                (
                    "BACKGROUND",
                    (0,0),
                    (-1,-1),
                    colors.HexColor("#DBEAFE")
                ),

                (
                    "TEXTCOLOR",
                    (0,0),
                    (-1,-1),
                    PRIMARY
                ),

                (
                    "BOX",
                    (0,0),
                    (-1,-1),
                    0.4,
                    PRIMARY
                ),

                (
                    "LEFTPADDING",
                    (0,0),
                    (-1,-1),
                    8
                ),

                (
                    "RIGHTPADDING",
                    (0,0),
                    (-1,-1),
                    8
                ),

                (
                    "TOPPADDING",
                    (0,0),
                    (-1,-1),
                    4
                ),

                (
                    "BOTTOMPADDING",
                    (0,0),
                    (-1,-1),
                    4
                ),

            ]

        )

    )

    return table



# ===========================================================
# TAG GRID
# ===========================================================

def create_tag_grid(items, columns=4):

    rows = []
    row = []

    for item in items:

        row.append(
            create_tag(item)
        )

        if len(row) == columns:
            rows.append(row)
            row=[]


    if row:

        while len(row)<columns:
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

    score=max(
        0,
        min(score,100)
    )

    width=6.2*inch

    filled=width*score/100


    return Table(

        [["",""]],

        colWidths=[
            filled,
            width-filled
        ],

        rowHeights=[12],

        style=TableStyle(

            [

                (
                    "BACKGROUND",
                    (0,0),
                    (0,0),
                    SUCCESS
                ),

                (
                    "BACKGROUND",
                    (1,0),
                    (1,0),
                    BORDER
                ),

                (
                    "BOX",
                    (0,0),
                    (-1,-1),
                    0.3,
                    BORDER
                ),

            ]

        )

    )



# ===========================================================
# PREMIUM TABLE
# ===========================================================

def create_table(headers, rows):

    data=[headers]
    data.extend(rows)

    table=Table(data)


    table.setStyle(

        TableStyle(

            [

                (
                    "BACKGROUND",
                    (0,0),
                    (-1,0),
                    PRIMARY_DARK
                ),

                (
                    "TEXTCOLOR",
                    (0,0),
                    (-1,0),
                    colors.white
                ),

                (
                    "FONTNAME",
                    (0,0),
                    (-1,0),
                    "Helvetica-Bold"
                ),

                (
                    "GRID",
                    (0,0),
                    (-1,-1),
                    0.25,
                    BORDER
                ),

                (
                    "BOTTOMPADDING",
                    (0,0),
                    (-1,-1),
                    10
                ),

                (
                    "TOPPADDING",
                    (0,0),
                    (-1,-1),
                    10
                ),

                (
                    "LEFTPADDING",
                    (0,0),
                    (-1,-1),
                    8
                ),

                (
                    "RIGHTPADDING",
                    (0,0),
                    (-1,-1),
                    8
                ),

            ]

        )

    )

    return table

# Backward compatibility aliases

section = create_section_title

subheading = subsection

metric_card = create_metric_card

progress = create_progress

simple_table = create_table

info_table = create_table

badge_grid = create_tag_grid