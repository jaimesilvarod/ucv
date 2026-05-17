import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px
from datetime import datetime, timezone
import hashlib
import uuid
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as RLImage,
    PageBreak,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import qrcode


AURORA_VERSION = "1.2.0"
AUTHOR_WEB = "jaimesilva.co"

# IMPORTANTE: cambia esto por la URL real pública de tu app Streamlit.
VERIFY_BASE_URL = "https://ucv-monitor.streamlit.app"

AURORA_DARK = "#0B1220"
AURORA_PRIMARY = "#4F46E5"
AURORA_CYAN = "#06B6D4"
AURORA_GREEN = "#10B981"
AURORA_RED = "#EF4444"
AURORA_AMBER = "#F59E0B"
AURORA_MUTED = "#64748B"

ASSETS_DIR = Path("assets")
ASSETS_DIR.mkdir(exist_ok=True)

FONT_DIR = ASSETS_DIR / "fonts"
FONT_DIR.mkdir(exist_ok=True)

AURORA_ICON_PATH = ASSETS_DIR / "aurora-icon.png"
APTOS_FONT_PATH = FONT_DIR / "Aptos.ttf"
APTOS_BOLD_FONT_PATH = FONT_DIR / "Aptos-Bold.ttf"


def ensure_aurora_assets():
    if AURORA_ICON_PATH.exists():
        return

    size = 512
    scale = size / 256

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    for i in range(size):
        r = int(79 + (6 - 79) * i / size)
        g = int(70 + (182 - 70) * i / size)
        b = int(229 + (212 - 229) * i / size)
        draw.line([(i, 0), (i, size)], fill=(r, g, b, 255))

    pad = int(18 * scale)
    radius = int(58 * scale)
    draw.rounded_rectangle(
        (pad, pad, size - pad, size - pad),
        radius=radius,
        outline=(255, 255, 255, 95),
        width=int(3 * scale),
    )

    draw.arc(
        (
            int(62 * scale),
            int(80 * scale),
            int(194 * scale),
            int(198 * scale),
        ),
        start=205,
        end=335,
        fill=(255, 255, 255, 255),
        width=int(18 * scale),
    )
    draw.ellipse(
        (
            int(112 * scale),
            int(112 * scale),
            int(144 * scale),
            int(144 * scale),
        ),
        fill=(255, 255, 255, 255),
    )

    img.save(AURORA_ICON_PATH)


ensure_aurora_assets()


def register_pdf_fonts():
    if APTOS_FONT_PATH.exists():
        pdfmetrics.registerFont(TTFont("Aptos", str(APTOS_FONT_PATH)))
        base = "Aptos"
    else:
        base = "Helvetica"

    if APTOS_BOLD_FONT_PATH.exists():
        pdfmetrics.registerFont(TTFont("Aptos-Bold", str(APTOS_BOLD_FONT_PATH)))
        bold = "Aptos-Bold"
    else:
        bold = "Helvetica-Bold"

    return base, bold


PDF_FONT, PDF_FONT_BOLD = register_pdf_fonts()


st.set_page_config(
    page_title="Aurora",
    page_icon=str(AURORA_ICON_PATH),
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={},
)

st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at 8% 14%, rgba(79,70,229,.22), transparent 24%),
        radial-gradient(circle at 30% 8%, rgba(6,182,212,.16), transparent 28%),
        radial-gradient(circle at 74% 6%, rgba(16,185,129,.19), transparent 30%),
        radial-gradient(circle at 88% 36%, rgba(34,211,238,.12), transparent 28%),
        radial-gradient(circle at 52% 88%, rgba(139,92,246,.13), transparent 32%),
        linear-gradient(180deg, #F8FBFF 0%, #EEF4FF 48%, #F7F9FF 100%);
    color: #0F172A;
    margin-top: 0rem !important;
}

section[data-testid="stSidebar"] { display:none !important; }

.block-container {
    max-width: 100% !important;
    padding: 1.2rem 4rem 5rem 4rem !important;
}

html, body, [class*="css"] {
    font-family: Inter, ui-sans-serif, system-ui, sans-serif;
}

header[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] {
    display: none !important;
}

#MainMenu { visibility: hidden !important; }
footer { visibility: hidden !important; }

.topbar{
    display:flex !important;
    align-items:center !important;
    justify-content:space-between !important;
    margin-bottom:.4rem !important;
}

.brand-wrap {
    display:flex;
    align-items:center;
    gap:14px;
    flex-wrap:wrap;
}

.brand-logo svg {
    filter: drop-shadow(0 0 18px rgba(79,70,229,.28))
            drop-shadow(0 0 32px rgba(6,182,212,.16));
}

.brand-text {
    font-size:2rem;
    font-weight:950;
    letter-spacing:-.07em;
    color:#0F172A;
}

.brand-badge {
    padding:7px 13px;
    border-radius:999px;
    background:rgba(79,70,229,.10);
    color:#4F46E5;
    font-size:.72rem;
    font-weight:850;
    letter-spacing:.08em;
}

.standards-badge {
    display:inline-flex;
    align-items:center;
    padding:8px 14px;
    border-radius:999px;
    background:rgba(255,255,255,.50);
    border:1px solid rgba(255,255,255,.62);
    box-shadow:0 10px 30px rgba(15,23,42,.04);
    font-size:.74rem;
    font-weight:850;
    color:#64748B;
    backdrop-filter:blur(18px);
}

div[data-testid="stSegmentedControl"] {
    max-width: 620px !important;
    margin: 14px 0 18px 0 !important;
}

div[data-testid="stSegmentedControl"] > div {
    display: flex !important;
    width: fit-content !important;
    gap: 6px !important;
    padding: 6px !important;
    border-radius: 18px !important;
    background: rgba(255,255,255,.54) !important;
    border: 1px solid rgba(255,255,255,.68) !important;
    box-shadow:
        0 12px 36px rgba(15,23,42,.045),
        inset 0 1px 0 rgba(255,255,255,.58) !important;
    backdrop-filter: blur(22px) !important;
}

div[data-testid="stSegmentedControl"] label > div {
    border-radius: 13px !important;
    min-height: 38px !important;
    padding: 0 16px !important;
    font-size: .82rem !important;
    font-weight: 850 !important;
    color: #475569 !important;
    transition: all .18s ease !important;
}

div[data-testid="stSegmentedControl"] label[aria-checked="true"] > div,
div[data-testid="stSegmentedControl"] label[data-baseweb="radio"]:has(input:checked) > div {
    background: linear-gradient(135deg,#4F46E5,#06B6D4,#10B981) !important;
    color: white !important;
    box-shadow: 0 12px 28px rgba(79,70,229,.22) !important;
}

div[data-baseweb="select"] > div {
    min-height: 44px !important;
    border-radius: 16px !important;
    background: rgba(255,255,255,.72) !important;
    border: 1px solid rgba(255,255,255,.70) !important;
    box-shadow: 0 10px 28px rgba(15,23,42,.04) !important;
}

button[kind="primary"],
button[kind="secondary"],
.stDownloadButton button,
.stButton button {
    min-height: 44px !important;
    border-radius:999px !important;
    background:linear-gradient(135deg,#4F46E5,#06B6D4) !important;
    color:white !important;
    border:0 !important;
    box-shadow:0 12px 30px rgba(79,70,229,.20) !important;
    font-weight:850 !important;
    padding: 0 22px !important;
}

.section-title{
    margin-top:12px !important;
    margin-bottom:4px !important;
    font-size:1.48rem !important;
    font-weight:950 !important;
    letter-spacing:-.05em !important;
}

.section-subtitle{
    margin-bottom:10px !important;
    font-size:.92rem !important;
    color:#64748B !important;
}

.metric-compact-grid {
    display:grid;
    grid-template-columns: repeat(4, minmax(180px, 1fr));
    gap:14px;
    margin:16px 0 24px 0;
}

.metric-compact {
    padding:16px 18px;
    border-radius:22px;
    background:rgba(255,255,255,.38);
    border:1px solid rgba(255,255,255,.62);
    backdrop-filter:blur(24px) saturate(112%);
    -webkit-backdrop-filter:blur(24px) saturate(112%);
    box-shadow:
        0 14px 38px rgba(15,23,42,.04),
        inset 0 1px 0 rgba(255,255,255,.62);
}

.metric-compact-label {
    font-size:.72rem;
    font-weight:900;
    color:#64748B;
    letter-spacing:.06em;
    text-transform:uppercase;
}

.metric-compact-value {
    margin-top:8px;
    font-size:1.8rem;
    font-weight:950;
    letter-spacing:-.05em;
    color:#0F172A;
}

.metric-compact-note {
    margin-top:6px;
    font-size:.78rem;
    color:#64748B;
    line-height:1.35;
}

[data-testid="stDataFrame"] {
    border-radius:24px;
    overflow:hidden;
    border:1px solid rgba(15,23,42,.06);
    box-shadow:0 18px 55px rgba(15,23,42,.05);
    background:rgba(255,255,255,.70);
}

.js-plotly-plot,
.plot-container,
svg.main-svg {
    background:transparent !important;
    border:none !important;
    box-shadow:none !important;
}

.export-panel {
    padding:10px 12px;
    border-radius:20px;
    background:rgba(255,255,255,.42);
    border:1px solid rgba(255,255,255,.62);
    box-shadow:0 14px 38px rgba(15,23,42,.04);
    backdrop-filter:blur(22px);
    margin-top:6px;
}

.hash-caption {
    margin-top:6px;
    font-size:.70rem;
    color:#64748B;
    word-break:break-all;
}

.verify-card {
    padding: 22px;
    border-radius: 24px;
    background: rgba(255,255,255,.58);
    border: 1px solid rgba(255,255,255,.68);
    box-shadow: 0 20px 60px rgba(15,23,42,.06);
    backdrop-filter: blur(22px);
}

@media (max-width: 1100px) {
    .block-container {
        padding: 1rem 1.3rem 5rem 1.3rem !important;
    }

    .metric-compact-grid {
        grid-template-columns: repeat(2, minmax(180px, 1fr));
    }
}

@media (max-width: 700px) {
    .metric-compact-grid {
        grid-template-columns: 1fr;
    }

    div[data-testid="stSegmentedControl"] > div {
        width: 100% !important;
        flex-wrap: wrap !important;
    }
}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


def dataframe_sha256(df_in: pd.DataFrame) -> str:
    df_hash = df_in.copy()
    for col in ["timestamp", "url"]:
        if col not in df_hash.columns:
            df_hash[col] = ""

    payload = (
        df_hash.sort_values(by=["timestamp", "url"], ascending=[True, True])
        .astype(str)
        .to_csv(index=False)
        .encode("utf-8")
    )
    return hashlib.sha256(payload).hexdigest()


def bytes_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def short_hash(value: str, groups: int = 6) -> str:
    clean = str(value).upper()
    return "-".join(clean[i:i + 4] for i in range(0, min(len(clean), groups * 4), 4))


def estado_servicio(uptime, fallos, latencia):
    if uptime >= 99 and fallos == 0 and latencia < 1000:
        return "OPERATIVO"
    if uptime >= 95 and latencia < 3000:
        return "DEGRADADO"
    return "CRITICO"


def estado_global_operacion(uptime, total_fallos, latencia):
    if uptime >= 99 and total_fallos == 0 and latencia < 1000:
        return "OPERATIONAL", AURORA_GREEN
    if uptime >= 95 and latencia < 3000:
        return "DEGRADED", AURORA_AMBER
    return "CRITICAL", AURORA_RED


def classify_latency(ms: float) -> str:
    if ms < 1000:
        return "Sana"
    if ms < 3000:
        return "Degradada"
    return "Crítica"


def short_url(url: str, max_len: int = 62) -> str:
    if not isinstance(url, str):
        return ""
    cleaned = url.replace("https://", "").replace("http://", "")
    return cleaned if len(cleaned) <= max_len else cleaned[:max_len] + "..."


def make_qr_png(data: str) -> str:
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0B1220", back_color="white").convert("RGB")
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(tmp.name)
    return tmp.name


def p(text, style):
    return Paragraph(str(text), style)


def build_pdf_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="AuroraTitle",
        fontName=PDF_FONT_BOLD,
        fontSize=22,
        leading=26,
        textColor=colors.HexColor(AURORA_DARK),
        spaceAfter=8,
    ))

    styles.add(ParagraphStyle(
        name="AuroraH2",
        fontName=PDF_FONT_BOLD,
        fontSize=11,
        leading=14,
        textColor=colors.HexColor(AURORA_DARK),
        spaceBefore=6,
        spaceAfter=5,
    ))

    styles.add(ParagraphStyle(
        name="AuroraBody",
        fontName=PDF_FONT,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6,
    ))

    styles.add(ParagraphStyle(
        name="AuroraSmall",
        fontName=PDF_FONT,
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor(AURORA_MUTED),
    ))

    styles.add(ParagraphStyle(
        name="AuroraKpiLabel",
        fontName=PDF_FONT_BOLD,
        fontSize=7,
        leading=9,
        textColor=colors.HexColor(AURORA_MUTED),
        alignment=TA_LEFT,
    ))

    styles.add(ParagraphStyle(
        name="AuroraKpiValue",
        fontName=PDF_FONT_BOLD,
        fontSize=17,
        leading=20,
        textColor=colors.HexColor(AURORA_DARK),
        alignment=TA_LEFT,
    ))

    styles.add(ParagraphStyle(
        name="AuroraWhite",
        fontName=PDF_FONT_BOLD,
        fontSize=12,
        leading=15,
        textColor=colors.white,
    ))

    styles.add(ParagraphStyle(
        name="AuroraWhiteSmall",
        fontName=PDF_FONT,
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#CBD5E1"),
    ))

    styles.add(ParagraphStyle(
        name="CenterSmall",
        fontName=PDF_FONT,
        fontSize=7,
        leading=9,
        textColor=colors.HexColor(AURORA_MUTED),
        alignment=TA_CENTER,
    ))

    return styles


def draw_pdf_header_footer(canvas, doc, report_id, generated_utc):
    canvas.saveState()

    width, height = A4

    canvas.setFillColor(colors.HexColor(AURORA_DARK))
    canvas.rect(0, height - 24 * mm, width, 24 * mm, fill=1, stroke=0)

    canvas.drawImage(
        str(AURORA_ICON_PATH),
        14 * mm,
        height - 18 * mm,
        10 * mm,
        10 * mm,
        mask="auto",
        preserveAspectRatio=True,
        anchor="c",
    )

    canvas.setFillColor(colors.white)
    canvas.setFont(PDF_FONT_BOLD, 10)
    canvas.drawString(29 * mm, height - 12 * mm, "Aurora")

    canvas.setFont(PDF_FONT, 7)
    canvas.setFillColor(colors.HexColor("#CBD5E1"))
    canvas.drawString(29 * mm, height - 16 * mm, "Operational Evidence Report")

    canvas.setStrokeColor(colors.HexColor(AURORA_PRIMARY))
    canvas.setLineWidth(1.2)
    canvas.line(14 * mm, height - 22 * mm, width - 14 * mm, height - 22 * mm)

    canvas.setFont(PDF_FONT, 6.5)
    canvas.setFillColor(colors.HexColor("#94A3B8"))
    canvas.drawRightString(width - 14 * mm, height - 12 * mm, report_id)
    canvas.drawRightString(width - 14 * mm, height - 16 * mm, generated_utc)

    canvas.setStrokeColor(colors.HexColor("#E2E8F0"))
    canvas.setLineWidth(0.5)
    canvas.line(14 * mm, 15 * mm, width - 14 * mm, 15 * mm)

    canvas.setFont(PDF_FONT, 6.5)
    canvas.setFillColor(colors.HexColor("#64748B"))
    canvas.drawString(
        14 * mm,
        10 * mm,
        "Aurora Observability Platform · Technical Evidence Report · Integrity Protected",
    )
    canvas.drawRightString(width - 14 * mm, 10 * mm, f"Page {doc.page}")

    canvas.restoreState()


def kpi_card(label, value, note, styles):
    content = [
        [p(label.upper(), styles["AuroraKpiLabel"])],
        [p(value, styles["AuroraKpiValue"])],
        [p(note, styles["AuroraSmall"])],
    ]
    table = Table(content, colWidths=[40 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#E2E8F0")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return table


def section_band(title, styles):
    table = Table([[p(title, styles["AuroraWhite"])]], colWidths=[182 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(AURORA_DARK)),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return table


def preparar_df_operacion(df_operacion: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    df_pdf = df_operacion.copy()

    for col in [
        "timestamp",
        "url",
        "http_code",
        "latency_ms",
        "error_type",
        "screenshot_url",
        "content_hash",
        "ssl_issuer",
        "ssl_expiry",
    ]:
        if col not in df_pdf.columns:
            df_pdf[col] = None

    df_pdf["is_fail"] = (
        (df_pdf["http_code"] >= 400)
        | (df_pdf["http_code"].isna())
        | (df_pdf["error_type"].fillna("OK") != "OK")
    )

    total_checks = len(df_pdf)
    df_fallos = df_pdf[df_pdf["is_fail"]].copy()
    total_fallos = len(df_fallos)
    uptime = 100.0 if total_checks == 0 else ((total_checks - total_fallos) / total_checks) * 100
    avg_latency = float(df_pdf["latency_ms"].mean()) if total_checks else 0.0

    df_servicios = (
        df_pdf.groupby("url")
        .agg(
            muestras=("url", "count"),
            fallos=("is_fail", "sum"),
            latencia_promedio=("latency_ms", "mean"),
            latencia_maxima=("latency_ms", "max"),
            evidencia=("screenshot_url", lambda x: x.notna().sum()),
        )
        .reset_index()
    )

    df_servicios["uptime"] = ((df_servicios["muestras"] - df_servicios["fallos"]) / df_servicios["muestras"]) * 100
    df_servicios["health_score"] = (
        df_servicios["uptime"] * 0.7
        + (100 - (df_servicios["latencia_promedio"].clip(0, 5000) / 5000 * 100)) * 0.3
    ).clip(0, 100)

    df_servicios["estado"] = df_servicios.apply(
        lambda r: estado_servicio(r["uptime"], r["fallos"], r["latencia_promedio"]),
        axis=1,
    )

    metrics = {
        "total_checks": int(total_checks),
        "total_failures": int(total_fallos),
        "uptime": float(uptime),
        "avg_latency_ms": float(avg_latency),
        "window_start": df_pdf["timestamp"].min(),
        "window_end": df_pdf["timestamp"].max(),
    }

    return df_pdf, df_servicios, metrics


def generar_pdf_bytes(
    df_operacion,
    report_id: str,
    generated_utc: datetime,
    source_hash: str,
    verify_url: str,
):
    df_pdf, df_servicios_pdf, metrics = preparar_df_operacion(df_operacion)

    generated_utc_label = generated_utc.strftime("%Y-%m-%d %H:%M:%S UTC")
    qr_path = make_qr_png(verify_url)

    uptime = metrics["uptime"]
    total_checks = metrics["total_checks"]
    total_fallos = metrics["total_failures"]
    latencia_promedio = metrics["avg_latency_ms"]
    ventana_inicio = metrics["window_start"]
    ventana_fin = metrics["window_end"]

    df_fallos = df_pdf[df_pdf["is_fail"]].copy()
    op_status, op_color = estado_global_operacion(uptime, total_fallos, latencia_promedio)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp.close()

    doc = SimpleDocTemplate(
        tmp.name,
        pagesize=A4,
        rightMargin=14 * mm,
        leftMargin=14 * mm,
        topMargin=34 * mm,
        bottomMargin=20 * mm,
        title=f"Aurora Technical Evidence Report {report_id}",
        author=AUTHOR_WEB,
        subject="Operational availability, latency and incident evidence report",
        creator="Aurora Observability Platform",
    )

    styles = build_pdf_styles()
    story = []

    hero = Table(
        [[
            RLImage(str(AURORA_ICON_PATH), width=18 * mm, height=18 * mm),
            [
                p("Aurora Technical Evidence Report", styles["AuroraTitle"]),
                p("Operational availability, latency, incident integrity and traceability package.", styles["AuroraBody"]),
                p(f"Developed by {AUTHOR_WEB} · Aurora v{AURORA_VERSION}", styles["AuroraSmall"]),
            ],
            [
                p("STATUS", styles["AuroraKpiLabel"]),
                p(op_status, ParagraphStyle(
                    name="StatusStyle",
                    fontName=PDF_FONT_BOLD,
                    fontSize=15,
                    leading=18,
                    textColor=colors.HexColor(op_color),
                )),
                p(f"Report ID<br/>{report_id}", styles["AuroraSmall"]),
            ],
        ]],
        colWidths=[24 * mm, 100 * mm, 58 * mm],
    )
    hero.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#E2E8F0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(hero)
    story.append(Spacer(1, 8 * mm))

    story.append(section_band("Executive Operational Summary", styles))
    story.append(Spacer(1, 4 * mm))

    summary = (
        f"Aurora observed the monitored operation between <b>{ventana_inicio}</b> and <b>{ventana_fin}</b>. "
        f"The global availability measured was <b>{uptime:.2f}%</b>, with <b>{total_fallos}</b> incidents "
        f"over <b>{total_checks}</b> technical checks. Average latency was <b>{latencia_promedio:.0f} ms</b>. "
        f"The report consolidates HTTP status, DNS/TLS failures, latency degradation, content hashes, "
        f"SSL metadata and visual evidence references where available."
    )
    story.append(p(summary, styles["AuroraBody"]))

    kpi_grid = Table(
        [[
            kpi_card("Availability", f"{uptime:.2f}%", "Global measured uptime", styles),
            kpi_card("Incidents", str(total_fallos), f"Over {total_checks} checks", styles),
            kpi_card("Avg latency", f"{latencia_promedio:.0f} ms", "Operational response time", styles),
            kpi_card("Data integrity", short_hash(source_hash, 3), "Dataset SHA-256", styles),
        ]],
        colWidths=[45.5 * mm, 45.5 * mm, 45.5 * mm, 45.5 * mm],
    )
    kpi_grid.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(Spacer(1, 4 * mm))
    story.append(kpi_grid)
    story.append(Spacer(1, 7 * mm))

    integrity_box = Table(
        [[
            [
                p("Integrity & Chain-of-Custody Snapshot", styles["AuroraH2"]),
                p(f"<b>Generated UTC:</b> {generated_utc_label}", styles["AuroraBody"]),
                p(f"<b>Source dataset SHA-256:</b> {source_hash}", styles["AuroraBody"]),
                p(f"<b>Method:</b> Automated extraction from Aurora technical vault. Full monitored operation, independent of dashboard filters.", styles["AuroraBody"]),
                p("<b>Standards alignment:</b> ISO/IEC 27037 principles for digital evidence handling and NIST SP 800-92 log management guidance.", styles["AuroraBody"]),
            ],
            [
                RLImage(qr_path, width=28 * mm, height=28 * mm),
                p("Verification endpoint", styles["CenterSmall"]),
                p(verify_url, styles["CenterSmall"]),
            ],
        ]],
        colWidths=[138 * mm, 44 * mm],
    )
    integrity_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EEF2FF")),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor(AURORA_PRIMARY)),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(integrity_box)
    story.append(PageBreak())

    story.append(section_band("Operational Service Matrix", styles))
    story.append(Spacer(1, 4 * mm))

    service_rows = [[
        p("Service", styles["AuroraWhiteSmall"]),
        p("Status", styles["AuroraWhiteSmall"]),
        p("Uptime", styles["AuroraWhiteSmall"]),
        p("Score", styles["AuroraWhiteSmall"]),
        p("Failures", styles["AuroraWhiteSmall"]),
        p("Avg Lat.", styles["AuroraWhiteSmall"]),
        p("Evidence", styles["AuroraWhiteSmall"]),
    ]]

    df_services_out = df_servicios_pdf.sort_values(
        by=["uptime", "fallos", "latencia_promedio"],
        ascending=[True, False, False],
    )

    for _, r in df_services_out.head(50).iterrows():
        service_rows.append([
            p(str(r["url"]).replace("https://", "").replace("http://", "")[:58], styles["AuroraSmall"]),
            p(str(r["estado"]), styles["AuroraSmall"]),
            p(f"{r['uptime']:.2f}%", styles["AuroraSmall"]),
            p(f"{r['health_score']:.1f}", styles["AuroraSmall"]),
            p(str(int(r["fallos"])), styles["AuroraSmall"]),
            p(f"{r['latencia_promedio']:.0f} ms", styles["AuroraSmall"]),
            p(str(int(r["evidencia"])), styles["AuroraSmall"]),
        ])

    service_table = Table(
        service_rows,
        repeatRows=1,
        colWidths=[61 * mm, 23 * mm, 20 * mm, 17 * mm, 17 * mm, 23 * mm, 21 * mm],
    )
    service_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(AURORA_DARK)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(service_table)
    story.append(PageBreak())

    story.append(section_band("Incident Timeline", styles))
    story.append(Spacer(1, 4 * mm))

    if df_fallos.empty:
        story.append(p("No incidents were recorded in the monitored operation.", styles["AuroraBody"]))
    else:
        for _, row in df_fallos.sort_values("timestamp", ascending=False).head(80).iterrows():
            code = str(int(row["http_code"])) if pd.notna(row.get("http_code")) else "DNS/TLS"
            event = str(row.get("error_type") or "Technical failure")
            latency = f"{float(row.get('latency_ms') or 0):.0f} ms"
            service = str(row.get("url", "")).replace("https://", "").replace("http://", "")
            ts = str(row.get("timestamp", ""))[:19]

            item = Table(
                [[
                    p(ts, styles["AuroraSmall"]),
                    p(service, styles["AuroraBody"]),
                    p(code, styles["AuroraSmall"]),
                    p(latency, styles["AuroraSmall"]),
                    p(event[:120], styles["AuroraSmall"]),
                ]],
                colWidths=[31 * mm, 65 * mm, 20 * mm, 22 * mm, 44 * mm],
            )
            item.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFFFFF")),
                ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            story.append(item)
            story.append(Spacer(1, 2 * mm))

    story.append(PageBreak())

    story.append(section_band("Technical Seal & Evidentiary Scope", styles))
    story.append(Spacer(1, 5 * mm))

    seal = Table(
        [[
            [
                p("INTEGRITY PROTECTED", ParagraphStyle(
                    name="SealTitle",
                    fontName=PDF_FONT_BOLD,
                    fontSize=18,
                    leading=22,
                    textColor=colors.HexColor(AURORA_PRIMARY),
                )),
                p("Aurora Operational Evidence Snapshot", styles["AuroraH2"]),
                p(
                    f"This document was generated by Aurora v{AURORA_VERSION}, developed by {AUTHOR_WEB}. "
                    f"It preserves an ordered, chronological and verifiable technical account of the events "
                    f"registered by the monitoring system. This report is a technical evidence package and "
                    f"does not replace a court-appointed expert opinion.",
                    styles["AuroraBody"],
                ),
                p(f"<b>Report ID:</b> {report_id}", styles["AuroraBody"]),
                p(f"<b>Dataset SHA-256:</b> {source_hash}", styles["AuroraBody"]),
                p(f"<b>Verification:</b> {verify_url}", styles["AuroraBody"]),
            ],
            [
                RLImage(str(AURORA_ICON_PATH), width=24 * mm, height=24 * mm),
                Spacer(1, 4 * mm),
                RLImage(qr_path, width=31 * mm, height=31 * mm),
                p("Scan to verify report reference", styles["CenterSmall"]),
            ],
        ]],
        colWidths=[132 * mm, 50 * mm],
    )
    seal.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 1.0, colors.HexColor(AURORA_PRIMARY)),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(seal)

    doc.build(
        story,
        onFirstPage=lambda canvas, doc: draw_pdf_header_footer(canvas, doc, report_id, generated_utc_label),
        onLaterPages=lambda canvas, doc: draw_pdf_header_footer(canvas, doc, report_id, generated_utc_label),
    )

    with open(tmp.name, "rb") as f:
        return f.read()


def registrar_reporte(metadata: dict):
    init_connection().table("aurora_reports").upsert(metadata).execute()


@st.cache_data(ttl=300)
def load_data():
    try:
        response = (
            init_connection()
            .table("incidentes")
            .select("""
                timestamp,
                url,
                http_code,
                latency_ms,
                error_type,
                screenshot_url,
                content_hash,
                ssl_issuer,
                ssl_expiry
            """)
            .order("timestamp", desc=True)
            .limit(500)
            .execute()
        )

        df = pd.DataFrame(response.data)

        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
            df["latency_ms"] = pd.to_numeric(df["latency_ms"], errors="coerce").fillna(0)
            df["http_code"] = pd.to_numeric(df["http_code"], errors="coerce")

            for col in ["error_type", "url", "screenshot_url", "content_hash", "ssl_issuer", "ssl_expiry"]:
                if col not in df.columns:
                    df[col] = None

        return df

    except Exception as e:
        st.error("Aurora no pudo conectarse con la bóveda forense.")
        st.exception(e)
        return pd.DataFrame()


def render_brand():
    st.markdown("""
    <div class="topbar">
      <div class="brand-wrap">
        <div class="brand-logo">
          <svg width="42" height="42" viewBox="0 0 64 64" fill="none">
            <defs>
              <linearGradient id="g" x1="8" y1="8" x2="56" y2="56">
                <stop offset="0%" stop-color="#4F46E5"/>
                <stop offset="55%" stop-color="#06B6D4"/>
                <stop offset="100%" stop-color="#10B981"/>
              </linearGradient>
            </defs>
            <rect x="6" y="6" width="52" height="52" rx="16" fill="url(#g)"/>
            <path d="M18 39C23 22 41 22 46 39" stroke="white" stroke-width="5" stroke-linecap="round"/>
            <circle cx="32" cy="32" r="5" fill="white"/>
          </svg>
        </div>
        <div class="brand-text">Aurora</div>
        <div class="brand-badge">LIVE MONITORING</div>
        <div class="standards-badge">ISO/IEC 27037 · NIST SP 800-92 aligned</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_verify_mode(report_id: str):
    render_brand()

    st.markdown('<div class="verify-card">', unsafe_allow_html=True)
    st.markdown("## Aurora · Verificación de informe")
    st.caption("Validación pública de integridad documental")

    try:
        response = (
            init_connection()
            .table("aurora_reports")
            .select("*")
            .eq("report_id", report_id)
            .limit(1)
            .execute()
        )
    except Exception as e:
        st.error("No fue posible consultar el registro de verificación.")
        st.exception(e)
        st.stop()

    if not response.data:
        st.error("Informe no encontrado en el registro Aurora.")
        st.stop()

    report = response.data[0]

    st.success("Informe registrado y verificable.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Report ID", report["report_id"])
    col2.metric("Uptime", f"{float(report['uptime']):.2f}%")
    col3.metric("Incidentes", int(report["total_failures"]))

    st.code(f"Dataset SHA-256: {report['source_sha256']}")
    st.code(f"PDF SHA-256: {report.get('pdf_sha256') or 'Pendiente'}")

    st.markdown("### Validar PDF")
    uploaded = st.file_uploader("Subir PDF para comparar contra el hash registrado", type=["pdf"])

    if uploaded:
        uploaded_hash = hashlib.sha256(uploaded.read()).hexdigest()

        if uploaded_hash == report.get("pdf_sha256"):
            st.success("El PDF coincide exactamente con el hash registrado.")
        else:
            st.error("El PDF no coincide con el hash registrado.")

        st.code(f"Hash del archivo cargado: {uploaded_hash}")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


query_params = st.query_params
if "verify" in query_params:
    render_verify_mode(query_params["verify"])


render_brand()

df = load_data()

if df.empty:
    st.warning("Aún no hay suficientes datos en la bóveda forense.")
    st.stop()

report_id = f"AUR-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8].upper()}"
generated_utc = datetime.now(timezone.utc)
source_hash = dataframe_sha256(df)
verify_url = f"{VERIFY_BASE_URL}?verify={report_id}"

pdf_bytes = generar_pdf_bytes(
    df,
    report_id=report_id,
    generated_utc=generated_utc,
    source_hash=source_hash,
    verify_url=verify_url,
)
pdf_hash = bytes_sha256(pdf_bytes)

df_full, df_services_full, metrics_full = preparar_df_operacion(df)

registrar_reporte({
    "report_id": report_id,
    "generated_utc": generated_utc.isoformat(),
    "aurora_version": AURORA_VERSION,
    "author_web": AUTHOR_WEB,
    "source_sha256": source_hash,
    "pdf_sha256": pdf_hash,
    "verify_url": verify_url,
    "total_checks": int(metrics_full["total_checks"]),
    "total_failures": int(metrics_full["total_failures"]),
    "uptime": float(metrics_full["uptime"]),
    "avg_latency_ms": float(metrics_full["avg_latency_ms"]),
    "window_start": metrics_full["window_start"].isoformat() if pd.notna(metrics_full["window_start"]) else None,
    "window_end": metrics_full["window_end"].isoformat() if pd.notna(metrics_full["window_end"]) else None,
})

export_left, export_right = st.columns([5.8, 1])

with export_right:
    st.markdown('<div class="export-panel">', unsafe_allow_html=True)
    st.download_button(
        label="📄 PDF",
        data=pdf_bytes,
        file_name=f"Aurora_Enterprise_Evidence_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf",
        key="top_pdf",
        help="Exportar informe técnico completo a PDF",
        use_container_width=True,
    )
    st.markdown(f'<div class="hash-caption">SHA-256 PDF: {pdf_hash[:16]}...</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

endpoints_disponibles = sorted(df["url"].dropna().unique().tolist())

if "section" not in st.session_state:
    st.session_state.section = "Resumen Ejecutivo"

section = st.segmented_control(
    "Vista",
    ["Resumen Ejecutivo", "Latencia", "Incidentes", "Evidencia Forense"],
    default=st.session_state.section,
    key="section",
    label_visibility="collapsed",
)

control1, control2, control3 = st.columns([2.4, 1.1, .7])

with control1:
    endpoint_seleccionado = st.selectbox(
        "Mostrando",
        ["Todas"] + endpoints_disponibles,
        format_func=lambda x: "Mostrando: TODOS" if x == "Todas" else f"Mostrando: {short_url(x, 80)}",
        label_visibility="collapsed",
    )

with control2:
    ventana = st.selectbox(
        "Ventana",
        ["Últimas 24 horas", "Últimos 7 días", "Últimos 30 días", "Todo"],
        label_visibility="collapsed",
    )

with control3:
    if st.button("Actualizar"):
        load_data.clear()
        st.rerun()

df_base = df.copy()
now_utc = pd.Timestamp.now(tz="UTC")

if ventana == "Últimas 24 horas":
    df_base = df_base[df_base["timestamp"] >= now_utc - pd.Timedelta(hours=24)]
elif ventana == "Últimos 7 días":
    df_base = df_base[df_base["timestamp"] >= now_utc - pd.Timedelta(days=7)]
elif ventana == "Últimos 30 días":
    df_base = df_base[df_base["timestamp"] >= now_utc - pd.Timedelta(days=30)]

if endpoint_seleccionado != "Todas":
    df_filtrado = df_base[df_base["url"] == endpoint_seleccionado].copy()
else:
    df_filtrado = df_base.copy()

if df_filtrado.empty:
    st.warning("No hay datos para el endpoint o ventana seleccionada.")
    st.stop()

df_filtrado, df_servicios, metrics = preparar_df_operacion(df_filtrado)

df_fallos = df_filtrado[df_filtrado["is_fail"]].copy()
total_checks = metrics["total_checks"]
total_fallos = metrics["total_failures"]
uptime_porcentaje = metrics["uptime"]
latencia_promedio = metrics["avg_latency_ms"]
ventana_inicio = metrics["window_start"]
ventana_fin = metrics["window_end"]

servicio_mas_caido = df_servicios.sort_values("uptime").iloc[0]
servicio_mas_lento = df_servicios.sort_values("latencia_promedio", ascending=False).iloc[0]
servicio_mas_saludable = df_servicios.sort_values("health_score", ascending=False).iloc[0]
servicio_mas_evidencia = df_servicios.sort_values("evidencia", ascending=False).iloc[0]

if section == "Resumen Ejecutivo":
    st.markdown('<div class="section-title">Gobierno Ejecutivo de Disponibilidad</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Vista consolidada para entender disponibilidad, criticidad, evidencia y salud operativa.</div>', unsafe_allow_html=True)

    st.markdown(f"""
<div class="metric-compact-grid">

<div class="metric-compact">
  <div class="metric-compact-label">Disponibilidad</div>
  <div class="metric-compact-value">{uptime_porcentaje:.2f}%</div>
  <div class="metric-compact-note">Ventana: {ventana_inicio.strftime('%Y-%m-%d %H:%M')} → {ventana_fin.strftime('%Y-%m-%d %H:%M')} UTC</div>
</div>

<div class="metric-compact">
  <div class="metric-compact-label">Incidentes</div>
  <div class="metric-compact-value">{total_fallos}</div>
  <div class="metric-compact-note">Sobre {total_checks} verificaciones</div>
</div>

<div class="metric-compact">
  <div class="metric-compact-label">Latencia promedio</div>
  <div class="metric-compact-value">{latencia_promedio:.0f} ms</div>
  <div class="metric-compact-note">Estado: {classify_latency(latencia_promedio)}</div>
</div>

<div class="metric-compact">
  <div class="metric-compact-label">Muestras</div>
  <div class="metric-compact-value">{total_checks}</div>
  <div class="metric-compact-note">Registros analizados</div>
</div>

<div class="metric-compact">
  <div class="metric-compact-label">Servicio más caído</div>
  <div class="metric-compact-value">{servicio_mas_caido['uptime']:.1f}%</div>
  <div class="metric-compact-note">{short_url(servicio_mas_caido['url'])}</div>
</div>

<div class="metric-compact">
  <div class="metric-compact-label">Servicio más lento</div>
  <div class="metric-compact-value">{servicio_mas_lento['latencia_promedio']:.0f} ms</div>
  <div class="metric-compact-note">{short_url(servicio_mas_lento['url'])}</div>
</div>

<div class="metric-compact">
  <div class="metric-compact-label">Mejor salud</div>
  <div class="metric-compact-value">{servicio_mas_saludable['health_score']:.0f}/100</div>
  <div class="metric-compact-note">{short_url(servicio_mas_saludable['url'])}</div>
</div>

<div class="metric-compact">
  <div class="metric-compact-label">Mayor evidencia</div>
  <div class="metric-compact-value">{int(servicio_mas_evidencia['evidencia'])}</div>
  <div class="metric-compact-note">{short_url(servicio_mas_evidencia['url'])}</div>
</div>

</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Salud por Servicio</div>', unsafe_allow_html=True)

    df_health = df_servicios.copy()
    df_health["uptime"] = df_health["uptime"].round(2)
    df_health["health_score"] = df_health["health_score"].round(1)
    df_health["latencia_promedio"] = df_health["latencia_promedio"].round(0)
    df_health["latencia_maxima"] = df_health["latencia_maxima"].round(0)
    df_health = df_health.sort_values(
        by=["uptime", "fallos", "latencia_promedio"],
        ascending=[True, False, False],
    )

    st.dataframe(
        df_health[["url", "uptime", "health_score", "muestras", "fallos", "latencia_promedio", "latencia_maxima", "evidencia"]],
        use_container_width=True,
        hide_index=True,
    )

elif section == "Latencia":
    st.markdown('<div class="section-title">Evolución de Tiempos de Respuesta</div>', unsafe_allow_html=True)

    fig_latencia = px.line(
        df_filtrado.sort_values("timestamp"),
        x="timestamp",
        y="latency_ms",
        color="url",
        template="simple_white",
        markers=True,
    )
    fig_latencia.update_traces(line=dict(width=3.2), marker=dict(size=7, line=dict(width=1.5, color="white")))
    fig_latencia.update_layout(
        height=560,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#0F172A", size=13),
        hovermode="x unified",
        xaxis=dict(title="", showgrid=False, zeroline=False, tickfont=dict(color="#64748B")),
        yaxis=dict(title="Latencia (ms)", showgrid=True, gridcolor="rgba(100,116,139,0.18)", zeroline=False, tickfont=dict(color="#64748B")),
        legend=dict(title="", orientation="h", yanchor="bottom", y=1.08, xanchor="left", x=0, bgcolor="rgba(255,255,255,0)", font=dict(size=12, color="#334155")),
        margin=dict(l=20, r=20, t=40, b=20),
    )
    fig_latencia.add_hline(
        y=3000,
        line_dash="dash",
        line_color="rgba(239,68,68,0.45)",
        annotation_text="Umbral crítico 3000 ms",
        annotation_position="top left",
    )
    st.plotly_chart(fig_latencia, use_container_width=True)

elif section == "Incidentes":
    st.markdown('<div class="section-title">Bitácora de Fallos y Tiempos de Inactividad</div>', unsafe_allow_html=True)

    if df_fallos.empty:
        st.success("No se han registrado fallos para los filtros seleccionados.")
    else:
        df_fallos_view = df_fallos[["timestamp", "url", "http_code", "latency_ms", "error_type"]].sort_values(by="timestamp", ascending=False).copy()
        df_fallos_view["timestamp"] = df_fallos_view["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        df_fallos_view["url"] = df_fallos_view["url"].apply(lambda x: short_url(x, 70))
        df_fallos_view["http_code"] = df_fallos_view["http_code"].apply(lambda x: "DNS/TLS" if pd.isna(x) else str(int(x)))
        df_fallos_view["latency_ms"] = df_fallos_view["latency_ms"].astype(int).astype(str) + " ms"
        df_fallos_view = df_fallos_view.rename(columns={
            "timestamp": "Fecha",
            "url": "Servicio",
            "http_code": "Código",
            "latency_ms": "Latencia",
            "error_type": "Evento",
        })
        st.dataframe(df_fallos_view, use_container_width=True, hide_index=True, height=560)

elif section == "Evidencia Forense":
    st.markdown('<div class="section-title">Auditoría de Integridad y Certificados</div>', unsafe_allow_html=True)

    df_evidencia_view = df_filtrado[["timestamp", "url", "content_hash", "ssl_issuer", "ssl_expiry", "screenshot_url"]].sort_values(by="timestamp", ascending=False).copy()
    df_evidencia_view["timestamp"] = df_evidencia_view["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    df_evidencia_view["url"] = df_evidencia_view["url"].apply(lambda x: short_url(x, 70))
    df_evidencia_view["content_hash"] = df_evidencia_view["content_hash"].fillna("Sin hash").apply(lambda x: x[:18] + "..." if isinstance(x, str) and len(x) > 18 else x)
    df_evidencia_view["ssl_issuer"] = df_evidencia_view["ssl_issuer"].fillna("No disponible").apply(lambda x: x[:50] + "..." if isinstance(x, str) and len(x) > 50 else x)
    df_evidencia_view["ssl_expiry"] = df_evidencia_view["ssl_expiry"].fillna("No disponible")
    df_evidencia_view["screenshot_url"] = df_evidencia_view["screenshot_url"].fillna("Sin captura")
    df_evidencia_view = df_evidencia_view.rename(columns={
        "timestamp": "Fecha",
        "url": "Servicio",
        "content_hash": "Hash SHA256",
        "ssl_issuer": "Emisor SSL",
        "ssl_expiry": "Expira SSL",
        "screenshot_url": "Evidencia",
    })
    st.dataframe(df_evidencia_view, use_container_width=True, hide_index=True, height=560)
