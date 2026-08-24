from reportlab.platypus import (
    Spacer,
    Table,
    TableStyle,
    Paragraph,
)

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER

from src.pdf.styles import REPORT_STYLES
from src.pdf.components import safe_text



def build_cover_section(project):

    elements = []


    # =====================================================
    # TOP SPACE
    # =====================================================

    elements.append(
        Spacer(
            1,
            0.45 * inch
        )
    )


    # =====================================================
    # LOGO
    # =====================================================

    logo = Table(

        [
            [
                Paragraph(
                    "<b>H</b>",
                    REPORT_STYLES["body_center"]
                )
            ]
        ],

        colWidths=[
            0.9*inch
        ],

        rowHeights=[
            0.9*inch
        ]

    )


    logo.setStyle(

        TableStyle(

            [

                (
                    "BACKGROUND",
                    (0,0),
                    (-1,-1),
                    colors.HexColor("#06B6D4")
                ),

                (
                    "TEXTCOLOR",
                    (0,0),
                    (-1,-1),
                    colors.white
                ),

                (
                    "FONTNAME",
                    (0,0),
                    (-1,-1),
                    "Helvetica-Bold"
                ),

                (
                    "FONTSIZE",
                    (0,0),
                    (-1,-1),
                    34
                ),

                (
                    "ALIGN",
                    (0,0),
                    (-1,-1),
                    "CENTER"
                ),

                (
                    "VALIGN",
                    (0,0),
                    (-1,-1),
                    "MIDDLE"
                ),

            ]

        )

    )


    elements.append(logo)


    elements.append(
        Spacer(
            1,
            0.25*inch
        )
    )


    # =====================================================
    # BRAND
    # =====================================================


    brand = REPORT_STYLES["cover_title"].clone(
        "PremiumBrand"
    )


    brand.fontSize = 38
    brand.leading = 45
    brand.alignment = TA_CENTER
    brand.textColor = colors.HexColor("#2563EB")


    elements.append(

        Paragraph(
            "HackMind AI",
            brand
        )

    )


    elements.append(
        Spacer(
            1,
            0.12*inch
        )
    )



    subtitle = REPORT_STYLES["cover_subtitle"].clone(
        "PremiumSubtitle"
    )


    subtitle.fontSize = 15
    subtitle.alignment = TA_CENTER
    subtitle.textColor = colors.HexColor("#64748B")


    elements.append(

        Paragraph(

            "AI Powered Startup Intelligence Report",

            subtitle

        )

    )


    elements.append(
        Spacer(
            1,
            0.55*inch
        )
    )


    # =====================================================
    # PROJECT HERO
    # =====================================================


    project_title = getattr(
        project,
        "project_title",
        "Startup Project"
    )


    hero = Table(

        [

            [

                Paragraph(

                    f"""
                    <font color="#FFFFFF">
                    <b>{safe_text(project_title)}</b>
                    </font>
                    """,

                    REPORT_STYLES["premium_hero"]

                )

            ]

        ],

        colWidths=[
            6.9*inch
        ]

    )


    hero.setStyle(

        TableStyle(

            [

                (
                    "BACKGROUND",
                    (0,0),
                    (-1,-1),
                    colors.HexColor("#0F172A")
                ),


                (
                    "BOX",
                    (0,0),
                    (-1,-1),
                    1,
                    colors.HexColor("#06B6D4")
                ),


                (
                    "ALIGN",
                    (0,0),
                    (-1,-1),
                    "CENTER"
                ),


                (
                    "TOPPADDING",
                    (0,0),
                    (-1,-1),
                    28
                ),


                (
                    "BOTTOMPADDING",
                    (0,0),
                    (-1,-1),
                    28
                ),


            ]

        )

    )


    elements.append(hero)


    elements.append(
        Spacer(
            1,
            0.3*inch
        )
    )



    # =====================================================
    # IDEA CARD
    # =====================================================


    idea = getattr(
        project,
        "idea",
        ""
    )


    idea_table = Table(

        [

            [

                Paragraph(
                    "<b>Startup Vision</b>",
                    REPORT_STYLES["card_title"]
                )

            ],


            [

                Paragraph(
                    idea,
                    REPORT_STYLES["body"]
                )

            ]

        ],

        colWidths=[
            6.9*inch
        ]

    )


    idea_table.setStyle(

        TableStyle(

            [

                (
                    "BACKGROUND",
                    (0,0),
                    (-1,-1),
                    colors.HexColor("#EFF6FF")
                ),


                (
                    "BOX",
                    (0,0),
                    (-1,-1),
                    0.8,
                    colors.HexColor("#93C5FD")
                ),


                (
                    "LEFTPADDING",
                    (0,0),
                    (-1,-1),
                    18
                ),


                (
                    "RIGHTPADDING",
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
                    "BOTTOMPADDING",
                    (0,0),
                    (-1,-1),
                    18
                ),

            ]

        )

    )


    elements.append(
        idea_table
    )


    elements.append(
        Spacer(
            1,
            0.35*inch
        )
    )



    # =====================================================
    # SCORE
    # =====================================================


    score = getattr(
        project,
        "overall_score",
        0
    )


    score_table = Table(

        [

            [

                Paragraph(
                    "<b>AI Evaluation Score</b>",
                    REPORT_STYLES["card_title"]
                ),


                Paragraph(

                    f"""
                    <font color="#06B6D4">
                    <b>{score}/100</b>
                    </font>
                    """,

                    REPORT_STYLES["metric_value"]

                )

            ]

        ],

        colWidths=[
            4.8*inch,
            2.1*inch
        ]

    )


    score_table.setStyle(

        TableStyle(

            [

                (
                    "BACKGROUND",
                    (0,0),
                    (-1,-1),
                    colors.HexColor("#F8FAFC")
                ),


                (
                    "BOX",
                    (0,0),
                    (-1,-1),
                    1,
                    colors.HexColor("#06B6D4")
                ),


                (
                    "VALIGN",
                    (0,0),
                    (-1,-1),
                    "MIDDLE"
                ),


                (
                    "TOPPADDING",
                    (0,0),
                    (-1,-1),
                    18
                ),


                (
                    "BOTTOMPADDING",
                    (0,0),
                    (-1,-1),
                    18
                ),

            ]

        )

    )


    elements.append(score_table)


    elements.append(
        Spacer(
            1,
            0.9*inch
        )
    )



    # =====================================================
    # FOOTER
    # =====================================================


    footer = REPORT_STYLES["footer"].clone(
        "PremiumFooter"
    )


    footer.alignment = TA_CENTER


    elements.append(

        Paragraph(
            "Generated by HackMind AI Copilot",
            footer
        )

    )


    elements.append(

        Paragraph(
            "Planner • Research • Judge • Pitch Architect",
            footer
        )

    )


    elements.append(

        Paragraph(
            "Confidential Startup Intelligence Document",
            footer
        )

    )


    return elements