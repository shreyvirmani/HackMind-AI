from pathlib import Path

from reportlab.platypus import (
    SimpleDocTemplate,
    PageBreak,
)

from reportlab.lib.pagesizes import A4

from src.pdf.styles import PAGE_MARGIN

from src.pdf.sections.cover import (
    build_cover_section,
)

from src.pdf.sections.executive_summary import (
    build_executive_summary,
)

from src.pdf.sections.planner import (
    planner_section,
)

from src.pdf.sections.research import (
    research_section,
)

from src.pdf.sections.architecture import (
    architecture_section,
)

from src.pdf.sections.judge import (
    judge_section,
)

from src.pdf.sections.pitch import (
    pitch_deck_section,
)

from src.pdf.sections.appendix import (
    appendix_section,
)


# ======================================================
# PAGE FOOTER
# ======================================================

def add_page_number(canvas, doc):

    canvas.saveState()

    width, height = A4

    canvas.setFont(
        "Helvetica",
        8
    )

    canvas.drawCentredString(
        width / 2,
        22,
        f"HackMind AI Copilot  •  Page {doc.page}"
    )

    canvas.restoreState()


# ======================================================
# PDF GENERATOR
# ======================================================

class PDFGenerator:

    def __init__(self):

        self.output_dir = Path(
            "generated_reports"
        )

        self.output_dir.mkdir(
            exist_ok=True
        )


    def generate(
        self,
        project
    ):

        # ==================================================
        # SAFE PROJECT TITLE
        # ==================================================
        #
        # Prevent an accidentally huge project title from
        # becoming an oversized ReportLab flowable.
        #
        # Normal project titles are left untouched.
        # Extremely long titles are truncated only for the
        # PDF filename/title.
        # ==================================================

        raw_title = str(
            getattr(
                project,
                "project_title",
                "HackMind AI Project"
            )
            or "HackMind AI Project"
        )

        safe_title = raw_title.strip()

        if not safe_title:
            safe_title = "HackMind AI Project"

        # Keep the PDF metadata/title reasonable.
        pdf_title = safe_title[:300]

        # Keep filesystem filename reasonable.
        filename_title = safe_title[:150]

        filename = (
            filename_title
            .replace(" ", "_")
            + "_Startup_Intelligence_Report.pdf"
        )

        output_path = (
            self.output_dir
            / filename
        )


        # ==================================================
        # DOCUMENT
        # ==================================================

        doc = SimpleDocTemplate(

            str(output_path),

            pagesize=A4,

            leftMargin=PAGE_MARGIN,

            rightMargin=PAGE_MARGIN,

            topMargin=PAGE_MARGIN,

            bottomMargin=PAGE_MARGIN,

            title=pdf_title,

            author="HackMind AI Copilot",

            subject=(
                "AI Generated Startup Intelligence Report"
            )

        )


        story = []


        # ==================================================
        # PREMIUM COVER
        # ==================================================

        story.extend(

            build_cover_section(
                project
            )

        )


        story.append(
            PageBreak()
        )


        # ==================================================
        # CONTENT SECTIONS
        # ==================================================

        sections = [

            # ----------------------------------------------
            # Executive Summary
            # ----------------------------------------------

            build_executive_summary(
                project
            ),


            # ----------------------------------------------
            # Planner / Roadmap
            # ----------------------------------------------

            planner_section.build(

                project.roadmap
                if project.roadmap
                else {}

            ),


            # ----------------------------------------------
            # Research
            # ----------------------------------------------

            research_section.build(

                project.research
                if project.research
                else {}

            ),


            # ----------------------------------------------
            # Architecture
            # ----------------------------------------------

            architecture_section.build(

                project.architecture
                if project.architecture
                else {}

            ),


            # ----------------------------------------------
            # Judge / Evaluation
            # ----------------------------------------------

            judge_section.build(

                project.judge
                if project.judge
                else {}

            ),


            # ----------------------------------------------
            # Pitch Deck
            # ----------------------------------------------

            pitch_deck_section.build(

                project.pitch_deck
                if project.pitch_deck
                else {}

            ),


            # ----------------------------------------------
            # Appendix
            # ----------------------------------------------

            appendix_section.build(
                project
            ),

        ]


        # ==================================================
        # ADD SECTIONS
        # ==================================================

        for section in sections:

            if section:

                story.extend(
                    section
                )


        # ==================================================
        # BUILD
        # ==================================================

        doc.build(

            story,

            onFirstPage=add_page_number,

            onLaterPages=add_page_number

        )


        return output_path


# ======================================================
# SINGLE GENERATOR INSTANCE
# ======================================================

pdf_generator = PDFGenerator()
