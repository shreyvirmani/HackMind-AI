from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch


# ==========================================================
# BASE STYLES
# ==========================================================

styles = getSampleStyleSheet()


# ==========================================================
# HACKMIND BRAND COLORS
# Frontend equivalent:
# from-cyan-500 to-blue-600
# ==========================================================


CYAN = colors.HexColor("#06B6D4")

BLUE = colors.HexColor("#2563EB")

BLUE_DARK = colors.HexColor("#1E40AF")

NAVY = colors.HexColor("#0F172A")

SLATE = colors.HexColor("#334155")


PRIMARY = BLUE

PRIMARY_DARK = NAVY

PRIMARY_LIGHT = colors.HexColor("#E0F2FE")


ACCENT = CYAN


SUCCESS = colors.HexColor("#22C55E")

WARNING = colors.HexColor("#F59E0B")

DANGER = colors.HexColor("#EF4444")


BACKGROUND = colors.HexColor("#F8FAFC")

CARD_BG = colors.white

CARD_ALT = colors.HexColor("#F1F5F9")


TEXT = colors.HexColor("#0F172A")

TEXT_LIGHT = colors.HexColor("#64748B")


BORDER = colors.HexColor("#CBD5E1")

DIVIDER = colors.HexColor("#94A3B8")



# ==========================================================
# PAGE
# ==========================================================

PAGE_MARGIN = 0.55 * inch



# ==========================================================
# COVER
# ==========================================================


COVER_TITLE = ParagraphStyle(

    "CoverTitle",

    parent=styles["Title"],

    fontName="Helvetica-Bold",

    fontSize=38,

    leading=46,

    alignment=TA_CENTER,

    textColor=BLUE,

    spaceAfter=14,

)



COVER_SUBTITLE = ParagraphStyle(

    "CoverSubtitle",

    parent=styles["BodyText"],

    fontName="Helvetica",

    fontSize=15,

    leading=22,

    alignment=TA_CENTER,

    textColor=TEXT_LIGHT,

)



# ==========================================================
# HEADINGS
# ==========================================================


SECTION_TITLE = ParagraphStyle(

    "SectionTitle",

    parent=styles["Heading1"],

    fontName="Helvetica-Bold",

    fontSize=23,

    leading=30,

    textColor=NAVY,

    spaceBefore=18,

    spaceAfter=14,

)



SUBSECTION_TITLE = ParagraphStyle(

    "SubSectionTitle",

    parent=styles["Heading2"],

    fontName="Helvetica-Bold",

    fontSize=16,

    leading=22,

    textColor=BLUE,

    spaceBefore=12,

    spaceAfter=8,

)



CARD_TITLE = ParagraphStyle(

    "CardTitle",

    parent=styles["Heading3"],

    fontName="Helvetica-Bold",

    fontSize=13,

    leading=17,

    textColor=BLUE_DARK,

)

# ==========================================================
# PREMIUM COVER HERO
# ==========================================================

PREMIUM_HERO = ParagraphStyle(

    "PremiumHero",

    parent=styles["Heading1"],

    fontName="Helvetica-Bold",

    fontSize=24,

    leading=32,

    alignment=TA_CENTER,

    textColor=BLUE_DARK,

    spaceAfter=10,

)



# ==========================================================
# BODY
# ==========================================================


BODY = ParagraphStyle(

    "Body",

    parent=styles["BodyText"],

    fontName="Helvetica",

    fontSize=10.5,

    leading=18,

    textColor=TEXT,

    spaceAfter=8,

)



BODY_CENTER = ParagraphStyle(

    "BodyCenter",

    parent=BODY,

    alignment=TA_CENTER,

)



BODY_RIGHT = ParagraphStyle(

    "BodyRight",

    parent=BODY,

    alignment=TA_RIGHT,

)



MUTED = ParagraphStyle(

    "Muted",

    parent=BODY,

    fontSize=9,

    leading=13,

    textColor=TEXT_LIGHT,

)



SMALL = ParagraphStyle(

    "Small",

    parent=BODY,

    fontSize=8,

    leading=12,

)



# ==========================================================
# BULLETS
# ==========================================================


BULLET = ParagraphStyle(

    "Bullet",

    parent=BODY,

    leftIndent=20,

    bulletIndent=10,

    spaceAfter=5,

)



# ==========================================================
# METRICS
# ==========================================================


METRIC_VALUE = ParagraphStyle(

    "MetricValue",

    parent=styles["Heading1"],

    alignment=TA_CENTER,

    fontName="Helvetica-Bold",

    fontSize=28,

    leading=32,

    textColor=CYAN,

)



METRIC_LABEL = ParagraphStyle(

    "MetricLabel",

    parent=BODY_CENTER,

    fontSize=10,

    textColor=TEXT_LIGHT,

)



# ==========================================================
# TABLE
# ==========================================================


TABLE_HEADER = ParagraphStyle(

    "TableHeader",

    parent=BODY,

    fontName="Helvetica-Bold",

    fontSize=10,

    textColor=colors.white,

    alignment=TA_CENTER,

)



TABLE_CELL = ParagraphStyle(

    "TableCell",

    parent=BODY,

    fontSize=9,

)



# ==========================================================
# FOOTER
# ==========================================================


FOOTER = ParagraphStyle(

    "Footer",

    parent=BODY,

    alignment=TA_CENTER,

    fontSize=8,

    textColor=TEXT_LIGHT,

)



# ==========================================================
# CODE BLOCK
# ==========================================================


CODE = ParagraphStyle(

    "Code",

    parent=BODY,

    fontName="Courier",

    fontSize=8,

    leading=11,

    backColor=colors.HexColor("#F1F5F9"),

    borderPadding=8,

)



# ==========================================================
# EXPORT DICTIONARY
# ==========================================================


REPORT_STYLES = {


    "cover_title": COVER_TITLE,

    "cover_subtitle": COVER_SUBTITLE,


    "section_title": SECTION_TITLE,

    "subsection_title": SUBSECTION_TITLE,

    "premium_hero": PREMIUM_HERO,
    
    "card_title": CARD_TITLE,


    "body": BODY,

    "body_center": BODY_CENTER,

    "body_right": BODY_RIGHT,


    "muted": MUTED,

    "small": SMALL,


    "bullet": BULLET,


    "metric_value": METRIC_VALUE,

    "metric_label": METRIC_LABEL,


    "table_header": TABLE_HEADER,

    "table_cell": TABLE_CELL,


    "footer": FOOTER,


    "code": CODE,

}



# ==========================================================
# OLD COMPATIBILITY NAMES
# ==========================================================


REPORT_STYLES.update({

    "Title": COVER_TITLE,

    "Body": BODY,

    "SectionTitle": SECTION_TITLE,

    "SubTitle": SUBSECTION_TITLE,

    "CardTitle": CARD_TITLE,

    "CardValue": METRIC_VALUE,

    "Muted": MUTED,

    "BulletBody": BULLET,

    "CodeBlock": CODE,

})