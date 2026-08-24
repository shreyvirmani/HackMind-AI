from src.pdf.components import (
    safe_text,
    create_section_title,
    create_card,
    create_metric_card,
    create_metric_dashboard,
    create_tag_grid,
    subsection,
    space,
)



class PlannerSection:


    def build(self, roadmap):

        story = []


        if not isinstance(roadmap, dict):

            roadmap = {}



        # =====================================================
        # HEADER
        # =====================================================

        story.append(

            create_section_title(
                "Startup Blueprint & Product Roadmap"
            )

        )

        story.append(
            space(16)
        )



        # =====================================================
        # DATA EXTRACTION
        # =====================================================

        features = roadmap.get(
            "features",
            []
        )

        users = roadmap.get(
            "target_users",
            []
        )

        timeline = roadmap.get(
            "development_timeline",
            []
        )



        # =====================================================
        # ROADMAP DASHBOARD
        # ONLY SHOW NON ZERO METRICS
        # =====================================================

        metrics = []


        if features:

            metrics.append(

                create_metric_card(
                    "Features",
                    len(features)
                )

            )


        if users:

            metrics.append(

                create_metric_card(
                    "Target Users",
                    len(users)
                )

            )


       



        if metrics:

            story.append(

                create_metric_dashboard(
                    metrics
                )

            )


            story.append(
                space(24)
            )



        # =====================================================
        # PROBLEM STATEMENT
        # =====================================================

        problem = roadmap.get(
            "problem_statement",
            ""
        )


        if problem:

            story.append(

                create_card(
                    "Problem Statement",
                    safe_text(problem)
                )

            )

            story.append(
                space(18)
            )



        # =====================================================
        # SOLUTION
        # =====================================================

        solution = roadmap.get(
            "solution",
            ""
        )


        if solution:

            story.append(

                create_card(
                    "Proposed Solution",
                    safe_text(solution)
                )

            )

            story.append(
                space(18)
            )



        # =====================================================
        # TARGET USERS
        # =====================================================

        if users:


            if isinstance(users, list):

                user_text = "<br/>".join(

                    [
                        f"✓ {safe_text(user)}"
                        for user in users
                    ]

                )

            else:

                user_text = safe_text(str(users))



            story.append(

                create_card(
                    "Target Users",
                    user_text
                )

            )


            story.append(
                space(18)
            )



        # =====================================================
        # CORE FEATURES
        # =====================================================

        if features:


            feature_text = "<br/>".join(

                [
                    f"✓ {safe_text(feature)}"
                    for feature in features
                ]

            )


            story.append(

                create_card(
                    "Core Product Features",
                    feature_text
                )

            )


            story.append(
                space(20)
            )



        # =====================================================
        # TECHNOLOGY STACK
        # =====================================================

        tech = roadmap.get(
            "tech_stack",
            {}
        )


        technologies = []


        if isinstance(tech, dict):

            for category, values in tech.items():

                if isinstance(values, list):

                    technologies.extend(values)



        if technologies:


            story.append(

                subsection(
                    "Technology Ecosystem"
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
                    "System Architecture",
                    safe_text(architecture)
                )

            )


            story.append(
                space(20)
            )



        # =====================================================
        # DEVELOPMENT ROADMAP
        # =====================================================

        if timeline:

            for phase in timeline:


                if not isinstance(phase, dict):

                    continue



                phase_name = phase.get(
                    "phase",
                    ""
                )


                tasks = phase.get(
                    "tasks",
                    []
                )


                if not phase_name and not tasks:

                    continue



                task_text = "<br/>".join(

                    [
                        f"→ {safe_text(task)}"
                        for task in tasks
                    ]

                )


                story.append(

                    create_card(
                        phase_name or "Development Phase",
                        task_text
                    )

                )

                story.append(
                    space(14)
                )



        # =====================================================
        # TEAM STRUCTURE
        # =====================================================

        roles = roadmap.get(
            "team_roles",
            []
        )


        if roles:


            story.append(

                subsection(
                    "Recommended Team Structure"
                )

            )


            for role in roles:


                if not isinstance(role, dict):

                    continue



                name = role.get(
                    "role",
                    ""
                )


                responsibility = role.get(
                    "responsibilities",
                    ""
                )


                if name or responsibility:


                    story.append(

                        create_card(
                            name or "Team Member",
                            safe_text(responsibility)
                        )

                    )


                    story.append(
                        space(12)
                    )



        # =====================================================
        # FUTURE SCOPE
        # =====================================================

        future = roadmap.get(
            "future_scope",
            ""
        )


        if future:


            story.append(

                create_card(
                    "Future Expansion Opportunities",
                    safe_text(future)
                )

            )



        story.append(
            space(30)
        )


        return story



planner_section = PlannerSection()