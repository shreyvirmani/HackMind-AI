from io import BytesIO

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
)

from src.models.roadmap import Roadmap
from src.templates.pdf_styles import (
    TITLE_STYLE,
    HEADING_STYLE,
    BODY_STYLE,
)

def export_pdf(roadmap: Roadmap):

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    story = []

    story.append(
        Paragraph(
            "🚀 HackMind AI",
            TITLE_STYLE,
        )
    )

    story.append(
        Spacer(1, 12)
    )

    story.append(
        Paragraph(
            "AI-Powered Hackathon Project Planner",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(1, 24)
    )

    story.append(
        Paragraph(
            "<b>PROJECT</b>",
            HEADING_STYLE,
        )
    )

    story.append(
        Paragraph(
            roadmap.project_title,
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(1, 18)
    )
    
    story.append(
        Paragraph(
            "<b>Problem Statement</b>",
            HEADING_STYLE,
        )
    )

    story.append(
        Paragraph(
            roadmap.problem_statement,
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(1, 18)
    )

    story.append(
        Paragraph(
            "<b>Solution</b>",
            HEADING_STYLE,
        )
    )

    story.append(
        Paragraph(
            roadmap.solution,
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(1, 18)
    )

    story.append(
        Paragraph(
            "<b>Key Features</b>",
            HEADING_STYLE,
        )
    )

    for feature in roadmap.key_features:

        story.append(
            Paragraph(
                f"• {feature}",
                BODY_STYLE,
            )
        )

    story.append(
        Spacer(1, 18)
    )

    doc.build(story)

    buffer.seek(0)

    return buffer