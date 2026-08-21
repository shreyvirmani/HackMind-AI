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


    def generate(self, project):

        filename = (
            str(project.project_title)
            .replace(" ", "_")
            + "_Startup_Intelligence_Report.pdf"
        )

        output_path = (
            self.output_dir
            / filename
        )


        doc = SimpleDocTemplate(

            str(output_path),

            pagesize=A4,

            leftMargin=PAGE_MARGIN,
            rightMargin=PAGE_MARGIN,
            topMargin=PAGE_MARGIN,
            bottomMargin=PAGE_MARGIN,

            title=str(project.project_title),

            author="HackMind AI Copilot",

            subject=(
                "AI Generated Startup Intelligence Report"
            )
        )


        story = []


        # ==================================================
        # COVER
        # ==================================================

        cover = build_cover_section(project)

        if cover:
            story.extend(cover)


        # ==================================================
        # TEMPORARY TEST MODE
        # ==================================================
        #
        # ALL CONTENT SECTIONS ARE DISABLED.
        #
        # This is intentional.
        #
        # The current backend is producing:
        #
        # Table
        #   -> 1 row
        #   -> 1 column
        #   -> 2502pt tall cell
        #
        # containing AI-generated text beginning with:
        #
        # "Build a production-ready SIH Team Matcher..."
        #
        # ReportLab cannot split that table cell across pages.
        #
        # Once this generates successfully, we will identify
        # the exact section responsible and fix it properly.
        #
        # ==================================================


        # No executive summary
        # No planner
        # No research
        # No architecture
        # No judge
        # No pitch
        # No appendix


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
# GENERATOR INSTANCE
# ======================================================

pdf_generator = PDFGenerator()
