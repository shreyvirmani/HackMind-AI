from src.pdf.components import (
    create_section_title,
    create_card,
    create_table,
    subsection,
    space,
)


class ResearchSection:

    def build(self, research):

        story = []

        if not isinstance(research, dict):
            research = {}



        # =====================================================
        # HEADER
        # ====================================================

        # =====================================================
        # MARKET ANALYSIS
        # =====================================================

        market = research.get(
            "market_analysis",
            ""
        )


        if market:

            story.append(
                create_card(
                    "Market Overview",
                    market
                )
            )

            story.append(
                space(18)
            )



        # =====================================================
        # TARGET AUDIENCE
        # =====================================================

        audience = research.get(
            "target_audience",
            []
        )


        if audience:


            if isinstance(audience, list):

                audience_text = "<br/>".join(
                    [
                        f"✓ {item}"
                        for item in audience
                    ]
                )

            else:

                audience_text = str(audience)



            story.append(
                create_card(
                    "Target Audience Segmentation",
                    audience_text
                )
            )


            story.append(
                space(18)
            )



        # =====================================================
        # COMPETITOR ANALYSIS
        # =====================================================

        competitors = research.get(
            "competitor_analysis",
            []
        )


        if competitors:


            rows = []


            if isinstance(competitors, list):

                for comp in competitors:


                    if isinstance(comp, dict):

                        rows.append(
                            [
                                comp.get(
                                    "name",
                                    ""
                                ),

                                comp.get(
                                    "strengths",
                                    ""
                                )
                            ]
                        )

                    else:

                        rows.append(
                            [
                                str(comp),
                                "-"
                            ]
                        )


            if rows:


                story.append(
                    subsection(
                        "Competitive Landscape"
                    )
                )


                story.append(
                    create_table(
                        [
                            "Competitor",
                            "Strengths"
                        ],
                        rows
                    )
                )


                story.append(
                    space(22)
                )



        # =====================================================
        # EXISTING SOLUTIONS
        # =====================================================

        existing = research.get(
            "existing_solutions",
            []
        )


        if existing:


            if isinstance(existing,list):

                text = "<br/>".join(
                    [
                        f"→ {x}"
                        for x in existing
                    ]
                )

            else:

                text = str(existing)


            story.append(
                create_card(
                    "Existing Market Solutions",
                    text
                )
            )


            story.append(
                space(18)
            )



        # =====================================================
        # MARKET GAP
        # =====================================================

        gap = research.get(
            "market_gap",
            ""
        )


        if gap:


            story.append(
                create_card(
                    "Identified Market Gap",
                    gap
                )
            )


            story.append(
                space(18)
            )



        # =====================================================
        # SWOT ANALYSIS
        # =====================================================

        swot = research.get(
            "swot_analysis",
            {}
        )


        if isinstance(swot, dict) and swot:


            story.append(
                subsection(
                    "Strategic SWOT Analysis"
                )
            )


            for key in [
                "strengths",
                "weaknesses",
                "opportunities",
                "threats"
            ]:


                value = swot.get(
                    key,
                    []
                )


                if not value:
                    continue



                if isinstance(value,list):

                    content = "<br/>".join(
                        [
                            f"• {x}"
                            for x in value
                        ]
                    )

                else:

                    content = str(value)



                story.append(
                    create_card(
                        key.title(),
                        content
                    )
                )


                story.append(
                    space(12)
                )



        # =====================================================
        # BUSINESS MODEL
        # =====================================================

        business = research.get(
            "business_model",
            ""
        )


        if business:


            story.append(
                create_card(
                    "Business Model",
                    business
                )
            )


            story.append(
                space(18)
            )



        # =====================================================
        # REVENUE MODEL
        # =====================================================

        revenue = research.get(
            "revenue_model",
            ""
        )


        if revenue:


            story.append(
                create_card(
                    "Revenue Strategy",
                    revenue
                )
            )


            story.append(
                space(18)
            )



        # =====================================================
        # RISKS
        # =====================================================

        risks = research.get(
            "risks",
            []
        )


        if risks:


            if isinstance(risks,list):

                risk_text = "<br/>".join(
                    [
                        f"⚠ {x}"
                        for x in risks
                    ]
                )

            else:

                risk_text = str(risks)



            story.append(
                create_card(
                    "Potential Business Risks",
                    risk_text
                )
            )



        story.append(
            space(30)
        )


        return story



research_section = ResearchSection()