from reportlab.platypus import (
    Spacer,
    Table,
    TableStyle,
    Paragraph,
)

from reportlab.lib import colors
from reportlab.lib.units import inch

from src.pdf.components import (
    create_section_title,
    create_card,
    create_metric_card,
    create_metric_dashboard,
    create_progress,
    safe_text,
    collapse_ws,
)

from src.pdf.styles import REPORT_STYLES



def build_executive_summary(project):

    elements = []

    roadmap = project.roadmap or {}
    judge = project.judge or {}

    score = judge.get(
        "overall_score",
        getattr(project, "overall_score", 0)
    )


    # ==================================================
    # SAFE DATA EXTRACTION
    # ==================================================

    title = (
        roadmap.get("project_title")
        or getattr(project, "project_title", "")
    )


    tagline = roadmap.get(
        "tagline",
        ""
    )


    problem = roadmap.get(
        "problem_statement",
        ""
    )


    solution = roadmap.get(
        "solution",
        ""
    )


    target_users = roadmap.get(
        "target_users",
        []
    )


    strengths = judge.get(
        "strengths",
        []
    )


    weaknesses = judge.get(
        "weaknesses",
        []
    )


    improvements = judge.get(
        "improvements",
        []
    )


    feedback = judge.get(
        "overall_feedback",
        ""
    )


    # ==================================================
    # HEADER
    # ==================================================

    elements.append(
        create_section_title(
            "Executive Summary"
        )
    )


    elements.append(
        Spacer(1,20)
    )



    # ==================================================
    # HERO CARD
    # ==================================================

    hero_parts = []


    if title:

        hero_parts.append(
            collapse_ws(f"""
            <font size="18">
            <b>{safe_text(title)}</b>
            </font>
            """)
        )


    if tagline:

        hero_parts.append(
            collapse_ws(f"""
            <br/><br/>
            <font color="#2563EB">
            {safe_text(tagline)}
            </font>
            """)
        )


    if hero_parts:

        elements.append(
            create_card(
                "Startup Overview",
                "".join(hero_parts)
            )
        )


        elements.append(
            Spacer(1,20)
        )



    # ==================================================
    # KPI SECTION
    # ==================================================

    dashboard = create_metric_dashboard(
        [

            create_metric_card(
                "AI Score",
                f"{score}/100"
            ),

            create_metric_card(
                "Strengths",
                len(strengths)
            ),

            create_metric_card(
                "Improvements",
                len(improvements)
            )

        ]
    )


    elements.append(
        dashboard
    )


    elements.append(
        Spacer(1,15)
    )


    elements.append(
        create_progress(score)
    )


    elements.append(
        Spacer(1,25)
    )



    # ==================================================
    # PROBLEM
    # ==================================================

    if problem:

        elements.append(
            create_card(
                "Problem Statement",
                safe_text(problem)
            )
        )


        elements.append(
            Spacer(1,15)
        )



    # ==================================================
    # SOLUTION
    # ==================================================

    if solution:

        elements.append(
            create_card(
                "Proposed Solution",
                safe_text(solution)
            )
        )


        elements.append(
            Spacer(1,15)
        )



    # ==================================================
    # TARGET USERS
    # ==================================================

    if target_users:

        if isinstance(target_users, list):

            users = "<br/>".join(
                [
                    f"• {safe_text(x)}"
                    for x in target_users
                ]
            )

        else:

            users = str(target_users)


        elements.append(
            create_card(
                "Target Users",
                users
            )
        )


        elements.append(
            Spacer(1,15)
        )



    # ==================================================
    # SWOT
    # ==================================================

    if strengths or weaknesses:


        strength_text = "<br/>".join(
            [
                f"• {safe_text(x)}"
                for x in strengths
            ]
        )


        weakness_text = "<br/>".join(
            [
                f"• {safe_text(x)}"
                for x in weaknesses
            ]
        )


        if not strength_text:
            strength_text = "Not available"


        if not weakness_text:
            weakness_text = "Not available"



        swot = Table(

            [

                [

                    Paragraph(
                        "<b>Strengths</b>",
                        REPORT_STYLES["body"]
                    ),

                    Paragraph(
                        "<b>Weaknesses</b>",
                        REPORT_STYLES["body"]
                    )

                ],


                [

                    Paragraph(
                        strength_text,
                        REPORT_STYLES["body"]
                    ),


                    Paragraph(
                        weakness_text,
                        REPORT_STYLES["body"]
                    )

                ]

            ],

            colWidths=[
                3.45 * inch,
                3.45 * inch
            ]

        )


        swot.setStyle(

            TableStyle(

                [

                    (
                        "BACKGROUND",
                        (0,0),
                        (-1,0),
                        colors.HexColor("#1E3A8A")
                    ),

                    (
                        "TEXTCOLOR",
                        (0,0),
                        (-1,0),
                        colors.white
                    ),

                    (
                        "GRID",
                        (0,0),
                        (-1,-1),
                        0.5,
                        colors.HexColor("#CBD5E1")
                    ),

                    (
                        "VALIGN",
                        (0,0),
                        (-1,-1),
                        "TOP"
                    ),

                    (
                        "LEFTPADDING",
                        (0,0),
                        (-1,-1),
                        12
                    ),

                    (
                        "RIGHTPADDING",
                        (0,0),
                        (-1,-1),
                        12
                    ),

                    (
                        "TOPPADDING",
                        (0,0),
                        (-1,-1),
                        12
                    ),

                    (
                        "BOTTOMPADDING",
                        (0,0),
                        (-1,-1),
                        12
                    ),

                ]

            )

        )


        elements.append(
            swot
        )


        elements.append(
            Spacer(1,20)
        )



    # ==================================================
    # IMPROVEMENTS
    # ==================================================

    if improvements:


        improvement_text = "<br/>".join(
            [
                f"→ {safe_text(x)}"
                for x in improvements
            ]
        )


        elements.append(
            create_card(
                "Recommended Improvements",
                improvement_text
            )
        )


        elements.append(
            Spacer(1,20)
        )



    # ==================================================
    # FINAL VERDICT
    # ==================================================

    if feedback:

        elements.append(
            create_card(
                "HackMind AI Final Verdict",
                safe_text(feedback)
            )
        )


    return elements