def build_prompt(
    project,
    message: str,
) -> str:

    question = message.lower()

    context = []

    # Always include the basics
    context.append(
        f"""
Project Title:
{project.project_title}

Idea:
{project.idea}
"""
    )

    # ---------- Roadmap ----------
    if any(
        word in question
        for word in [
            "roadmap",
            "feature",
            "timeline",
            "development",
            "architecture",
            "tech stack",
            "implementation",
        ]
    ):

        context.append(
            f"""
Roadmap

{project.roadmap}
"""
        )

    # ---------- Research ----------
    if any(
        word in question
        for word in [
            "research",
            "market",
            "competitor",
            "customer",
            "industry",
            "problem",
        ]
    ):

        context.append(
            f"""
Research

{project.research}
"""
        )

    # ---------- Judge ----------
    if any(
        word in question
        for word in [
            "judge",
            "score",
            "hackathon",
            "improve",
            "weakness",
            "feedback",
        ]
    ):

        context.append(
            f"""
Judge Evaluation

{project.judge}
"""
        )

    # ---------- Pitch ----------
    if any(
        word in question
        for word in [
            "pitch",
            "investor",
            "startup",
            "business",
            "funding",
            "revenue",
            "monetization",
        ]
    ):

        context.append(
            f"""
Pitch Deck

{project.pitch_deck}
"""
        )

    # If nothing matched, include everything
    if len(context) == 1:

        context.extend(
            [
                f"\nRoadmap\n{project.roadmap}",
                f"\nResearch\n{project.research}",
                f"\nJudge\n{project.judge}",
                f"\nPitch\n{project.pitch_deck}",
            ]
        )

    return f"""
You are HackMind AI Copilot.

You are an expert startup mentor, hackathon mentor and software architect.

Use the project information below to answer the user's question.

{' '.join(context)}

User Question:

{message}

Rules:

- Give practical advice.
- Be concise.
- Use bullet points when helpful.
- Never invent project information.
- Base your answer on the provided context.
"""