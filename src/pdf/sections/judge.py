from src.pdf.components import (
    safe_text,
    create_section_title,
    create_metric_card,
    create_metric_dashboard,
    create_progress,
    create_card,
    create_table,
    subsection,
    body,
    bullet,
    space,
)


class JudgeSection:

    def build(self, judge):

        story = []


        # ======================================================
        # HEADER
        # ======================================================

        story.append(
            create_section_title(
                "AI Evaluation Report"
            )
        )

        story.append(
            space(14)
        )


        # ======================================================
        # DATA EXTRACTION
        # ======================================================

        score = judge.get(
            "overall_score",
            0
        )

        feedback = judge.get(
            "overall_feedback",
            "No evaluation feedback available."
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


        # ======================================================
        # EXECUTIVE SCORE DASHBOARD
        # ======================================================

        dashboard = create_metric_dashboard(

            [

                create_metric_card(
                    "Overall Score",
                    f"{score}/100"
                ),

                create_metric_card(
                    "Strengths",
                    len(strengths)
                ),

                create_metric_card(
                    "Improvements",
                    len(improvements)
                ),

            ]

        )


        story.append(
            dashboard
        )

        story.append(
            space(18)
        )


        # ======================================================
        # SCORE BAR
        # ======================================================

        story.append(
            create_progress(score)
        )

        story.append(
            space(24)
        )


        # ======================================================
        # AI VERDICT
        # ======================================================

        story.append(

            create_card(

                "HackMind AI Final Verdict",

                safe_text(feedback)

            )

        )

        story.append(
            space(20)
        )


        # ======================================================
        # STRENGTHS / WEAKNESSES
        # ======================================================

        if strengths:

            strength_text = "<br/>".join(

                [
                    f"✓ {safe_text(item)}"
                    for item in strengths
                ]

            )

            story.append(

                create_card(

                    "Key Strengths",

                    strength_text

                )

            )

            story.append(
                space(16)
            )


        if weaknesses:

            weakness_text = "<br/>".join(

                [
                    f"⚠ {safe_text(item)}"
                    for item in weaknesses
                ]

            )


            story.append(

                create_card(

                    "Critical Weaknesses",

                    weakness_text

                )

            )

            story.append(
                space(16)
            )



        # ======================================================
        # IMPROVEMENT ROADMAP
        # ======================================================

        if improvements:

            improvement_text = "<br/>".join(

                [
                    f"→ {safe_text(item)}"
                    for item in improvements
                ]

            )


            story.append(

                create_card(

                    "Recommended Improvements",

                    improvement_text

                )

            )

            story.append(
                space(20)
            )



        # ======================================================
        # EVALUATION METRICS TABLE
        # ======================================================

        story.append(

            subsection(
                "Evaluation Summary"
            )

        )

        rows = [

            [

                "Metric",

                "Result"

            ],

            [

                "Overall Score",

                f"{score}/100"

            ],

            [

                "Strength Analysis",

                str(len(strengths))

            ],

            [

                "Risk Factors",

                str(len(weaknesses))

            ],

            [

                "Optimization Areas",

                str(len(improvements))

            ]

        ]


        story.append(

            create_table(

                rows[0],

                rows[1:]

            )

        )


        story.append(
            space(24)
        )


        # ======================================================
        # INVESTMENT READINESS
        # ======================================================

        story.append(

            subsection(
                "AI Investment Readiness Assessment"
            )

        )


        if score >= 90:

            readiness = (
                "Exceptional startup potential. "
                "The concept demonstrates strong innovation, "
                "market opportunity and execution readiness."
            )


        elif score >= 80:

            readiness = (
                "Strong startup foundation. "
                "The solution has clear potential with "
                "minor improvements required for market validation."
            )


        elif score >= 70:

            readiness = (
                "Promising concept with a good foundation. "
                "Further refinement in product strategy, "
                "validation and scalability is recommended."
            )


        else:

            readiness = (
                "Early-stage concept requiring additional "
                "development before achieving strong startup readiness."
            )


        story.append(

            create_card(

                "Final Assessment",

                readiness

            )

        )


        story.append(
            space(30)
        )


        return story



judge_section = JudgeSection()