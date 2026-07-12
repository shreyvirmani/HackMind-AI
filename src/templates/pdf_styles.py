from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import HexColor

styles = getSampleStyleSheet()

TITLE_STYLE = styles["Title"]
TITLE_STYLE.alignment = TA_CENTER
TITLE_STYLE.textColor = HexColor("#2563EB")
TITLE_STYLE.spaceAfter = 20

HEADING_STYLE = styles["Heading2"]
HEADING_STYLE.textColor = HexColor("#111827")
HEADING_STYLE.spaceBefore = 16
HEADING_STYLE.spaceAfter = 10

BODY_STYLE = styles["BodyText"]
BODY_STYLE.leading = 20
BODY_STYLE.spaceAfter = 8