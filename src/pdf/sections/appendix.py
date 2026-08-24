from src.pdf.components import (
    safe_text,
    create_section_title,
    create_card,
    create_tag_grid,
    subsection,
    space,
)



class AppendixSection:


    def build(self, project):

        story = []


        # =====================================================
        # HEADER
        # =====================================================

        story.append(

            create_section_title(
                "Appendix & Technical Documentation"
            )

        )

        story.append(
            space(18)
        )


        roadmap = (
            project.roadmap
            if isinstance(project.roadmap, dict)
            else {}
        )


        research = (
            project.research
            if isinstance(project.research, dict)
            else {}
        )


        # =====================================================
        # FUTURE SCOPE
        # =====================================================

        future_scope = (

            roadmap.get(
                "future_scope",
                ""
            )

            or

            research.get(
                "future_scope",
                ""
            )

        )


        if future_scope:


            if isinstance(future_scope,list):

                future_text = "<br/>".join(

                    [
                        f"→ {safe_text(item)}"
                        for item in future_scope
                    ]

                )

            else:
                future_text = safe_text(future_scope).replace("\n", "<br/>")



            story.append(

                create_card(

                    "Future Expansion Opportunities",

                    future_text

                )

            )


            story.append(
                space(20)
            )



        # =====================================================
        # DEVELOPMENT TIMELINE
        # =====================================================

        timeline = roadmap.get(
            "development_timeline",
            []
        )


        if timeline:


            story.append(

                subsection(
                    "Detailed Development Timeline"
                )

            )


            for phase in timeline:


                if not isinstance(
                    phase,
                    dict
                ):

                    continue



                phase_name = phase.get(
                    "phase",
                    "Development Phase"
                )


                tasks = phase.get(
                    "tasks",
                    []
                )


                task_text = "<br/>".join(

                    [
                        f"✓ {safe_text(task)}"
                        for task in tasks
                    ]

                )


                story.append(

                    create_card(

                        phase_name,

                        task_text

                    )

                )


                story.append(
                    space(12)
                )



        # =====================================================
        # TEAM RESPONSIBILITIES
        # =====================================================

        roles = roadmap.get(
            "team_roles",
            []
        )


        if roles:


            story.append(

                subsection(
                    "Recommended Team Responsibilities"
                )

            )


            for role in roles:


                if not isinstance(
                    role,
                    dict
                ):

                    continue


                story.append(

                    create_card(

                        role.get(
                            "role",
                            "Team Role"
                        ),

                        safe_text(
                            role.get(
                                "responsibilities",
                                ""
                            )
                        )

                    )

                )


                story.append(
                    space(12)
                )



        # =====================================================
        # TECHNOLOGY STACK
        # =====================================================

        tech = roadmap.get(
            "tech_stack",
            {}
        )


        technologies = []


        if isinstance(
            tech,
            dict
        ):


            for values in tech.values():


                if isinstance(
                    values,
                    list
                ):

                    technologies.extend(
                        values
                    )


                else:

                    technologies.append(
                        str(values)
                    )



        if technologies:


            story.append(

                subsection(
                    "Complete Technology Stack"
                )

            )


            story.append(

                create_tag_grid(
                    technologies
                )

            )


            story.append(
                space(22)
            )



        # =====================================================
        # SYSTEM ARCHITECTURE
        # =====================================================

        architecture = roadmap.get(
            "system_architecture",
            ""
        )


        if architecture:


            story.append(

                create_card(

                    "System Architecture Documentation",

                    safe_text(architecture)

                )

            )


            story.append(
                space(20)
            )



        # =====================================================
        # REPORT INFORMATION
        # =====================================================


        report_info = """

        This report was generated by HackMind AI Copilot.

        Multi-agent workflow:

        • Planner Agent - Product roadmap and execution strategy

        • Research Agent - Market validation and competitive analysis

        • Judge Agent - AI evaluation and improvement feedback

        • Pitch Agent - Investor narrative and business strategy


        Each module is independently generated and combined into a
        complete startup intelligence document.

        """


        story.append(

            create_card(

                "Report Generation Information",

                report_info

            )

        )


        story.append(
            space(30)
        )


        return story



appendix_section = AppendixSection()