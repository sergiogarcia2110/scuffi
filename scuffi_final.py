# scuffi_final.py  ·  Scuffi CX Demo · Scuffers
# Run: python3 -m streamlit run scuffi_final.py
# Iconografía inline: paths SVG compatibles con Lucide (https://lucide.dev/, ISC License).

import re, io, base64, functools
from pathlib import Path
from typing import Optional
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as _comps
from PIL import Image as _PILImg


def _lucide_svg(inner: str, *, size: int = 16, color: str = "currentColor", stroke: float = 2, extra_class: str = "") -> str:
    """SVG de línea estilo Lucide (viewBox 24×24)."""
    cls = ("lucide " + extra_class).strip()
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        f'fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round" '
        f'class="{cls}">{inner}</svg>'
    )


# Paths tomados del set Lucide (misma semántica visual que lucide.dev)
_L = {
    "database": (
        '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19A9 3 0 0 0 21 19V5"/>'
        '<path d="M3 12A9 3 0 0 0 21 12"/>'
    ),
    "arrow-right": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    "zap": '<path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.81a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.81a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"/>',
    "package": (
        '<path d="m7.5 4.27 9 5.15"/><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/>'
        '<path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/>'
    ),
    "refresh-cw": (
        '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/>'
        '<path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/>'
    ),
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "bar-chart-2": '<line x1="18" x2="18" y1="20" y2="10"/><line x1="12" x2="12" y1="20" y2="4"/><line x1="6" x2="6" y1="20" y2="14"/>',
    "user": '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    "message-circle": '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/>',
    "instagram": (
        '<rect width="20" height="20" x="2" y="2" rx="5" ry="5"/>'
        '<path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" x2="17.51" y1="6.5" y2="6.5"/>'
    ),
    "map-pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "phone": (
        '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>'
    ),
    "bot": (
        '<path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/>'
        '<path d="M15 13v2"/><path d="M9 13v2"/>'
    ),
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "pencil": '<path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/>',
    "undo-2": '<path d="M9 14 4 9l5-5"/><path d="M4 9h10.5a5.5 5.5 0 0 1 5.5 5.5v0a5.5 5.5 0 0 1-5.5 5.5H11"/>',
    "mic": '<path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/>',
    "volume-2": (
        '<path d="M11 5 6 9H2v6h4l5 4V5z"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/>'
        '<path d="M19.07 4.93a10 10 0 0 1 0 14.14"/>'
    ),
    "arrow-up-right": '<path d="M7 7h10v10"/><path d="M7 17 17 7"/>',
    "clipboard-list": (
        '<rect width="8" height="4" x="8" y="2" rx="1" ry="1"/>'
        '<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>'
        '<path d="M12 11h4"/><path d="M12 16h4"/><path d="M8 11h.01"/><path d="M8 16h.01"/>'
    ),
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/>',
    "footprints": (
        '<path d="M4 16v-2.38a2 2 0 0 1 1.74-1.99l3.27-.55a2 2 0 0 0 1.31-.5l2.71-2.29a2 2 0 0 1 1.59-.56h.13a2 2 0 0 1 1.58 1.18L20 13"/>'
        '<path d="M6.35 9.97 4.52 8.14a2 2 0 0 1-.52-1.86l.42-2.08A2 2 0 0 1 6.05 3h3.69a2 2 0 0 1 1.8 1.1l1.08 2.16"/>'
        '<path d="M11.42 3.38 13 2"/><path d="m18.01 18.51 1.42-1.42"/><path d="m18.91 15.92 1.66-1.66"/>'
    ),
    "triangle-alert": (
        '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>'
        '<path d="M12 9v4"/><path d="M12 17h.01"/>'
    ),
    "star": '<path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>',
}


def _icon(name: str, size: int = 16, color: str = "currentColor", **kw) -> str:
    return _lucide_svg(_L[name], size=size, color=color, **kw)


@functools.lru_cache(maxsize=1)
def _fallback_page_icon_path() -> str:
    """PNG mínimo (sin emoji) si no hay logo.png para favicon de Streamlit."""
    p = Path(__file__).resolve().parent / "_scuffi_tab_fallback.png"
    if not p.is_file():
        im = _PILImg.new("RGBA", (64, 64), (0, 0, 0, 0))
        d = _PILImg.ImageDraw.Draw(im)
        d.polygon([(32, 6), (54, 14), (54, 36), (32, 58), (10, 36), (10, 14)], fill=(43, 117, 81, 255))
        im.save(p, "PNG")
    return str(p)


@functools.lru_cache(maxsize=1)
def _logo_assets():
    """Recorta logo.png, limpia alpha, genera favicon y data URLs para la UI."""
    try:
        img = _PILImg.open("logo.png").convert("RGBA")
    except Exception:
        return None, "", "", ""
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 0 and a < 14:
                px[x, y] = (r, g, b, 0)

    def _fit_square(im, side):
        iw, ih = im.size
        scale = min(side / iw, side / ih)
        nw, nh = max(1, int(iw * scale)), max(1, int(ih * scale))
        im2 = im.resize((nw, nh), _PILImg.Resampling.LANCZOS)
        sq = _PILImg.new("RGBA", (side, side), (0, 0, 0, 0))
        sq.paste(im2, ((side - nw) // 2, (side - nh) // 2), im2)
        return sq

    def _b64_url(im):
        buf = io.BytesIO()
        im.save(buf, format="PNG", optimize=True)
        return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

    def _resize_max_h(im, max_h):
        iw, ih = im.size
        if ih <= max_h:
            return im
        sc = max_h / ih
        return im.resize((max(1, int(iw * sc)), max_h), _PILImg.Resampling.LANCZOS)

    fav = _fit_square(img, 64)
    fav.save("logo_favicon.png", "PNG")
    nav = _resize_max_h(img.copy(), 22)
    bridge = _resize_max_h(img.copy(), 34)
    foot = _resize_max_h(img.copy(), 18)
    return (
        "logo_favicon.png",
        _b64_url(nav),
        _b64_url(bridge),
        _b64_url(foot),
    )


_LOG_FAV, _LOGO_NAV, _LOGO_BRIDGE, _LOGO_FOOT = _logo_assets()

# ─── CONFIG ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Scuffi · CX Demo",
    page_icon=_LOG_FAV if _LOG_FAV else _fallback_page_icon_path(),
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── SCUFFI IMAGES (mtime en caché → al cambiar el PNG se vuelve a procesar) ──
def _file_mtime_ns(rel: str) -> int:
    try:
        return Path(rel).resolve().stat().st_mtime_ns
    except OSError:
        return -1


@st.cache_data
def _scuffi_b64(mtime_ns: int) -> Optional[str]:
    if mtime_ns < 0:
        return None
    try:
        img = _PILImg.open("scuffi.png").convert("RGBA")
        pixels = list(img.getdata())
        clean = [
            (255, 255, 255, 0) if r > 215 and g > 215 and b > 215 else (r, g, b, a)
            for r, g, b, a in pixels
        ]
        img.putdata(clean)
        buf = io.BytesIO()
        img.save(buf, "PNG")
        return base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return None


@st.cache_data
def _scuffi_poster_b64(mtime_ns: int) -> Optional[str]:
    if mtime_ns < 0:
        return None
    try:
        img = _PILImg.open("scuffi_poster.png").convert("RGBA")
        buf = io.BytesIO()
        img.save(buf, "PNG", optimize=True)
        return base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return None


_SB = _scuffi_b64(_file_mtime_ns("scuffi.png"))
_SS = f"data:image/png;base64,{_SB}" if _SB else ""
_POSTER_B64 = _scuffi_poster_b64(_file_mtime_ns("scuffi_poster.png"))
_POSTER_SS = f"data:image/png;base64,{_POSTER_B64}" if _POSTER_B64 else ""

# ─── DATA ─────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("reviews_scuffers.csv", parse_dates=["fecha"])
    df["mes"] = df["fecha"].dt.to_period("M").astype(str)
    return df

df = load_data()

total      = len(df)
avg_rating = df["rating"].mean()
n_neg      = (df["sentimiento"] == "Negativo").sum()
n_pos      = (df["sentimiento"] == "Positivo").sum()
pct_neg    = n_neg / total * 100
pct_pos    = n_pos / total * 100
health     = max(0, min(100, int((avg_rating / 5) * 50 + (pct_pos / 100) * 50)))

neg_df     = df[df["sentimiento"] == "Negativo"]
atc_n      = len(neg_df[neg_df["categoria_problema"] == "Atención al Cliente"])
log_n      = len(neg_df[neg_df["categoria_problema"] == "Envíos y Logística"])
dev_n      = len(neg_df[neg_df["categoria_problema"] == "Devoluciones"])
TICKET, READERS, LOSS, ANN = 65, 150, 0.08, 2.5
clientes_perdidos = int(atc_n * READERS * LOSS * TICKET * ANN)
ventas_riesgo     = int(log_n * READERS * LOSS * TICKET * ANN)
coste_reputacion  = int(750_000 * 0.07 * max(0, 4.2 - avg_rating))
total_impacto     = clientes_perdidos + ventas_riesgo + coste_reputacion

CATEGORY_COLORS = {
    "Atención al Cliente":   "#EF4444",
    "Envíos y Logística":    "#F97316",
    "Devoluciones":          "#A855F7",
    "Calidad de Producto":   "#3B82F6",
    "Experiencia en Tienda": "#D97706",
    "Experiencia Digital":   "#2B7551",
    "Precio":                "#6B7280",
    "Experiencia Positiva":  "#10B981",
}

# ─── SESSION STATE ────────────────────────────────────────────────────────────
def _ss(k, v):
    if k not in st.session_state:
        st.session_state[k] = v

_ss("review_st", "initial")
_ss("nav_page", "cx")

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

#MainMenu, footer { visibility: hidden !important; }
header[data-testid="stHeader"] { display: none !important; }
[data-testid="stToolbar"], .stDeployButton, [data-testid="stToolbarActions"] { display: none !important; }

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; background: #fff; color: #0D0D0D; }
.main .block-container { padding-top: 1.5rem; padding-bottom: 4rem; max-width: 1200px; }

/* Section headers */
.sec-hdr { display: flex; align-items: center; gap: 14px; margin: 44px 0 20px; }
.sec-num { font-family: 'Syne', sans-serif; font-size: 0.8rem; font-weight: 800; color: #D1D5DB; letter-spacing: .08em; }
.sec-ttl { font-family: 'Syne', sans-serif; font-size: 1.6rem; font-weight: 800; color: #0D0D0D; margin: 0; letter-spacing: .02em; }
.sec-line { flex: 1; height: 1px; background: linear-gradient(90deg, #E5E5E5, transparent); }

/* Demo badge */
.demo-badge {
    display: inline-flex; align-items: center; gap: 8px;
    background: #F3F4F6; color: #9CA3AF; font-size: 0.68rem; font-weight: 600;
    letter-spacing: 0.06em; padding: 3px 10px; border-radius: 99px;
}
.demo-badge .lucide { color: #9CA3AF; }

/* Lucide (inline SVG, estilo https://lucide.dev/) */
.lucide { display: inline-block; vertical-align: middle; flex-shrink: 0; }
.insight-icon { display: flex; align-items: center; margin-bottom: 8px; }
.insight-icon .lucide { color: #6B7280; }
.draft-label { display: flex; align-items: center; gap: 8px; }
.draft-label .lucide { flex-shrink: 0; }

/* Header site nav (CX vs Data) */
.hdr-wrap { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;
    padding: 6px 0 10px; border-bottom: 1px solid #E5E5E5; margin-bottom: 0; }
.hdr-row { border-bottom: 1px solid #E5E5E5; padding: 6px 0 10px; margin-bottom: 0; }
.hdr-left { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.hdr-nav { display: flex; align-items: center; gap: 4px; background: #F3F4F6; padding: 4px; border-radius: 10px; }
.hdr-nav a {
    text-decoration: none; font-family: 'DM Sans', sans-serif; font-size: 0.8rem; font-weight: 600;
    color: #6B7280; padding: 8px 14px; border-radius: 8px; transition: background .15s, color .15s;
}
.hdr-nav a:hover { background: #E5E7EB; color: #374151; }
.hdr-nav a.hdr-nav-active { background: #fff; color: #2B7551; box-shadow: 0 1px 3px rgba(0,0,0,.06); }

/* Divider */
.divider { border: none; border-top: 1px solid #E5E5E5; margin: 2.5rem 0; }

/* KPI card */
.kpi-card {
    background: #F8F8F6; border: 1px solid #EBEBEB; border-radius: 12px;
    padding: 18px 20px; text-align: center; height: 100%;
}
.kpi-lbl { font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: .1em; color: #9CA3AF; margin-bottom: 6px; }
.kpi-val { font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 800; line-height: 1; margin-bottom: 4px; }
.kpi-sub { font-size: 0.72rem; color: #9CA3AF; }
.kpi-card.red    { border-top: 3px solid #EF4444; }
.kpi-card.amber  { border-top: 3px solid #D97706; }
.kpi-card.green  { border-top: 3px solid #2B7551; }

/* Impact cards */
.imp-card {
    background: #FEF2F2; border: 1px solid #FECACA; border-radius: 12px;
    padding: 16px; text-align: center;
}
.imp-val { font-family: 'Syne', sans-serif; font-size: 1.7rem; font-weight: 800; color: #DC2626; line-height: 1; margin-bottom: 4px; }
.imp-lbl { font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; color: #EF4444; margin-bottom: 4px; }
.imp-desc { font-size: 0.72rem; color: #9CA3AF; line-height: 1.4; }

/* Insight callout */
.insight-card {
    background: #fff; border: 1.5px solid #E5E5E5; border-radius: 12px;
    padding: 18px; border-left: 4px solid #EF4444; height: 100%;
    transition: border-color .2s, box-shadow .2s;
}
.insight-card:hover { border-left-color: #2B7551; box-shadow: 0 4px 16px rgba(43,117,81,.08); }
.insight-cat { font-family: 'Syne', sans-serif; font-size: 0.85rem; font-weight: 700; margin-bottom: 4px; }
.insight-finding { font-size: 0.78rem; color: #6B7280; line-height: 1.5; margin-bottom: 8px; }
.insight-action {
    font-size: 0.75rem; font-weight: 600; color: #2B7551;
    background: #F1F7F4; padding: 5px 10px; border-radius: 6px;
    display: inline-block;
}

/* Scuffi section */
.scuffi-card {
    background: #F8F8F6; border: 1.5px solid #E5E5E5; border-radius: 16px;
    padding: 28px; height: 100%;
}
.scuffi-nm {
    font-family: 'Syne', sans-serif; font-size: 2.8rem; font-weight: 800;
    color: #2B7551; letter-spacing: .06em; line-height: 1; margin-bottom: 2px;
}
.scuffi-tg { font-size: 0.75rem; font-weight: 600; letter-spacing: .12em; text-transform: uppercase; color: #9CA3AF; margin-bottom: 20px; }
.spower { display: flex; gap: 10px; margin-bottom: 12px; align-items: flex-start; }
.spower-ico { font-size: 1rem; flex-shrink: 0; margin-top: 2px; }
.spower-txt { font-size: 0.82rem; color: #4B5563; line-height: 1.5; }
.spower-txt strong { color: #0D0D0D; font-weight: 600; }
.ch-pill {
    display: inline-block; padding: 4px 12px; margin: 3px 2px;
    background: #F1F7F4; border: 1px solid #C5DED2; border-radius: 99px;
    font-size: 0.72rem; color: #2B7551; font-weight: 600; letter-spacing: .04em;
}

/* Multichannel tabs */
.stTabs [data-baseweb="tab-list"] { gap: 0; border-bottom: 1px solid #E5E5E5; }
.stTabs [data-baseweb="tab"] { font-size: 0.82rem; font-weight: 500; color: #6B7280; padding: 10px 20px; border-bottom: 2px solid transparent; }
.stTabs [aria-selected="true"] { color: #2B7551 !important; border-bottom-color: #2B7551 !important; font-weight: 600 !important; }

/* Buttons */
.stButton > button {
    font-size: 0.82rem !important; border-radius: 8px !important;
    border: 1.5px solid #2B7551 !important; background: #2B7551 !important;
    color: #fff !important; padding: 6px 16px !important;
}
.stButton > button:hover { background: #245542 !important; border-color: #245542 !important; }

/* Review/Maps */
.review-card { background: #F8F8F6; border: 1px solid #E5E5E5; border-radius: 12px; padding: 16px; margin-bottom: 14px; }
.review-stars { color: #FBBF24; font-size: 1rem; letter-spacing: 2px; margin-bottom: 4px; }
.review-meta { font-size: 0.72rem; color: #9CA3AF; margin-bottom: 8px; }
.review-text { font-size: 0.85rem; color: #374151; line-height: 1.55; font-style: italic; }
.draft-card { background: #F1F7F4; border: 1.5px solid #C5DED2; border-radius: 12px; padding: 16px; margin: 12px 0; }
.draft-label { font-size: 0.62rem; font-weight: 700; text-transform: uppercase; letter-spacing: .1em; color: #2B7551; margin-bottom: 8px; }
.draft-text { font-size: 0.83rem; color: #1F2937; line-height: 1.6; }

/* Voice */
.voice-card { background: #0D0D0D; border-radius: 14px; padding: 28px 24px; color: #fff; }
.voice-phase-badge { display: inline-block; background: rgba(43,117,81,.2); color: #7DCF9E; font-size: 0.65rem; font-weight: 700; letter-spacing: .1em; padding: 3px 10px; border-radius: 99px; margin-bottom: 12px; text-transform: uppercase; }
.waveform { display: flex; align-items: center; gap: 3px; height: 40px; margin: 16px 0; }
.wave-bar { width: 4px; background: #2B7551; border-radius: 2px; animation: wave 1.2s ease-in-out infinite; }
.wave-bar:nth-child(1) { animation-delay: 0s; }
.wave-bar:nth-child(2) { animation-delay: .1s; }
.wave-bar:nth-child(3) { animation-delay: .2s; }
.wave-bar:nth-child(4) { animation-delay: .3s; }
.wave-bar:nth-child(5) { animation-delay: .4s; }
.wave-bar:nth-child(6) { animation-delay: .3s; }
.wave-bar:nth-child(7) { animation-delay: .2s; }
.wave-bar:nth-child(8) { animation-delay: .1s; }
.wave-bar:nth-child(9) { animation-delay: 0s; }
@keyframes wave { 0%,100% { height: 8px; } 50% { height: 34px; } }

/* Projection numbers */
.proj-num { font-family: 'Syne', sans-serif; font-size: 1.6rem; font-weight: 800; color: #2B7551; line-height: 1; margin-bottom: 4px; }
.proj-lbl { font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; color: #9CA3AF; }
.proj-card { background: #F1F7F4; border: 1px solid #C5DED2; border-radius: 12px; padding: 18px; text-align: center; }

/* Data & Analytics (sección 05) */
.pipe-wrap {
    background: linear-gradient(180deg, #F8F8F6 0%, #fff 100%);
    border: 1px solid #E5E5E5; border-radius: 16px; padding: 1.35rem 1.25rem 1.5rem; margin-bottom: 1.5rem;
}
.pipe-ttl {
    font-family: 'Syne', sans-serif; font-size: 0.72rem; font-weight: 800; text-transform: uppercase;
    letter-spacing: 0.12em; color: #9CA3AF; margin-bottom: 14px; text-align: center;
}
.pipe-flow { display: flex; flex-wrap: nowrap; align-items: stretch; justify-content: center; gap: 0;
    overflow-x: auto; padding-bottom: 6px; -webkit-overflow-scrolling: touch; }
.pipe-step {
    flex: 1; min-width: 100px; max-width: 160px; text-align: center; padding: 10px 8px;
    position: relative;
}
.pipe-step-num {
    width: 28px; height: 28px; margin: 0 auto 8px; border-radius: 50%;
    background: linear-gradient(135deg, #2B7551, #1a5238); color: #fff;
    font-family: 'Syne', sans-serif; font-size: 0.72rem; font-weight: 800; line-height: 28px;
    box-shadow: 0 4px 14px rgba(43, 117, 81, 0.25);
    animation: pipeGlow 2.8s ease-in-out infinite;
}
.pipe-step:nth-child(2) .pipe-step-num { animation-delay: 0.35s; }
.pipe-step:nth-child(3) .pipe-step-num { animation-delay: 0.7s; }
.pipe-step:nth-child(4) .pipe-step-num { animation-delay: 1.05s; }
.pipe-step:nth-child(5) .pipe-step-num { animation-delay: 1.4s; }
@keyframes pipeGlow { 0%, 100% { box-shadow: 0 4px 14px rgba(43, 117, 81, 0.25); } 50% { box-shadow: 0 4px 22px rgba(125, 207, 158, 0.45); } }
.pipe-step-ttl { font-size: 0.72rem; font-weight: 700; color: #0D0D0D; margin-bottom: 4px; }
.pipe-step-desc { font-size: 0.65rem; color: #6B7280; line-height: 1.4; }
.pipe-arrow { display: flex; align-items: center; color: #C5DED2; font-size: 1.1rem; font-weight: 300; padding: 0 2px; user-select: none; }

.data-insight-deck { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin: 1.25rem 0 1.5rem; }
@media (max-width: 900px) { .data-insight-deck { grid-template-columns: 1fr; } }
.data-insight-card {
    background: #fff; border: 1px solid #E5E5E5; border-radius: 14px; padding: 18px;
    border-left: 4px solid var(--accent, #2B7551); height: 100%;
    box-shadow: 0 4px 20px rgba(0,0,0,.04);
}
.data-insight-card .tag { font-size: 0.62rem; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; color: var(--accent, #2B7551); margin-bottom: 8px; }
.data-insight-card h3 { font-family: 'Syne', sans-serif; font-size: 0.88rem; font-weight: 800; color: #0D0D0D; margin: 0 0 10px 0; }
.data-insight-card p { font-size: 0.78rem; color: #6B7280; line-height: 1.55; margin: 0 0 10px 0; }
.data-insight-card .cta { font-size: 0.74rem; font-weight: 600; color: #245542; background: #F1F7F4; padding: 6px 10px; border-radius: 8px; display: inline-block; }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# NAVBAR
# =============================================================================
_nav_logo = (
    f'<img src="{_LOGO_NAV}" alt="Scuffers" style="height:22px;width:auto;vertical-align:middle;'
    f'margin-right:10px;display:inline-block;">'
    if _LOGO_NAV
    else ""
)
_hdr_left, _hdr_right = st.columns([2.5, 1.05], gap="medium")
with _hdr_left:
    st.markdown(
        '<div style="padding:6px 0 10px;">'
        '<div style="display:flex;align-items:center;flex-wrap:wrap;gap:14px;">'
        '<div style="font-family:\'Syne\',sans-serif;font-size:1rem;font-weight:800;letter-spacing:.04em;display:flex;align-items:center;">'
        f'{_nav_logo}'
        'SCUFFI <span style="font-weight:400;color:#9CA3AF;font-size:.85rem;">· CX AI Demo</span>'
        '</div>'
        '<div class="demo-badge">'
        + _icon("database", 14, "#9CA3AF")
        + " Datos reales · Scuffers Google Maps</div>"
        "</div></div>",
        unsafe_allow_html=True,
    )
with _hdr_right:
    _nb1, _nb2 = st.columns(2, gap="small")
    _nav = st.session_state.get("nav_page", "cx")
    with _nb1:
        if st.button(
            "CX Demo",
            key="nav_cx",
            use_container_width=True,
            type="primary" if _nav == "cx" else "secondary",
        ):
            st.session_state.nav_page = "cx"
    with _nb2:
        if st.button(
            "Scuffi",
            key="nav_poster",
            use_container_width=True,
            type="primary" if _nav == "poster" else "secondary",
        ):
            st.session_state.nav_page = "poster"
st.markdown(
    '<div style="border-bottom:1px solid #E5E5E5;margin:0 0 10px 0;"></div>',
    unsafe_allow_html=True,
)

if st.session_state.get("nav_page", "cx") == "poster":
    st.markdown(
        '<div class="scuffi-poster-wrap" style="display:flex;justify-content:center;align-items:center;'
        'padding:0.35rem 0 0.75rem;box-sizing:border-box;'
        'max-height:min(calc(100dvh - 88px),calc(100vh - 88px));overflow:hidden;">',
        unsafe_allow_html=True,
    )
    if _POSTER_SS:
        st.markdown(
            f'<img src="{_POSTER_SS}" alt="Scuffi poster" class="scuffi-poster-img" '
            'style="max-height:min(calc(100dvh - 100px),calc(100vh - 100px));'
            'max-width:96vw;width:auto;height:auto;object-fit:contain;'
            'border-radius:14px;box-shadow:0 12px 48px rgba(0,0,0,.1);display:block;margin:0 auto;">',
            unsafe_allow_html=True,
        )
    else:
        st.error(
            "Falta el archivo **scuffi_poster.png** en la carpeta del proyecto. "
            "Colócalo junto a `scuffi_final.py` y recarga la página."
        )
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


def _render_footer():
    _foot_logo = (
        f'<img src="{_LOGO_FOOT}" alt="" style="height:18px;width:auto;vertical-align:middle;margin-right:8px;">'
        if _LOGO_FOOT
        else ""
    )
    st.markdown(
        '<div style="text-align:center;margin-top:3rem;padding-top:1.5rem;'
        'border-top:1px solid #E5E5E5;font-size:.68rem;color:#9CA3AF;letter-spacing:.06em;display:flex;'
        'align-items:center;justify-content:center;flex-wrap:wrap;gap:4px;">'
        f'{_foot_logo}'
        'SCUFFI · CX AI Demo'
        '</div>',
        unsafe_allow_html=True,
    )


def _render_section_data_analytics():
    """Sección 05: pipeline de datos + lecturas tipo dashboard con Scuffi."""
    st.markdown(
        '<div class="sec-hdr">'
        '<span class="sec-num">05</span>'
        '<h2 class="sec-ttl">DATA &amp; ANALYTICS</h2>'
        '<div class="sec-line"></div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="font-size:.88rem;color:#6B7280;margin:-8px 0 22px;max-width:760px;line-height:1.6;">'
        "Vista de cómo <strong style='color:#0D0D0D;'>implementaríamos Data &amp; Analytics con Scuffi</strong>: "
        "cada resolución deja campos estructurados (intent, sentimiento, categoría, canal, tiempos) que alimentan "
        "un mismo tablero — sin exportar reseñas a Excel ni depender de memoria del equipo."
        "</div>",
        unsafe_allow_html=True,
    )
    _pipe_steps = [
        ("1", "Multicanal", "IG, web, Maps, voz: un solo flujo."),
        ("2", "Captura", "Intent, sentimiento, categoría, CSAT, tiempo."),
        ("3", "Datos", "Histórico unificado, no pantallazos."),
        ("4", "Insight", "Alertas y tendencias automáticas."),
        ("5", "Acción", "Prioridad clara para ops, producto y marca."),
    ]
    _cells = []
    for _i, (_num, _ttl, _desc) in enumerate(_pipe_steps):
        _cells.append(
            f'<div class="pipe-step"><div class="pipe-step-num">{_num}</div>'
            f'<div class="pipe-step-ttl">{_ttl}</div><div class="pipe-step-desc">{_desc}</div></div>'
        )
        if _i < len(_pipe_steps) - 1:
            _cells.append(
                '<div class="pipe-arrow">' + _icon("arrow-right", 20, "#C5DED2") + "</div>"
            )
    st.markdown(
        '<div class="pipe-wrap">'
        '<div class="pipe-ttl">De la conversación a la mejora continua</div>'
        f'<div class="pipe-flow">{"".join(_cells)}</div>'
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="font-family:\'Syne\',sans-serif;font-size:.72rem;font-weight:800;text-transform:uppercase;'
        'letter-spacing:.12em;color:#9CA3AF;margin:1.35rem 0 12px 0;">'
        "Tres lecturas que Scuffi habría mostrado el primer mes</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="data-insight-deck">'
        f'<div class="data-insight-card" style="--accent:#F97316;">'
        f'<div class="tag">Ops · Logística</div>'
        f"<h3>{log_n} señales de envíos en el histórico</h3>"
        f"<p>Patrón claro: el cliente no tiene visibilidad ni resolución rápida. "
        f"Scuffi alerta por volumen y canal antes de que el problema se cemente en Maps.</p>"
        f'<div class="cta">'
        + _icon("arrow-right", 14, "#245542")
        + " Priorizar comunicación proactiva y SLA con transporte</div>"
        f"</div>"
        f'<div class="data-insight-card" style="--accent:#A855F7;">'
        f'<div class="tag">CX · Devoluciones</div>'
        f"<h3>{dev_n} frustraciones con el proceso</h3>"
        f"<p>La fricción no es la política, es el esfuerzo mental del cliente. "
        f"Scuffi cierra el loop sin que el usuario navegue formularios opacos.</p>"
        f'<div class="cta">'
        + _icon("arrow-right", 14, "#245542")
        + " Devolución guiada = menos tickets y menos 1★</div>"
        f"</div>"
        f'<div class="data-insight-card" style="--accent:#3B82F6;">'
        f'<div class="tag">Marca · Maps</div>'
        f"<h3>0 respuestas públicas hoy</h3>"
        f"<p>Cada respuesta bien hecha suma confianza en la ficha. Scuffi redacta y propone en segundos; "
        f"tú solo validas tono de marca.</p>"
        f'<div class="cta">'
        + _icon("arrow-right", 14, "#245542")
        + " Pasar de silencio a presencia activa en reviews</div>"
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


# =============================================================================
# SECTION 1 — HERO
# =============================================================================
st.markdown('<div style="padding:1.8rem 0 1.2rem;">', unsafe_allow_html=True)
hero_l, hero_r = st.columns([1.35, 1])

with hero_l:
    st.markdown(
        '<div style="font-size:.68rem;font-weight:700;letter-spacing:.16em;text-transform:uppercase;'
        'color:#EF4444;margin-bottom:.8rem;display:flex;align-items:center;gap:8px;">'
        '<span style="display:inline-block;width:20px;height:2px;background:#EF4444;"></span>'
        'DIAGNÓSTICO DE MARCA · SCUFFERS MADRID'
        '</div>'
        '<div style="font-family:\'Syne\',sans-serif;font-size:clamp(1.8rem,3vw,2.7rem);font-weight:800;'
        'line-height:1.15;color:#0D0D0D;margin-bottom:1rem;">'
        'Scuffers necesita un<br>'
        '<span style="color:#2B7551;">superhéroe de CX</span><br>'
        '<span style="font-size:.55em;font-weight:400;color:#6B7280;">'
        '— y los datos lo demuestran.'
        '</span>'
        '</div>'
        f'<div style="font-size:.9rem;color:#6B7280;line-height:1.65;max-width:480px;">'
        f'Analicé {total} reseñas reales de Scuffers. El problema no es solo el rating: es que '
        f'<strong style="color:#0D0D0D;">el cliente no recibe resolución</strong>. '
        f'Scuffi cambia eso.'
        f'</div>',
        unsafe_allow_html=True,
    )

with hero_r:
    h1, h2 = st.columns(2)
    with h1:
        st.markdown(
            f'<div class="kpi-card red">'
            f'<div class="kpi-lbl">Rating Google Maps</div>'
            f'<div class="kpi-val" style="color:#DC2626;">{avg_rating:.1f}★</div>'
            f'<div class="kpi-sub">vs 4.2★ sector · gap −{4.2 - avg_rating:.1f}★</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with h2:
        st.markdown(
            f'<div class="kpi-card red">'
            f'<div class="kpi-lbl">Reseñas negativas</div>'
            f'<div class="kpi-val" style="color:#DC2626;">{pct_neg:.0f}%</div>'
            f'<div class="kpi-sub">{n_neg} de {total} reseñas analizadas</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
    h3, h4 = st.columns(2)
    with h3:
        hcolor = "#DC2626" if health < 40 else "#D97706" if health < 70 else "#2B7551"
        st.markdown(
            f'<div class="kpi-card red">'
            f'<div class="kpi-lbl">Brand Health Score</div>'
            f'<div class="kpi-val" style="color:{hcolor};">{health}/100</div>'
            f'<div class="kpi-sub">Zona crítica: &lt;40</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with h4:
        st.markdown(
            f'<div class="kpi-card red">'
            f'<div class="kpi-lbl">Impacto económico/año</div>'
            f'<div class="kpi-val" style="color:#DC2626;">€{total_impacto // 1000}k</div>'
            f'<div class="kpi-sub">Ingresos en riesgo estimados</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown('</div>', unsafe_allow_html=True)


# =============================================================================
# SECTION 2 — RADIOGRAFÍA DE MARCA
# =============================================================================
st.markdown(
    '<div class="sec-hdr">'
    '<span class="sec-num">01</span>'
    '<h2 class="sec-ttl">RADIOGRAFÍA DE MARCA</h2>'
    '<div class="sec-line"></div>'
    '</div>',
    unsafe_allow_html=True,
)

col_g, col_kpis, col_imp = st.columns([1.1, 1, 1.3])

with col_g:
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=health,
        title={"text": "Brand Health Score", "font": {"color": "#9CA3AF", "size": 11, "family": "DM Sans"}},
        gauge={
            "axis": {
                "range": [0, 100],
                "tickcolor": "#E5E5E5",
                "tickfont": {"color": "#D1D5DB", "size": 10},
                "tickvals": [0, 25, 50, 75, 100],
            },
            "bar": {
                "color": "#DC2626" if health < 40 else "#D97706" if health < 70 else "#2B7551",
                "thickness": 0.22,
            },
            "bgcolor": "rgba(0,0,0,0)",
            "bordercolor": "#E5E5E5",
            "borderwidth": 1,
            "steps": [
                {"range": [0, 33],  "color": "rgba(220,38,38,.06)"},
                {"range": [33, 66], "color": "rgba(217,119,6,.05)"},
                {"range": [66, 100], "color": "rgba(43,117,81,.05)"},
            ],
        },
        number={
            "font": {
                "color": "#DC2626" if health < 40 else "#D97706" if health < 70 else "#2B7551",
                "size": 46,
                "family": "Syne",
            },
            "suffix": "/100",
        },
    ))
    fig_gauge.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#6B7280"}, margin=dict(t=30, b=10, l=30, r=30), height=250,
    )
    st.plotly_chart(fig_gauge, use_container_width=True)
    st.markdown(
        '<div style="text-align:center;margin-top:-8px;">'
        '<div style="font-size:.62rem;color:#9CA3AF;letter-spacing:.1em;text-transform:uppercase;">Zona Crítica · Acción Urgente</div>'
        '<div style="display:flex;justify-content:center;gap:14px;margin-top:8px;">'
        '<span style="font-size:.65rem;color:#EF4444;">● 0–33 Crítico</span>'
        '<span style="font-size:.65rem;color:#D97706;">● 33–66 Riesgo</span>'
        '<span style="font-size:.65rem;color:#2B7551;">● 66–100 Saludable</span>'
        '</div></div>',
        unsafe_allow_html=True,
    )

with col_kpis:
    st.markdown(
        f'<div class="kpi-card red" style="margin-bottom:10px;">'
        f'<div class="kpi-lbl">Puntuación media</div>'
        f'<div class="kpi-val" style="color:#DC2626;">{avg_rating:.1f} / 5.0</div>'
        f'<div class="kpi-sub">Sector: 4.2★ · Gap: −{4.2 - avg_rating:.1f}★</div>'
        f'</div>'
        f'<div class="kpi-card red" style="margin-bottom:10px;">'
        f'<div class="kpi-lbl">Sin respuesta pública</div>'
        f'<div class="kpi-val" style="color:#DC2626;">100%</div>'
        f'<div class="kpi-sub">0 respuestas de Scuffers en Google Maps</div>'
        f'</div>'
        f'<div class="kpi-card amber">'
        f'<div class="kpi-lbl">Reseñas positivas</div>'
        f'<div class="kpi-val" style="color:#D97706;">{pct_pos:.0f}%</div>'
        f'<div class="kpi-sub">{n_pos} fans que no están siendo fidelizados</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

with col_imp:
    st.markdown(
        f'<div class="imp-card" style="margin-bottom:10px;">'
        f'<div class="imp-val">€{clientes_perdidos:,}</div>'
        f'<div class="imp-lbl">Clientes perdidos · Atención</div>'
        f'<div class="imp-desc">{atc_n} reseñas neg. × 150 lectores × 8% disuasión × €{TICKET} ticket · anualizado</div>'
        f'</div>'
        f'<div class="imp-card" style="margin-bottom:10px;">'
        f'<div class="imp-val">€{ventas_riesgo:,}</div>'
        f'<div class="imp-lbl">Ventas en riesgo · Logística</div>'
        f'<div class="imp-desc">{log_n} reseñas negativas de envíos · impacto en decisión de compra</div>'
        f'</div>'
        f'<div class="imp-card">'
        f'<div class="imp-val">€{coste_reputacion:,}</div>'
        f'<div class="imp-lbl">Coste reputacional</div>'
        f'<div class="imp-desc">Gap de {4.2 - avg_rating:.1f}★ vs sector × 7% impacto revenue × €750k est.</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# =============================================================================
# SECTION 3 — MAPA DE PROBLEMAS
# =============================================================================
st.markdown(
    '<div class="sec-hdr">'
    '<span class="sec-num">02</span>'
    '<h2 class="sec-ttl">MAPA DE PROBLEMAS</h2>'
    '<div class="sec-line"></div>'
    '</div>',
    unsafe_allow_html=True,
)

col_bubble, col_bars = st.columns([1.5, 1])

with col_bubble:
    cat_cnt = neg_df["categoria_problema"].value_counts()
    URGENCY = {
        "Atención al Cliente":   (8, 9),
        "Envíos y Logística":    (5, 8),
        "Devoluciones":          (7, 7),
        "Calidad de Producto":   (4, 7),
        "Experiencia en Tienda": (6, 5),
        "Experiencia Digital":   (8, 4),
        "Precio":                (5, 3),
    }
    bx, by, bsize, bcolor, bhover = [], [], [], [], []
    for cat, cnt in cat_cnt.items():
        ease, impact = URGENCY.get(cat, (5, 5))
        bx.append(ease); by.append(impact)
        # Marcadores más grandes (legibles en presentación / pantalla compartida)
        bsize.append(max(cnt * 16 + 56, 72))
        bcolor.append(CATEGORY_COLORS.get(cat, "#888"))
        urg = (
            "Alta — ACTUAR YA"
            if impact >= 8
            else "Media — IMPORTANTE"
            if impact >= 6
            else "Baja — MONITORIZAR"
        )
        bhover.append(
            f"<b>{cat}</b><br>"
            f"Reseñas negativas: {cnt} ({cnt/len(neg_df)*100:.0f}%)<br>"
            f"Urgencia: {urg}<br>"
            f"Facilidad: {ease}/10 · Impacto: {impact}/10"
        )
    fig_b = go.Figure()
    fig_b.add_trace(go.Scatter(
        x=bx, y=by, mode="markers",
        marker=dict(size=bsize, color=bcolor, sizemode="area", opacity=0.92,
                    line=dict(color="rgba(255,255,255,.85)", width=2)),
        hovertemplate="%{customdata}<extra></extra>",
        customdata=bhover,
    ))
    for lbl, x, y, col in [
        ("QUICK WINS", 8.5, 9.5, "#245542"),
        ("ESTRATÉGICO", 2.5, 9.5, "#B91C1C"),
        ("FILL IN", 8.5, 2, "#4338CA"),
        ("BAJA PRIORIDAD", 2.5, 2, "#4B5563"),
    ]:
        fig_b.add_annotation(
            x=x, y=y, text=f"<b>{lbl}</b>", showarrow=False,
            font=dict(size=13, color=col, family="DM Sans"),
        )
    fig_b.add_hline(y=6, line=dict(color="rgba(0,0,0,0.08)", dash="dot"))
    fig_b.add_vline(x=6, line=dict(color="rgba(0,0,0,0.08)", dash="dot"))
    fig_b.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(248,248,246,1)",
        xaxis=dict(title=dict(text="Facilidad de solución →",
                              font=dict(size=12, color="#4B5563", family="DM Sans")),
                   range=[0, 11], gridcolor="rgba(0,0,0,.05)", color="#6B7280",
                   tickfont=dict(color="#6B7280", size=11)),
        yaxis=dict(title=dict(text="Impacto potencial →",
                              font=dict(size=12, color="#4B5563", family="DM Sans")),
                   range=[0, 11], gridcolor="rgba(0,0,0,.05)", color="#6B7280",
                   tickfont=dict(color="#6B7280", size=11)),
        margin=dict(t=24, b=48, l=56, r=24), height=440,
        hoverlabel=dict(bgcolor="#fff", bordercolor="#E5E5E5",
                        font=dict(color="#0D0D0D", size=13, family="DM Sans")),
    )
    st.plotly_chart(fig_b, use_container_width=True)

with col_bars:
    cat_total = len(neg_df)
    cat_dist  = neg_df["categoria_problema"].value_counts()
    urgency_colors = {
        "Atención al Cliente":   "#EF4444",
        "Envíos y Logística":    "#F97316",
        "Devoluciones":          "#A855F7",
        "Calidad de Producto":   "#3B82F6",
        "Experiencia en Tienda": "#D97706",
        "Experiencia Digital":   "#2B7551",
        "Precio":                "#9CA3AF",
    }
    urgency_txt = {
        "Atención al Cliente":   "ACTUAR YA",
        "Envíos y Logística":    "ACTUAR YA",
        "Devoluciones":          "IMPORTANTE",
        "Calidad de Producto":   "IMPORTANTE",
        "Experiencia en Tienda": "IMPORTANTE",
        "Experiencia Digital":   "MONITORIZAR",
        "Precio":                "MONITORIZAR",
    }
    pcts   = [v / cat_total * 100 if cat_total > 0 else 0 for v in cat_dist.values]
    colors = [urgency_colors.get(k, "#9CA3AF") for k in cat_dist.index]
    labels = [urgency_txt.get(k, "") for k in cat_dist.index]
    fig_bars = go.Figure(go.Bar(
        x=pcts, y=list(cat_dist.index), orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{p:.0f}%  {l}" for p, l in zip(pcts, labels)],
        textposition="outside",
        textfont=dict(color="#1F2937", size=13, family="DM Sans"),
        hovertemplate="<b>%{y}</b><br>%{x:.0f}% del total negativo<extra></extra>",
    ))
    fig_bars.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,.05)", color="#6B7280",
                   tickfont=dict(color="#6B7280", size=11), ticksuffix="%",
                   range=[0, max(pcts) * 1.62]),
        yaxis=dict(showgrid=False, color="#111827",
                   tickfont=dict(color="#111827", size=12)),
        margin=dict(t=36, b=12, l=8, r=120), height=400,
        title=dict(text="DISTRIBUCIÓN DE QUEJAS",
                   font=dict(size=12, color="#374151", family="DM Sans"), x=0),
        font=dict(family="DM Sans", color="#111827"),
        hoverlabel=dict(bgcolor="#fff", bordercolor="#E5E5E5",
                        font=dict(color="#0D0D0D", size=12)),
    )
    st.plotly_chart(fig_bars, use_container_width=True)

# Insight callouts
st.markdown('<div style="margin-top:8px;">', unsafe_allow_html=True)
ins_cols = st.columns(3)
insights = [
    (
        _icon("zap", 22, "#6B7280"),
        "Atención al Cliente · 35% de quejas",
        f"{atc_n} reseñas negativas, 0 respondidas públicamente. Sin SLA. Cada reseña disuade ~12 compradores potenciales.",
        _icon("arrow-right", 13, "#2B7551")
        + " Scuffi responde &lt;1 min · 24/7 · resolución guiada",
    ),
    (
        _icon("package", 22, "#6B7280"),
        "Envíos y Logística · 22% de quejas",
        f"{log_n} incidencias de tracking sin comunicación proactiva. Clientes en la oscuridad = frustración amplificada.",
        _icon("arrow-right", 13, "#2B7551")
        + " Scuffi notifica proactivamente y gestiona la incidencia en tiempo real",
    ),
    (
        _icon("refresh-cw", 22, "#6B7280"),
        "Devoluciones · proceso confuso",
        f"{dev_n} reseñas negativas sobre el proceso. El cliente tiene que gestionar solo su devolución — eso es fricción evitable.",
        _icon("arrow-right", 13, "#2B7551")
        + " Scuffi hace la devolución por el cliente, no el cliente",
    ),
]
for i, (icon, cat, finding, action) in enumerate(insights):
    with ins_cols[i]:
        st.markdown(
            f'<div class="insight-card">'
            f'<div class="insight-icon">{icon}</div>'
            f'<div class="insight-cat">{cat}</div>'
            f'<div class="insight-finding">{finding}</div>'
            f'<div class="insight-action">{action}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
st.markdown('</div>', unsafe_allow_html=True)


# =============================================================================
# SEGUE — bridge data to solution
# =============================================================================
_bridge_logo = (
    f'<img src="{_LOGO_BRIDGE}" alt="Scuffers" style="height:34px;width:auto;display:block;">'
    if _LOGO_BRIDGE
    else _icon("footprints", 36, "#2B7551")
)
st.markdown(
    '<div style="background:#F1F7F4;border:1.5px solid #C5DED2;border-radius:14px;'
    'padding:20px 28px;margin:2.5rem 0;display:flex;align-items:center;gap:20px;">'
    f'<div style="flex-shrink:0;display:flex;align-items:center;">{_bridge_logo}</div>'
    '<div>'
    '<div style="font-family:\'Syne\',sans-serif;font-weight:700;font-size:1rem;color:#0D0D0D;margin-bottom:4px;">'
    'Los datos tienen una respuesta: Scuffi'
    '</div>'
    '<div style="font-size:.84rem;color:#6B7280;">'
    'Un asistente de IA especializado en CX para Scuffers que no solo responde consultas — '
    '<strong style="color:#2B7551;">resuelve casos, hace devoluciones, gestiona incidencias y convierte cada interacción en inteligencia para mejorar el negocio.</strong>'
    '</div>'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
)


# =============================================================================
# SECTION 4 — SCUFFI
# =============================================================================
st.markdown(
    '<div class="sec-hdr">'
    '<span class="sec-num">03</span>'
    '<h2 class="sec-ttl">SCUFFI · LA IA DE SCUFFERS</h2>'
    '<div class="sec-line"></div>'
    '</div>',
    unsafe_allow_html=True,
)

col_sf, col_chat = st.columns([1, 1.15])

with col_sf:
    _av = (
        f'<img src="{_SS}" style="width:130px;height:130px;object-fit:contain;display:block;">'
        if _SS
        else (
            '<span style="display:flex;align-items:center;justify-content:center;width:130px;height:130px;">'
            + _icon("shield", 64, "#7DCF9E", stroke=1.5)
            + "</span>"
        )
    )
    _ico = functools.partial(_icon, color="rgba(255,255,255,.9)")
    powers = [
        (_ico("target", 17), "RESOLUCIÓN GUIADA", "87%", "casos cerrados sin escalar", "#EF4444"),
        (_ico("refresh-cw", 17), "DEVOLUCIONES AUTO", "0", "pasos que hace el cliente", "#A855F7"),
        (_ico("package", 17), "TRACKING REAL-TIME", "100%", "incidencias notificadas proactivamente", "#F97316"),
        (_ico("bar-chart-2", 17), "INSIGHTS ACCIONABLES", "∞", "cada chat = dato de negocio", "#3B82F6"),
        (_ico("user", 17), "ESCALADO INTELIGENTE", "0%", "contexto perdido al transferir", "#10B981"),
    ]
    pow_html = ""
    for i, (ico, name, stat, desc, col) in enumerate(powers):
        pow_html += (
            f'<div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);'
            f'border-radius:10px;padding:11px 13px;position:relative;overflow:hidden;">'
            f'<div style="position:absolute;top:0;left:0;width:3px;height:100%;background:{col};border-radius:10px 0 0 10px;"></div>'
            f'<div style="display:flex;align-items:center;gap:7px;margin-bottom:6px;">'
            f'<span style="display:inline-flex;line-height:0;">{ico}</span>'
            f'<span style="font-family:\'Syne\',sans-serif;font-size:.62rem;font-weight:800;'
            f'letter-spacing:.08em;color:rgba(255,255,255,.5);text-transform:uppercase;">{name}</span>'
            f'</div>'
            f'<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">'
            f'<span style="font-family:\'Syne\',sans-serif;font-size:1.5rem;font-weight:800;'
            f'color:{col};line-height:1;flex-shrink:0;">{stat}</span>'
            f'<span style="font-size:.78rem;color:rgba(255,255,255,.52);line-height:1.35;'
            f'flex:1;min-width:min(100%,9rem);">{desc}</span>'
            f'</div>'
            f'</div>'
        )
    _channels = [
        ("message-circle", "Web"),
        ("instagram", "Instagram DM"),
        ("map-pin", "Google Maps"),
        ("phone", "Voz"),
    ]
    channels_html = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:5px;padding:3px 10px;margin:2px;'
        f'background:rgba(43,117,81,.15);border:1px solid rgba(43,117,81,.3);border-radius:99px;'
        f'font-size:.65rem;font-weight:600;color:#7DCF9E;letter-spacing:.04em;">'
        f'{_icon(nm, 13, "#7DCF9E")}{lbl}</span>'
        for nm, lbl in _channels
    )
    st.markdown(
        f'<div style="background:#0A1A11;border-radius:18px;padding:22px;color:#fff;'
        f'overflow:hidden;position:relative;">'
        # glow
        f'<div style="position:absolute;top:-60px;right:-60px;width:220px;height:220px;'
        f'background:radial-gradient(circle,rgba(43,117,81,.28) 0%,transparent 70%);'
        f'border-radius:50%;pointer-events:none;"></div>'
        # hero row: image + identity
        f'<div style="display:flex;align-items:center;gap:16px;margin-bottom:18px;">'
        f'<div style="flex-shrink:0;background:rgba(43,117,81,.1);border-radius:50%;'
        f'padding:10px;box-shadow:0 0 0 2px rgba(43,117,81,.25),0 0 32px rgba(43,117,81,.18);">'
        f'{_av}</div>'
        f'<div style="flex:1;min-width:0;">'
        f'<div style="font-family:\'Syne\',sans-serif;font-size:2.1rem;font-weight:800;'
        f'color:#fff;letter-spacing:.06em;line-height:1;margin-bottom:3px;'
        f'text-shadow:0 0 28px rgba(43,117,81,.5);">SCUFFI</div>'
        f'<div style="font-size:.68rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;'
        f'color:rgba(255,255,255,.4);margin-bottom:8px;line-height:1.35;">Superhéroe de CX · Scuffers · 24/7</div>'
        f'<div style="display:inline-flex;align-items:center;gap:6px;background:#1A7F4E;'
        f'padding:4px 11px;border-radius:99px;border:1px solid rgba(255,255,255,.1);">'
        f'<span style="width:6px;height:6px;border-radius:50%;background:#7DCF9E;'
        f'box-shadow:0 0 0 2px rgba(125,207,158,.25);flex-shrink:0;"></span>'
        f'<span style="font-size:.6rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase;'
        f'color:#fff;">NO SOLO CONTESTA: RESUELVE</span>'
        f'</div>'
        f'</div>'
        f'</div>'
        # superpowers grid
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:7px;margin-bottom:16px;">'
        f'{pow_html}'
        f'</div>'
        # channels
        f'<div style="padding-top:12px;border-top:1px solid rgba(255,255,255,.07);">'
        f'<div style="font-size:.56rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;'
        f'color:rgba(255,255,255,.3);margin-bottom:6px;">Canales activos</div>'
        f'{channels_html}'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

with col_chat:
    # Animated chat demo (self-contained HTML iframe)
    av_tag = (f'<img src="{_SS}" style="width:100%;height:100%;object-fit:contain;">'
              if _SS else "S")
    chat_css = (
        "* { box-sizing:border-box; margin:0; padding:0; }"
        "body { font-family:'Segoe UI',sans-serif; background:#F8F8F6; padding:18px; }"
        ".chat-hdr { display:flex; align-items:center; gap:10px; padding-bottom:12px;"
        "  border-bottom:1px solid #E5E5E5; margin-bottom:16px; }"
        ".dot { width:8px; height:8px; background:#2B7551; border-radius:50%;"
        "  animation:blink 1.5s ease-in-out infinite; box-shadow:0 0 0 3px rgba(43,117,81,.15); }"
        ".hdr-name { font-weight:700; font-size:.9rem; color:#0D0D0D; }"
        ".hdr-st { font-size:.68rem; color:#2B7551; font-weight:500; }"
        ".hdr-demo { margin-left:auto; font-size:.65rem; color:#9CA3AF; }"
        ".row { display:flex; gap:8px; margin-bottom:12px; align-items:flex-end; }"
        ".row-r { flex-direction:row-reverse; }"
        ".av { width:30px; height:30px; border-radius:50%; background:#DBE9E3; flex-shrink:0;"
        "  display:flex; align-items:center; justify-content:center; overflow:hidden; font-weight:700; font-size:12px; color:#2B7551; }"
        ".bbl { max-width:78%; padding:10px 13px; font-size:.8rem; line-height:1.55; border-radius:14px; }"
        ".bbl-l { background:#fff; border:1px solid #E5E5E5; border-radius:4px 14px 14px 14px; color:#0D0D0D; }"
        ".bbl-r { background:#2B7551; color:#fff; border-radius:14px 4px 14px 14px; }"
        ".bbl-r strong { color:#A3D4B8; }"
        "@keyframes chatL { from { opacity:0; transform:translateX(-14px); } to { opacity:1; transform:translateX(0); } }"
        "@keyframes chatR { from { opacity:0; transform:translateX(14px); } to { opacity:1; transform:translateX(0); } }"
        "@keyframes blink { 0%,100% { opacity:1; } 50% { opacity:.3; } }"
        ".m1 { animation:chatR .5s .4s ease both; }"
        ".m2 { animation:chatL .5s 1.4s ease both; }"
        ".m3 { animation:chatR .5s 2.8s ease both; }"
        ".m4 { animation:chatL .5s 4.0s ease both; }"
        ".m5 { animation:chatL .5s 6.2s ease both; }"
    )
    chat_body = (
        '<div class="chat-hdr">'
        '<div class="dot"></div>'
        '<div><div class="hdr-name">Scuffi</div><div class="hdr-st">● en línea · resolviendo</div></div>'
        '<div class="hdr-demo">DEMO EN VIVO</div>'
        '</div>'
        '<div class="row row-r m1">'
        '<div class="bbl bbl-r"><span style="display:inline-flex;vertical-align:middle;margin-right:6px;line-height:0;">'
        + _icon("triangle-alert", 16, "#FFFFFF")
        + '</span>Llevo 2 semanas esperando mi pedido y el tracking no se actualiza. Esto es una broma.</div>'
        '</div>'
        '<div class="row m2">'
        '<div class="av">' + av_tag + '</div>'
        '<div class="bbl bbl-l">¡Hola! Soy Scuffi. Entiendo perfectamente la frustración. Dame un segundo para localizar tu pedido ahora mismo. ¿Me dices tu número de pedido o el email con el que compraste?</div>'
        '</div>'
        '<div class="row row-r m3">'
        '<div class="bbl bbl-r">Es el #SCF-2025-0842, email sergio@gmail.com</div>'
        '</div>'
        '<div class="row m4">'
        '<div class="av">' + av_tag + '</div>'
        '<div class="bbl bbl-l">¡Ya lo tengo! Tu pedido está en tránsito — hubo una incidencia en el hub de MRW. He marcado tu caso como <strong>PRIORITARIO</strong> y el equipo logístico te contactará hoy antes de las 18h con solución definitiva.</div>'
        '</div>'
        '<div class="row m5">'
        '<div class="av">' + av_tag + '</div>'
        '<div class="bbl bbl-l">Además: si no se resuelve en 48h, te reenvío el artículo con envío exprés gratis <em>o</em> te hago el reembolso completo — tú eliges. Scuffi no cierra el caso hasta que esté resuelto. '
        + '<span style="display:inline-flex;vertical-align:middle;margin-left:3px;line-height:0;">'
        + _icon("check", 15, "#0D0D0D")
        + "</span></div>"
        '</div>'
    )
    chat_html = (
        '<!DOCTYPE html><html><head><meta charset="utf-8">'
        '<style>' + chat_css + '</style></head>'
        '<body>' + chat_body + '</body></html>'
    )
    _comps.html(chat_html, height=430, scrolling=False)

# Multichannel tabs
st.markdown(
    '<div style="font-family:\'Syne\',sans-serif;font-size:.85rem;font-weight:700;'
    'text-transform:uppercase;letter-spacing:.1em;color:#9CA3AF;margin:1.5rem 0 .75rem;">'
    'Canales donde Scuffi resuelve</div>',
    unsafe_allow_html=True,
)

tab_ig, tab_maps, tab_voice = st.tabs(
    ["Instagram DM", "Google Maps · Reseñas", "Voz (concepto · Fase 3)"]
)

# ── Instagram DM ──────────────────────────────────────────────────────────────
with tab_ig:
    css_ig = (
        "* { box-sizing:border-box; margin:0; padding:0; }"
        "body { font-family:'Segoe UI',sans-serif; background:#fff; padding:16px 16px 20px; }"
        ".hd { display:flex; align-items:center; gap:10px; padding-bottom:10px; border-bottom:1px solid #E5E5E5; margin-bottom:14px; }"
        ".hd-av { width:32px; height:32px; border-radius:50%; background:linear-gradient(135deg,#F58529,#DD2A7B,#8134AF); flex-shrink:0; }"
        ".hd-name { font-weight:700; font-size:.85rem; } .hd-handle { font-size:.68rem; color:#9CA3AF; }"
        ".row { display:flex; gap:8px; margin-bottom:9px; align-items:flex-end; }"
        ".row-r { flex-direction:row-reverse; }"
        ".av { width:24px; height:24px; border-radius:50%; background:#E5E5E5; display:flex; align-items:center; justify-content:center; font-size:.58rem; font-weight:700; color:#6B7280; flex-shrink:0; }"
        ".bbl { max-width:72%; padding:7px 11px; font-size:.78rem; line-height:1.5; border-radius:16px; }"
        ".bbl-l { background:#F3F4F6; color:#0D0D0D; }"
        ".bbl-r { background:#2B7551; color:#fff; }"
        ".tag { display:inline-block; background:#E0F0E8; color:#245542; font-size:.58rem; font-weight:700; padding:2px 7px; border-radius:99px; margin-top:3px; }"
        ".res { background:#F1F7F4; border:1px solid #C5DED2; border-radius:8px; padding:10px 12px 11px; margin-top:12px; margin-bottom:4px; font-size:.72rem; color:#245542; font-weight:600; line-height:1.45; display:flex; align-items:center; flex-wrap:wrap; gap:8px; }"
    )
    body_ig = (
        '<div class="hd"><div class="hd-av"></div>'
        '<div><div class="hd-name">sofia_madrid_</div><div class="hd-handle">@sofia_madrid_</div></div></div>'
        '<div class="row"><div class="av">SM</div>'
        '<div><div class="bbl bbl-l">hola!! pedí talla 40 pero leí que son oversized... ¿debería haber pedido 39?</div>'
        '<div class="tag">Intent: Tallas/Ajuste</div></div></div>'
        '<div class="row row-r"><div class="av" style="background:#DBE9E3;color:#2B7551;">S</div>'
        '<div class="bbl bbl-r">¡Hola Sofia! Sí, los diseños Scuffers son oversize. Si normalmente usas 40, el 39 quedará más ajustado. Te recomiendo la guía de tallas de la ficha del producto. ¿Quieres que te ayude con el cambio?</div></div>'
        '<div class="row"><div class="av">SM</div>'
        '<div class="bbl bbl-l">sí por favor ¿cómo lo hago?</div></div>'
        '<div class="row row-r"><div class="av" style="background:#DBE9E3;color:#2B7551;">S</div>'
        '<div class="bbl bbl-r">Perfecto: tienes dos opciones — hacerlo manual en returns.reveni.io/scuffers con tu nº de pedido (el primer cambio en España es gratuito), o entrar en scuffers.com y que Scuffi lo resuelva por ti. En cuanto recibamos el 40 te enviamos el 39. ¡Resuelto!</div></div>'
        '<div class="res"><span style="display:inline-flex;line-height:0;">'
        + _icon("check", 16, "#245542")
        + '</span> Resuelto · 2 min 14 seg · sin escalado · <span class="tag" style="margin:0;">Tallas/Ajuste</span></div>'
    )
    _comps.html(
        '<!DOCTYPE html><html><head><meta charset="utf-8"><style>' + css_ig + '</style></head>'
        '<body>' + body_ig + '</body></html>',
        height=420, scrolling=False,
    )

# ── Google Maps ────────────────────────────────────────────────────────────────
with tab_maps:
    st.markdown(
        '<div class="review-card">'
        '<div class="review-stars">★☆☆☆☆</div>'
        '<div class="review-meta">Carlos M. · hace 3 días · Google Maps</div>'
        '<div class="review-text">"Pésima atención al cliente. Llevo dos semanas intentando gestionar una devolución y nadie responde. Muy decepcionante para una marca con estas pretensiones."</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    if st.session_state.review_st == "initial":
        if st.button("Generar respuesta con Scuffi", key="gen_review"):
            st.session_state.review_st = "drafted"
            st.rerun()
    elif st.session_state.review_st == "drafted":
        draft = (
            "Hola Carlos, sentimos mucho que tu experiencia no haya estado a la altura. "
            "Las devoluciones se procesan en hasta 14 días desde la recepción — lamentamos que la comunicación no haya sido clara. "
            "Por favor, contáctanos directamente por chat con tu nº de pedido y lo gestionamos de forma inmediata. "
            "Valoramos tu paciencia.\n— Scuffi · Equipo Scuffers"
        )
        draft_html = re.sub(r'\n', '<br>', draft)
        st.markdown(
            '<div class="draft-card"><div class="draft-label">'
            + _icon("bot", 15, "#2B7551")
            + " Scuffi · Borrador generado en 1.2s</div>"
            f'<div class="draft-text">{draft_html}</div></div>',
            unsafe_allow_html=True,
        )
        ba, be, _ = st.columns([1, 1, 2])
        with ba:
            if st.button("Aprobar y publicar", key="approve_review"):
                st.session_state.review_st = "approved"; st.rerun()
        with be:
            if st.button("Descartar", key="discard_review"):
                st.session_state.review_st = "initial"; st.rerun()
    elif st.session_state.review_st == "approved":
        draft = ("Hola Carlos, sentimos mucho que tu experiencia no haya estado a la altura. "
                 "Las devoluciones se procesan en hasta 14 días desde la recepción — lamentamos que la comunicación no haya sido clara. "
                 "Por favor, contáctanos directamente por chat con tu nº de pedido y lo gestionamos de forma inmediata. "
                 "Valoramos tu paciencia.\n— Scuffi · Equipo Scuffers")
        draft_html = re.sub(r'\n', '<br>', draft)
        st.markdown(
            '<div class="draft-card"><div class="draft-label" style="color:#245542;">'
            + _icon("check", 15, "#245542")
            + " Respuesta publicada · hace un momento</div>"
            f'<div class="draft-text">{draft_html}</div></div>',
            unsafe_allow_html=True,
        )
        if st.button("Nueva reseña", key="reset_review"):
            st.session_state.review_st = "initial"; st.rerun()

# ── Voice ──────────────────────────────────────────────────────────────────────
with tab_voice:
    wave_html = "".join(
        '<div class="wave-bar" style="height:' + str(h) + 'px;"></div>'
        for h in [10, 18, 26, 34, 38, 34, 26, 18, 10]
    )
    feats = [
        (_icon("mic", 18, "#7DCF9E"), "Reconocimiento de intent por voz"),
        (_icon("volume-2", 18, "#7DCF9E"), "Respuesta sintetizada (TTS) personalizada"),
        (_icon("arrow-up-right", 18, "#7DCF9E"), "Escalado a humano cuando la complejidad lo requiere"),
        (_icon("clipboard-list", 18, "#7DCF9E"), "Registro post-llamada automático en CRM"),
    ]
    feats_html = "".join(
        '<div style="display:flex;align-items:flex-start;gap:10px;margin-bottom:10px;">'
        f'<span style="display:inline-flex;flex-shrink:0;line-height:0;">{ic}</span>'
        f'<span style="font-size:.8rem;color:#D1FAE5;line-height:1.5;">{txt}</span>'
        '</div>'
        for ic, txt in feats
    )
    st.markdown(
        '<div class="voice-card">'
        '<div class="voice-phase-badge">Roadmap · Fase 3+</div>'
        '<div style="font-family:Syne,sans-serif;font-size:1.2rem;font-weight:700;margin-bottom:5px;">Scuffi Voz · Canal telefónico</div>'
        '<div style="font-size:.8rem;color:#9CA3AF;margin-bottom:4px;">Mismo motor de resolución — canal telefónico. En roadmap.</div>'
        f'<div class="waveform">{wave_html}</div>'
        f'<div>{feats_html}</div>'
        '</div>',
        unsafe_allow_html=True,
    )


# =============================================================================
# SECTION 4 — PROYECCIÓN DE IMPACTO
# =============================================================================
st.markdown(
    '<div class="sec-hdr">'
    '<span class="sec-num">04</span>'
    '<h2 class="sec-ttl">PROYECCIÓN DE IMPACTO CON SCUFFI</h2>'
    '<div class="sec-line"></div>'
    '</div>',
    unsafe_allow_html=True,
)

months_p  = list(range(0, 19))
sin_ia    = [round(avg_rating - i * 0.04, 2) for i in range(19)]
con_ia    = [2.5, 2.5, 2.6, 2.75, 2.9, 3.1, 3.25, 3.4, 3.55,
             3.65, 3.75, 3.85, 3.95, 4.05, 4.15, 4.25, 4.35, 4.42, 4.5]

fig_proj = go.Figure()
fig_proj.add_trace(go.Scatter(
    x=months_p, y=sin_ia, name="Sin cambios (tendencia actual)",
    mode="lines", line=dict(color="#D1D5DB", width=2, dash="dash"),
    fill="tozeroy", fillcolor="rgba(220,38,38,.04)",
    hovertemplate="Mes %{x}: %{y:.1f}★<extra>Sin IA</extra>",
))
fig_proj.add_trace(go.Scatter(
    x=months_p, y=con_ia, name="Con Scuffi",
    mode="lines+markers", line=dict(color="#2B7551", width=3),
    marker=dict(size=5, color="#2B7551"),
    fill="tozeroy", fillcolor="rgba(43,117,81,.07)",
    hovertemplate="Mes %{x}: %{y:.1f}★<extra>Con Scuffi</extra>",
))
for mx, my, mlbl in [
    (2,  con_ia[2],  "Scuffi Live"),
    (6,  con_ia[6],  "3.25★"),
    (12, con_ia[12], "4.0★ · hito"),
    (18, con_ia[18], "4.5★ · meta"),
]:
    fig_proj.add_annotation(
        x=mx, y=my, text=f"<b>{mlbl}</b>", showarrow=True,
        arrowhead=0, arrowcolor="#2B7551", arrowwidth=1, ay=-32, ax=0,
        font=dict(size=12, color="#2B7551", family="DM Sans"),
        bgcolor="rgba(240,253,244,.9)", bordercolor="rgba(43,117,81,.3)",
        borderwidth=1, borderpad=4,
    )
fig_proj.add_hline(y=4.0, line=dict(color="rgba(43,117,81,.2)", dash="dot", width=1))
fig_proj.add_hline(y=avg_rating, line=dict(color="rgba(220,38,38,.15)", dash="dot", width=1))
fig_proj.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(248,248,246,1)",
    xaxis=dict(
        title=dict(
            text="Meses desde implementación",
            font=dict(size=14, color="#4B5563", family="DM Sans"),
        ),
        gridcolor="rgba(0,0,0,.05)",
        color="#6B7280",
        tickfont=dict(color="#374151", size=13),
    ),
    yaxis=dict(
        title=dict(
            text="Rating Google Maps (★)",
            font=dict(size=14, color="#4B5563", family="DM Sans"),
        ),
        range=[1, 5],
        gridcolor="rgba(0,0,0,.05)",
        color="#6B7280",
        tickfont=dict(color="#374151", size=13),
    ),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#4B5563", size=12), y=0.05, x=0.02),
    margin=dict(t=34, b=52, l=62, r=24),
    height=340,
    hoverlabel=dict(bgcolor="#fff", bordercolor="#E5E5E5", font=dict(color="#0D0D0D", size=12)),
)
st.plotly_chart(fig_proj, use_container_width=True)

# Projection numbers
pn1, pn2, pn3, pn4 = st.columns(4)
proj_items = [
    ("< 1 min", "Tiempo de 1ª respuesta", "vs ~18h actuales"),
    ("87%", "Consultas resueltas sin escalado", "vs 41% sin Scuffi"),
    ("4.5★", "Objetivo rating mes 18", "desde {:.1f}★ actual".format(avg_rating)),
    (f"€{total_impacto // 1000}k+", "Revenue desbloqueado/año", "Ingresos en riesgo recuperados"),
]
for col, (val, lbl, sub) in zip([pn1, pn2, pn3, pn4], proj_items):
    with col:
        st.markdown(
            f'<div class="proj-card">'
            f'<div class="proj-num">{val}</div>'
            f'<div style="font-size:.75rem;font-weight:600;color:#0D0D0D;margin:.3rem 0 .2rem;">{lbl}</div>'
            f'<div class="proj-lbl">{sub}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


_render_section_data_analytics()

_render_footer()
