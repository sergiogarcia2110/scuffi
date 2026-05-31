# drop_hype_monitor_final.py  ·  Drop Hype Monitor Demo · Scuffers
# Run: python3 -m streamlit run drop_hype_monitor_final.py

import io, base64, functools
from pathlib import Path
import streamlit as st
import plotly.graph_objects as go
import streamlit.components.v1 as _comps
from PIL import Image as _PILImg


# ─── LUCIDE ICONS ─────────────────────────────────────────────────────────────
def _lucide_svg(inner, *, size=16, color="currentColor", stroke=2, extra_class=""):
    cls = ("lucide " + extra_class).strip()
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        f'fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" '
        f'stroke-linejoin="round" class="{cls}">{inner}</svg>'
    )

_L = {
    "flame":        '<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 3z"/>',
    "trending-up":  '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>',
    "bell":         '<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>',
    "alert-triangle":'<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    "map-pin":      '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "bar-chart-2":  '<line x1="18" x2="18" y1="20" y2="10"/><line x1="12" x2="12" y1="20" y2="4"/><line x1="6" x2="6" y1="20" y2="14"/>',
    "zap":          '<path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.81a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.81a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"/>',
    "arrow-right":  '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    "check":        '<path d="M20 6 9 17l-5-5"/>',
    "eye":          '<path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>',
    "database":     '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19A9 3 0 0 0 21 19V5"/><path d="M3 12A9 3 0 0 0 21 12"/>',
    "file-text":    '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/>',
}

def _icon(name, size=16, color="currentColor", **kw):
    return _lucide_svg(_L.get(name, ""), size=size, color=color, **kw)


# ─── LOGO HANDLING ─────────────────────────────────────────────────────────────
@functools.lru_cache(maxsize=1)
def _fallback_page_icon_path():
    p = Path(__file__).resolve().parent / "_hype_tab_fallback.png"
    if not p.is_file():
        im = _PILImg.new("RGBA", (64, 64), (0, 0, 0, 0))
        from PIL import ImageDraw
        d = ImageDraw.Draw(im)
        d.ellipse([8, 8, 56, 56], fill=(249, 115, 22, 255))
        im.save(p, "PNG")
    return str(p)


@functools.lru_cache(maxsize=1)
def _logo_assets():
    try:
        img = _PILImg.open("logo.png").convert("RGBA")
    except Exception:
        return None, "", ""
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)

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

    return "logo.png", _b64_url(_resize_max_h(img.copy(), 22)), _b64_url(_resize_max_h(img.copy(), 18))


_LOG_FAV, _LOGO_NAV, _LOGO_FOOT = _logo_assets()

# ─── ACCENT COLOR ─────────────────────────────────────────────────────────────
AC   = "#F97316"   # orange
AC_D = "#EA6A04"
AC_L = "#FFF7ED"
AC_B = "#FED7AA"

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Drop Hype Monitor · Demo",
    page_icon=_LOG_FAV if _LOG_FAV else _fallback_page_icon_path(),
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── SIMULATED DATA ───────────────────────────────────────────────────────────
DAYS          = ["-7d", "-6d", "-5d", "-4d", "-3d", "-2d", "-1d", "HOY"]
HYPE_CURR     = [14,  22,  31,  47,  58,  76,  89, 100]
HYPE_PREV     = [11,  19,  28,  40,  52,  68,  81,  95]
IG_MENTIONS   = [45,  68,  92, 145, 198, 287, 412, 634]
TT_MENTIONS   = [18,  34,  52,  98, 156, 234, 389, 578]
X_MENTIONS    = [ 8,  14,  22,  38,  58,  82, 124, 187]
RD_MENTIONS   = [ 3,   6,   9,  14,  21,  29,  38,  52]
GT_SCORES     = [12,  18,  28,  42,  56,  71,  84,  96]

TOTAL_TODAY   = 634 + 578 + 187 + 52   # 1451
PREV_TOTAL    = 487 + 423 + 156 + 43   # 1109

HYPE_SCORE    = 89
HYPE_PREV_NOW = 81
PREDICTED_GMV = "42.000–48.000€"
PREV_GMV      = "31.200€"

ALERTS = [
    {"time": "hace 2h",   "severity": "high",   "icon": "zap",           "color": "#EF4444", "bg": "#FEF2F2", "border": "#FECACA",
     "title": "Pico viral en TikTok",           "msg": "+340% menciones en 1h · 389 vídeos nuevos con el hashtag #DropSombra"},
    {"time": "hace 6h",   "severity": "good",   "icon": "check",         "color": "#22C55E", "bg": "#F0FDF4", "border": "#BBF7D0",
     "title": "Mención orgánica de influencer", "msg": "Nathy Peluso mencionó el Drop Sombra en Instagram Stories · 2.3M seguidores"},
    {"time": "hace 14h",  "severity": "medium", "icon": "eye",           "color": AC,        "bg": AC_L,      "border": AC_B,
     "title": "Leak detectado",                 "msg": "Fotos no oficiales de la hoodie circulando en Reddit · 234 upvotes · Evaluando impacto"},
    {"time": "ayer",      "severity": "low",    "icon": "alert-triangle","color": "#F59E0B", "bg": "#FFFBEB", "border": "#FDE68A",
     "title": "Sentimiento negativo detectado", "msg": "5 comentarios críticos sobre precio en Instagram · 0.3% del total de menciones"},
]

CITIES = {"Madrid": 434, "Barcelona": 287, "Valencia": 198, "Sevilla": 134,
          "Bilbao": 98,  "Málaga": 78,   "Zaragoza": 63, "Otros": 159}

TOP_WORDS = [("DROP SOMBRA", 342), ("SCUFFERS", 289), ("VIERNES", 234), ("LIMITED", 198),
             ("OVERSIZED", 167), ("SOLD OUT", 145), ("MADRID", 134), ("HYPE", 123),
             ("HOODIE", 112), ("NATHY", 98)]

SENTIMIENTO = {"Positivo · Hype": 68, "Neutral · Expectativa": 22, "Negativo · Crítica": 10}

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');
#MainMenu,footer{{visibility:hidden!important}}
header[data-testid="stHeader"]{{display:none!important}}
[data-testid="stToolbar"],.stDeployButton,[data-testid="stToolbarActions"]{{display:none!important}}
html,body,[class*="css"]{{font-family:'DM Sans',sans-serif;background:#fff;color:#0D0D0D}}
.main .block-container{{padding-top:1.5rem;padding-bottom:4rem;max-width:1200px}}
.sec-hdr{{display:flex;align-items:center;gap:14px;margin:44px 0 20px}}
.sec-num{{font-family:'Syne',sans-serif;font-size:.8rem;font-weight:800;color:#D1D5DB;letter-spacing:.08em}}
.sec-ttl{{font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;color:#0D0D0D;margin:0;letter-spacing:.02em}}
.sec-line{{flex:1;height:1px;background:linear-gradient(90deg,#E5E5E5,transparent)}}
.demo-badge{{display:inline-flex;align-items:center;gap:8px;background:#F3F4F6;color:#9CA3AF;font-size:.68rem;font-weight:600;letter-spacing:.06em;padding:3px 10px;border-radius:99px}}
.lucide{{display:inline-block;vertical-align:middle;flex-shrink:0}}
.kpi-card{{background:#F8F8F6;border:1px solid #EBEBEB;border-radius:12px;padding:18px 20px;text-align:center;height:100%}}
.kpi-lbl{{font-size:.65rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:#9CA3AF;margin-bottom:6px}}
.kpi-val{{font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;line-height:1;margin-bottom:4px}}
.kpi-sub{{font-size:.72rem;color:#9CA3AF}}
.kpi-card.orange{{border-top:3px solid {AC}}}
.kpi-card.green{{border-top:3px solid #22C55E}}
.kpi-card.blue{{border-top:3px solid #3B82F6}}
.alert-card{{border:1.5px solid;border-radius:12px;padding:14px 16px;margin-bottom:10px;display:flex;gap:14px;align-items:flex-start}}
.alert-time{{font-size:.65rem;color:#9CA3AF;white-space:nowrap;margin-top:2px}}
.alert-title{{font-size:.82rem;font-weight:700;color:#0D0D0D;margin-bottom:3px}}
.alert-msg{{font-size:.75rem;color:#6B7280;line-height:1.45}}
.word-chip{{display:inline-block;padding:4px 10px;margin:3px;border-radius:99px;font-size:.72rem;font-weight:700;letter-spacing:.04em}}
.report-card{{background:#0D0D0D;border-radius:16px;padding:24px 28px;color:#fff}}
.stTabs [data-baseweb="tab-list"]{{gap:0;border-bottom:1px solid #E5E5E5}}
.stTabs [data-baseweb="tab"]{{font-size:.82rem;font-weight:500;color:#6B7280;padding:10px 20px;border-bottom:2px solid transparent}}
.stTabs [aria-selected="true"]{{color:{AC}!important;border-bottom-color:{AC}!important;font-weight:600!important}}
</style>
""", unsafe_allow_html=True)


# ─── NAVBAR ───────────────────────────────────────────────────────────────────
_nav_logo = f'<img src="{_LOGO_NAV}" alt="Scuffers" style="height:22px;width:auto;vertical-align:middle;margin-right:10px;">' if _LOGO_NAV else ""
_hl, _ = st.columns([3, 1], gap="medium")
with _hl:
    st.markdown(
        f'<div style="padding:6px 0 10px;"><div style="display:flex;align-items:center;flex-wrap:wrap;gap:14px;">'
        f'<div style="font-family:\'Syne\',sans-serif;font-size:1rem;font-weight:800;letter-spacing:.04em;display:flex;align-items:center;">'
        f'{_nav_logo}DROP HYPE MONITOR <span style="font-weight:400;color:#9CA3AF;font-size:.85rem;">· Sentimiento Pre-Drop en Tiempo Real</span></div>'
        f'<div class="demo-badge">{_icon("flame",14,"#9CA3AF")} Demo · Drop Sombra · 48h antes del lanzamiento</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )
st.markdown('<div style="border-bottom:1px solid #E5E5E5;margin:0 0 10px 0;"></div>', unsafe_allow_html=True)


def _footer():
    _fl = f'<img src="{_LOGO_FOOT}" alt="" style="height:18px;width:auto;vertical-align:middle;margin-right:8px;">' if _LOGO_FOOT else ""
    st.markdown(
        f'<div style="text-align:center;margin-top:3rem;padding-top:1.5rem;border-top:1px solid #E5E5E5;'
        f'font-size:.68rem;color:#9CA3AF;letter-spacing:.06em;display:flex;align-items:center;justify-content:center;gap:4px;">'
        f'{_fl}DROP HYPE MONITOR · Demo · Fase 1 Quick Win · ~125€/mes</div>',
        unsafe_allow_html=True,
    )


# =============================================================================
# HERO — HYPE SCORE + KPIs
# =============================================================================
st.markdown('<div style="padding:1.8rem 0 1.2rem;">', unsafe_allow_html=True)
hero_l, hero_m, hero_r = st.columns([1.2, 1, 1])

with hero_l:
    st.markdown(
        f'<div style="font-size:.68rem;font-weight:700;letter-spacing:.16em;text-transform:uppercase;'
        f'color:{AC};margin-bottom:.8rem;display:flex;align-items:center;gap:8px;">'
        f'<span style="display:inline-block;width:20px;height:2px;background:{AC};"></span>FASE 1 · QUICK WIN · ~125€/MES</div>'
        '<div style="font-family:\'Syne\',sans-serif;font-size:clamp(1.8rem,3vw,2.7rem);font-weight:800;'
        'line-height:1.15;color:#0D0D0D;margin-bottom:1rem;">'
        f'Cuantifica la anticipación<br><span style="color:{AC};">antes del drop,</span><br>'
        '<span style="font-size:.55em;font-weight:400;color:#6B7280;">no después.</span></div>'
        '<div style="font-size:.9rem;color:#6B7280;line-height:1.65;max-width:420px;">'
        'El éxito de un drop se fragua en las semanas anteriores. El Hype Monitor cuantifica esa '
        f'anticipación en tiempo real para que el equipo <strong style="color:#0D0D0D;">reaccione antes del lanzamiento.</strong></div>',
        unsafe_allow_html=True,
    )

with hero_m:
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=HYPE_SCORE,
        title={"text": "Hype Score · Drop Sombra", "font": {"color": "#9CA3AF", "size": 11, "family": "DM Sans"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#E5E5E5", "tickfont": {"color": "#D1D5DB", "size": 10},
                     "tickvals": [0, 25, 50, 75, 100]},
            "bar": {"color": AC, "thickness": 0.22},
            "bgcolor": "rgba(0,0,0,0)", "bordercolor": "#E5E5E5", "borderwidth": 1,
            "steps": [
                {"range": [0, 33],   "color": "rgba(229,231,235,.3)"},
                {"range": [33, 66],  "color": "rgba(249,115,22,.06)"},
                {"range": [66, 100], "color": "rgba(249,115,22,.12)"},
            ],
        },
        number={"font": {"color": AC, "size": 46, "family": "Syne"}, "suffix": "/100"},
    ))
    fig_gauge.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#6B7280"}, margin=dict(t=30, b=10, l=30, r=30), height=250,
    )
    st.plotly_chart(fig_gauge, use_container_width=True)
    st.markdown(
        f'<div style="text-align:center;margin-top:-8px;font-size:.62rem;color:#9CA3AF;letter-spacing:.1em;text-transform:uppercase;">'
        f'vs. drop anterior: {HYPE_PREV_NOW}/100 en este punto · <span style="color:#22C55E;">+{HYPE_SCORE - HYPE_PREV_NOW}pts</span></div>',
        unsafe_allow_html=True,
    )

with hero_r:
    for val, lbl, sub, color, cls in [
        (f"{TOTAL_TODAY:,}", "Menciones hoy",       f"+{int((TOTAL_TODAY/PREV_TOTAL - 1)*100)}% vs drop anterior", AC, "orange"),
        (PREDICTED_GMV,      "Predicción GMV",       f"1ª hora · vs {PREV_GMV} drop anterior", "#22C55E", "green"),
        ("48h",              "Informe pre-drop",      "Generado automáticamente por Claude API", "#3B82F6", "blue"),
    ]:
        st.markdown(f'<div class="kpi-card {cls}" style="margin-bottom:10px;"><div class="kpi-lbl">{lbl}</div><div class="kpi-val" style="color:{color};">{val}</div><div class="kpi-sub">{sub}</div></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


# =============================================================================
# SECTION 01 — HYPE SCORE TIMELINE
# =============================================================================
st.markdown('<div class="sec-hdr"><span class="sec-num">01</span><h2 class="sec-ttl">HYPE SCORE · 7 DÍAS PRE-DROP</h2><div class="sec-line"></div></div>', unsafe_allow_html=True)

fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(
    x=DAYS, y=HYPE_PREV, name="Drop Verano 2026 (anterior)",
    mode="lines", line=dict(color="#D1D5DB", width=2, dash="dash"),
    hovertemplate="Día %{x}: %{y}/100<extra>Verano 2026</extra>",
))
fig_trend.add_trace(go.Scatter(
    x=DAYS, y=HYPE_CURR, name="Drop Sombra (actual)",
    mode="lines+markers", line=dict(color=AC, width=3),
    marker=dict(size=6, color=AC),
    fill="tozeroy", fillcolor="rgba(249,115,22,.06)",
    hovertemplate="Día %{x}: %{y}/100<extra>Drop Sombra</extra>",
))
for day, val, lbl in [("-5d", 31, "Teaser IG"), ("-2d", 76, "Leak viral"), ("HOY", 100, "48h al drop")]:
    fig_trend.add_annotation(
        x=day, y=val, text=f"<b>{lbl}</b>", showarrow=True, arrowhead=0,
        arrowcolor=AC, arrowwidth=1, ay=-32, ax=0,
        font=dict(size=11, color=AC, family="DM Sans"),
        bgcolor="rgba(255,247,237,.9)", bordercolor=AC_B, borderwidth=1, borderpad=4,
    )
fig_trend.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(248,248,246,1)",
    xaxis=dict(gridcolor="rgba(0,0,0,.04)", tickfont=dict(color="#374151", size=12)),
    yaxis=dict(title=dict(text="Hype Score (0–100)", font=dict(size=12, color="#4B5563")),
               range=[0, 115], gridcolor="rgba(0,0,0,.04)", tickfont=dict(color="#6B7280", size=11)),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#374151", size=12), y=0.05, x=0.01),
    margin=dict(t=24, b=12, l=52, r=24), height=300,
    hoverlabel=dict(bgcolor="#fff", bordercolor="#E5E5E5", font=dict(color="#0D0D0D", size=12)),
)
st.plotly_chart(fig_trend, use_container_width=True)

total_mentions_by_day = [sum(x) for x in zip(IG_MENTIONS, TT_MENTIONS, X_MENTIONS, RD_MENTIONS)]
col_t1, col_t2, col_t3 = st.columns(3)
for col, (val, lbl, sub, color) in zip([col_t1, col_t2, col_t3], [
    (f"{TOTAL_TODAY:,}", "Menciones totales hoy",   "Instagram + TikTok + X + Reddit", AC),
    (f"{HYPE_SCORE}",    "Hype Score actual",        f"+{HYPE_SCORE - HYPE_PREV_NOW}pts vs. mismo punto anterior drop", "#22C55E"),
    (f"{IG_MENTIONS[-1]}", "Menciones solo en IG",  "Mayor plataforma · +54% del total", "#E1306C"),
]):
    with col:
        st.markdown(
            f'<div style="background:#F8F8F6;border:1px solid #EBEBEB;border-radius:12px;padding:16px;text-align:center;">'
            f'<div style="font-family:\'Syne\',sans-serif;font-size:1.6rem;font-weight:800;color:{color};line-height:1;margin-bottom:4px;">{val}</div>'
            f'<div style="font-size:.75rem;font-weight:600;color:#0D0D0D;margin-bottom:2px;">{lbl}</div>'
            f'<div style="font-size:.65rem;color:#9CA3AF;">{sub}</div></div>',
            unsafe_allow_html=True,
        )


# =============================================================================
# SECTION 02 — PLATAFORMAS Y SENTIMIENTO
# =============================================================================
st.markdown('<div class="sec-hdr"><span class="sec-num">02</span><h2 class="sec-ttl">PLATAFORMAS Y SENTIMIENTO</h2><div class="sec-line"></div></div>', unsafe_allow_html=True)

col_plat, col_sent = st.columns([1.3, 1])

with col_plat:
    platforms = ["Reddit", "X / Twitter", "TikTok", "Instagram"]
    vals = [52, 187, 578, 634]
    colors = ["#FF6314", "#1D9BF0", "#010101", "#E1306C"]
    fig_plat = go.Figure(go.Bar(
        x=vals, y=platforms, orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{v:,} menciones" for v in vals], textposition="outside",
        textfont=dict(color="#1F2937", size=12),
        hovertemplate="<b>%{y}</b><br>%{x:,} menciones<extra></extra>",
    ))
    fig_plat.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,.05)", tickfont=dict(color="#6B7280", size=11), range=[0, 850]),
        yaxis=dict(showgrid=False, tickfont=dict(color="#111827", size=13)),
        margin=dict(t=20, b=20, l=8, r=130), height=240,
        title=dict(text="MENCIONES HOY POR PLATAFORMA", font=dict(size=11, color="#374151"), x=0),
    )
    st.plotly_chart(fig_plat, use_container_width=True)

with col_sent:
    sent_colors = ["#22C55E", "#F59E0B", "#EF4444"]
    fig_sent = go.Figure(go.Pie(
        labels=list(SENTIMIENTO.keys()), values=list(SENTIMIENTO.values()),
        marker=dict(colors=sent_colors, line=dict(color="#fff", width=2)),
        hole=0.5, textfont=dict(size=11),
        hovertemplate="<b>%{label}</b><br>%{value}%<extra></extra>",
    ))
    fig_sent.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", showlegend=True,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#374151", size=11)),
        margin=dict(t=20, b=8, l=8, r=8), height=220,
        title=dict(text="SENTIMIENTO HOY", font=dict(size=11, color="#374151"), x=0.02),
        annotations=[dict(text="68%<br>positivo", x=0.5, y=0.5, font_size=13, showarrow=False,
                          font_color="#22C55E", font_family="Syne")],
    )
    st.plotly_chart(fig_sent, use_container_width=True)


# =============================================================================
# SECTION 03 — ALERTAS EN TIEMPO REAL
# =============================================================================
st.markdown('<div class="sec-hdr"><span class="sec-num">03</span><h2 class="sec-ttl">ALERTAS EN TIEMPO REAL</h2><div class="sec-line"></div></div>', unsafe_allow_html=True)

col_al1, col_al2 = st.columns(2)
for i, alert in enumerate(ALERTS):
    col = col_al1 if i % 2 == 0 else col_al2
    with col:
        st.markdown(
            f'<div class="alert-card" style="background:{alert["bg"]};border-color:{alert["border"]};">'
            f'<div style="flex-shrink:0;margin-top:2px;">{_icon(alert["icon"], 18, alert["color"])}</div>'
            f'<div style="flex:1;">'
            f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:3px;">'
            f'<div class="alert-title">{alert["title"]}</div>'
            f'<div class="alert-time">{alert["time"]}</div></div>'
            f'<div class="alert-msg">{alert["msg"]}</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )


# =============================================================================
# SECTION 04 — GEOGRAFÍA Y PALABRAS CLAVE
# =============================================================================
st.markdown('<div class="sec-hdr"><span class="sec-num">04</span><h2 class="sec-ttl">GEOGRAFÍA Y PALABRAS CLAVE</h2><div class="sec-line"></div></div>', unsafe_allow_html=True)

col_geo, col_words = st.columns([1.2, 1])

with col_geo:
    cities = list(CITIES.keys())
    vals_geo = list(CITIES.values())
    max_v = max(vals_geo)
    colors_geo = [AC if v == max_v else "#E5E7EB" for v in vals_geo]
    fig_geo = go.Figure(go.Bar(
        x=vals_geo, y=cities, orientation="h",
        marker=dict(color=colors_geo, line=dict(width=0)),
        text=[f"{v}" for v in vals_geo], textposition="outside",
        textfont=dict(color="#1F2937", size=11),
        hovertemplate="<b>%{y}</b><br>%{x} menciones<extra></extra>",
    ))
    fig_geo.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,.05)", tickfont=dict(color="#6B7280", size=11), range=[0, 530]),
        yaxis=dict(showgrid=False, tickfont=dict(color="#111827", size=12)),
        margin=dict(t=20, b=12, l=8, r=60), height=280,
        title=dict(text="CONVERSACIÓN POR CIUDAD (España)", font=dict(size=11, color="#374151"), x=0),
    )
    st.plotly_chart(fig_geo, use_container_width=True)

with col_words:
    st.markdown(
        f'<div style="font-family:\'Syne\',sans-serif;font-size:.72rem;font-weight:800;text-transform:uppercase;'
        f'letter-spacing:.12em;color:#9CA3AF;margin-bottom:14px;">TOP PALABRAS ASOCIADAS AL DROP</div>',
        unsafe_allow_html=True,
    )
    max_count = TOP_WORDS[0][1]
    chips_html = ""
    for word, count in TOP_WORDS:
        intensity = count / max_count
        opacity = 0.15 + intensity * 0.85
        font_size = 0.68 + intensity * 0.22
        chips_html += (
            f'<span class="word-chip" style="background:rgba(249,115,22,{opacity:.2f});"'
            f' title="{count} menciones">'
            f'<span style="font-size:{font_size:.2f}rem;color:{"#fff" if intensity > 0.5 else "#7C2D12"};">{word}</span></span>'
        )
    st.markdown(
        f'<div style="background:#F8F8F6;border:1px solid #EBEBEB;border-radius:12px;padding:20px;min-height:160px;">'
        f'{chips_html}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div style="font-size:.65rem;color:#9CA3AF;margin-top:8px;">'
        f'Actualizado cada hora · {sum(c for _, c in TOP_WORDS):,} menciones analizadas hoy</div>',
        unsafe_allow_html=True,
    )


# =============================================================================
# SECTION 05 — INFORME PRE-DROP AUTO-GENERADO
# =============================================================================
st.markdown('<div class="sec-hdr"><span class="sec-num">05</span><h2 class="sec-ttl">INFORME PRE-DROP · GENERADO POR CLAUDE API</h2><div class="sec-line"></div></div>', unsafe_allow_html=True)

col_rep, col_pred = st.columns([1.5, 1])

with col_rep:
    report_items = [
        (AC,       "SITUACIÓN",     f"Hype Score {HYPE_SCORE}/100 (+{HYPE_SCORE - HYPE_PREV_NOW}pts vs. Drop Verano). {TOTAL_TODAY:,} menciones en las últimas 24h. Momentum positivo en todas las plataformas."),
        ("#22C55E","OPORTUNIDADES", "Mención orgánica de Nathy Peluso con 2.3M seguidores. Tendencia viral en TikTok con +340% de pico en 1h. Sentimiento positivo al 68%."),
        ("#F59E0B","RIESGOS",       "Leak de imágenes en Reddit (controlado). 5 comentarios sobre precio. Sin impacto significativo — el sentimiento neto sigue siendo muy positivo."),
        ("#3B82F6","RECOMENDACIONES","Publicar el teaser oficial esta tarde para capitalizar el pico orgánico. Activar early access OG/Founder a las 18:00h. No publicar precio hasta las 19:30h."),
    ]
    rep_html = ""
    for color, tag, text in report_items:
        rep_html += (
            f'<div style="display:flex;gap:12px;align-items:flex-start;margin-bottom:14px;">'
            f'<div style="background:{color};color:#fff;font-family:Syne,sans-serif;font-weight:800;font-size:.58rem;'
            f'padding:3px 8px;border-radius:6px;flex-shrink:0;letter-spacing:.06em;margin-top:1px;">{tag}</div>'
            f'<div style="font-size:.82rem;color:rgba(255,255,255,.75);line-height:1.55;">{text}</div></div>'
        )
    st.markdown(
        f'<div class="report-card">'
        f'<div style="font-family:\'Syne\',sans-serif;font-size:.72rem;font-weight:800;text-transform:uppercase;'
        f'letter-spacing:.12em;color:rgba(255,255,255,.3);margin-bottom:4px;">INFORME PRE-DROP AUTOMÁTICO</div>'
        f'<div style="font-size:.75rem;color:rgba(255,255,255,.4);margin-bottom:16px;">Drop Sombra · Generado hace 12 min · Claude API · 1.8s</div>'
        f'{rep_html}</div>',
        unsafe_allow_html=True,
    )

with col_pred:
    months_pred = list(range(8))
    drops_prev_gmv = [18500, 22000, 24800, 27300, 28900, 31200, 31200, None]
    drops_pred_gmv = [None, None, None, None, None, None, 31200, 45000]

    fig_pred = go.Figure()
    fig_pred.add_trace(go.Bar(
        x=["Sep 25", "Oct 25", "Nov 25", "Dic 25", "Feb 26", "Abr 26"],
        y=[18500, 22000, 24800, 27300, 28900, 31200],
        name="Drops anteriores", marker_color="#E5E7EB",
        hovertemplate="<b>%{x}</b><br>€%{y:,}<extra></extra>",
    ))
    fig_pred.add_trace(go.Bar(
        x=["Drop Sombra (predicción)"],
        y=[45000], name=f"Predicción: 42k–48k€",
        marker_color=AC,
        text=["~45.000€"], textposition="outside",
        textfont=dict(color="#0D0D0D", size=12),
        hovertemplate="<b>Predicción Drop Sombra</b><br>€%{y:,}<extra></extra>",
    ))
    fig_pred.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(248,248,246,1)",
        xaxis=dict(gridcolor="rgba(0,0,0,.04)", tickfont=dict(color="#111827", size=11)),
        yaxis=dict(title=dict(text="GMV 1ª hora (€)", font=dict(size=11, color="#4B5563")),
                   gridcolor="rgba(0,0,0,.05)", tickfont=dict(color="#6B7280", size=10),
                   tickformat=","),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#374151", size=11)),
        margin=dict(t=20, b=12, l=60, r=24), height=280,
        title=dict(text="GMV PRIMERA HORA · HISTÓRICO + PREDICCIÓN", font=dict(size=10, color="#374151"), x=0),
        hoverlabel=dict(bgcolor="#fff", bordercolor="#E5E5E5", font=dict(color="#0D0D0D", size=12)),
    )
    st.plotly_chart(fig_pred, use_container_width=True)
    st.markdown(
        f'<div style="font-size:.72rem;color:#6B7280;text-align:center;">Predicción basada en correlación Hype Score × GMV histórico · '
        f'<strong style="color:{AC};">Confianza: 78%</strong></div>',
        unsafe_allow_html=True,
    )

# =============================================================================
# SECTION 06 — DE SEÑALES A DECISIONES
# =============================================================================
st.markdown('<div class="sec-hdr"><span class="sec-num">06</span><h2 class="sec-ttl">DE SEÑALES A DECISIONES · CÓMO IMPACTA AL DROP</h2><div class="sec-line"></div></div>', unsafe_allow_html=True)

st.markdown(
    '<div style="font-size:.88rem;color:#6B7280;margin:-8px 0 18px;max-width:880px;line-height:1.6;">'
    'El valor no está solo en tener un dashboard bonito. Está en transformar señales dispersas en decisiones concretas antes de que el drop ocurra: '
    '<strong style="color:#0D0D0D;">cuándo comunicar, cuánto stock empujar, qué objeciones responder y qué esperar en ventas.</strong></div>',
    unsafe_allow_html=True,
)

decision_cols = st.columns(4)
for col, (title, signal, action, owner, color) in zip(decision_cols, [
    ("Marketing", "TikTok +340% en 1h", "Publicar teaser oficial antes de perder momentum.", "Social Lead", AC),
    ("E-commerce", "Hype Score 89/100", "Preparar landing, cola, bundles y emails de early access.", "Ecom Lead", "#3B82F6"),
    ("Producto", "Precio aparece en críticas", "Reforzar storytelling de materiales y edición limitada.", "Brand/Product", "#F59E0B"),
    ("Operaciones", "Predicción 42-48k€ 1ª hora", "Refuerzo de soporte y control de stock en tallas calientes.", "Ops/CX", "#22C55E"),
]):
    with col:
        st.markdown(
            f'<div style="background:#fff;border:1.5px solid #E5E5E5;border-radius:12px;padding:16px;height:100%;">'
            f'<div style="font-family:\'Syne\',sans-serif;font-weight:800;color:{color};font-size:.82rem;margin-bottom:8px;">{title}</div>'
            f'<div style="font-size:.65rem;font-weight:800;letter-spacing:.08em;color:#9CA3AF;text-transform:uppercase;margin-bottom:3px;">Señal</div>'
            f'<div style="font-size:.74rem;color:#0D0D0D;font-weight:700;margin-bottom:10px;">{signal}</div>'
            f'<div style="font-size:.65rem;font-weight:800;letter-spacing:.08em;color:#9CA3AF;text-transform:uppercase;margin-bottom:3px;">Acción</div>'
            f'<div style="font-size:.72rem;color:#6B7280;line-height:1.45;margin-bottom:12px;">{action}</div>'
            f'<div style="border-top:1px solid #E5E5E5;padding-top:8px;font-size:.66rem;color:{color};font-weight:800;">Responsable: {owner}</div></div>',
            unsafe_allow_html=True,
        )

col_model, col_matrix = st.columns([1.25, 1])
with col_model:
    stages = [
        ("Captura", "Instagram, TikTok, X, Reddit, Google Trends, Shopify waitlists, Klaviyo clicks."),
        ("Normalización", "n8n + Python limpian ruido, deduplican menciones, detectan idioma, ciudad y plataforma."),
        ("Análisis IA", "Claude clasifica sentimiento, intención de compra, objeciones, leaks, influencers y señales anómalas."),
        ("Predicción", "SQL cruza hype histórico, ventas por drop, tasa de conversión, stock y calendario de comunicación."),
        ("Acción", "Alertas Slack/WhatsApp, informes pre-drop, recomendaciones y dashboard en Grafana."),
    ]
    st.markdown(
        '<div style="background:#0D0D0D;border-radius:16px;padding:22px;color:#fff;height:100%;">'
        '<div style="font-family:\'Syne\',sans-serif;font-size:.72rem;font-weight:800;text-transform:uppercase;letter-spacing:.12em;color:rgba(255,255,255,.35);margin-bottom:14px;">Arquitectura de inteligencia pre-drop</div>'
        + "".join(
            f'<div style="display:flex;gap:12px;margin-bottom:12px;align-items:flex-start;">'
            f'<div style="width:28px;height:28px;border-radius:50%;background:{AC};color:#fff;font-family:Syne,sans-serif;font-size:.68rem;font-weight:800;display:flex;align-items:center;justify-content:center;flex-shrink:0;">{i}</div>'
            f'<div><div style="font-size:.78rem;font-weight:800;color:#fff;margin-bottom:2px;">{title}</div>'
            f'<div style="font-size:.7rem;color:rgba(255,255,255,.58);line-height:1.45;">{desc}</div></div></div>'
            for i, (title, desc) in enumerate(stages, start=1)
        )
        + '</div>',
        unsafe_allow_html=True,
    )
with col_matrix:
    fig_matrix = go.Figure()
    matrix_points = [
        ("Leak Reddit", 55, 70, "#F59E0B"),
        ("TikTok viral", 92, 88, AC),
        ("Crítica precio", 38, 42, "#EF4444"),
        ("Influencer orgánico", 82, 77, "#22C55E"),
        ("Google Trends", 70, 64, "#3B82F6"),
    ]
    for label, hype, impact, color in matrix_points:
        fig_matrix.add_trace(go.Scatter(
            x=[hype], y=[impact], mode="markers+text", text=[label], textposition="top center",
            marker=dict(size=18, color=color, line=dict(color="#fff", width=2)),
            name=label, hovertemplate=f"<b>{label}</b><br>Hype: {hype}/100<br>Impacto esperado: {impact}/100<extra></extra>",
        ))
    fig_matrix.add_shape(type="line", x0=60, x1=60, y0=0, y1=100, line=dict(color="#E5E7EB", dash="dash"))
    fig_matrix.add_shape(type="line", x0=0, x1=100, y0=60, y1=60, line=dict(color="#E5E7EB", dash="dash"))
    fig_matrix.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(248,248,246,1)", showlegend=False,
        xaxis=dict(title="Intensidad de señal", range=[0, 105], gridcolor="rgba(0,0,0,.05)", tickfont=dict(color="#6B7280", size=10)),
        yaxis=dict(title="Impacto esperado", range=[0, 105], gridcolor="rgba(0,0,0,.05)", tickfont=dict(color="#6B7280", size=10)),
        margin=dict(t=20, b=40, l=45, r=20), height=320,
        title=dict(text="MATRIZ DE PRIORIDAD DE SEÑALES", font=dict(size=11, color="#374151"), x=0),
    )
    st.plotly_chart(fig_matrix, use_container_width=True)


# =============================================================================
# SECTION 07 — IMPLEMENTACIÓN, ROI Y RIESGOS
# =============================================================================
st.markdown('<div class="sec-hdr"><span class="sec-num">07</span><h2 class="sec-ttl">IMPLEMENTACIÓN · ROI, ROADMAP Y RIESGOS</h2><div class="sec-line"></div></div>', unsafe_allow_html=True)

tab_stack, tab_roadmap, tab_risk = st.tabs(["Stack técnico", "Roadmap 30-60-90", "Riesgos y mitigación"])

with tab_stack:
    tech_cols = st.columns(3)
    for col, (title, items, kpi) in zip(tech_cols, [
        ("Data ingestion", ["APIs sociales donde sea posible", "Scraping controlado si no hay API", "Google Trends, Shopify, Klaviyo", "n8n schedules cada hora"], "1 actualización/hora"),
        ("Inteligencia", ["Python para limpieza y scoring", "Claude Haiku para clasificación barata", "Claude Sonnet para informes", "SQL para histórico y features"], "78% confianza inicial"),
        ("Activación", ["Grafana para dashboard", "Slack/WhatsApp para alertas", "PDF/email pre-drop automático", "Brief de acciones por equipo"], "<5 min hasta alerta"),
    ]):
        with col:
            st.markdown(
                f'<div style="background:{AC_L};border:1px solid {AC_B};border-radius:12px;padding:18px;height:100%;">'
                f'<div style="font-family:\'Syne\',sans-serif;font-weight:800;color:#0D0D0D;margin-bottom:10px;">{title}</div>'
                + "".join(f'<div style="font-size:.73rem;color:#374151;line-height:1.55;margin-bottom:7px;">{_icon("check",12,"#22C55E")} {item}</div>' for item in items)
                + f'<div style="margin-top:12px;border-top:1px solid {AC_B};padding-top:10px;font-size:.7rem;font-weight:800;color:{AC};">{kpi}</div></div>',
                unsafe_allow_html=True,
            )

with tab_roadmap:
    roadmap = [
        ("0-30 días", "MVP de escucha", "Instagram/TikTok manual + Google Trends + Reddit/X, scoring de sentimiento, informe pre-drop y alertas básicas.", "Primer informe ejecutivo para el siguiente drop."),
        ("31-60 días", "Forecasting", "Histórico de drops en SQL, correlación hype-ventas, dashboard Grafana y alertas por anomalía.", "Predicción GMV por drop y recomendaciones accionables."),
        ("61-90 días", "Sistema de decisión", "Automatización n8n completa, playbooks por umbral, integración con Klaviyo/Shopify y aprendizaje post-drop.", "Cada drop deja datos para mejorar el siguiente."),
    ]
    for phase, title, desc, outcome in roadmap:
        st.markdown(
            f'<div style="display:grid;grid-template-columns:110px 1fr 260px;gap:16px;align-items:stretch;margin-bottom:10px;">'
            f'<div style="background:{AC};color:#fff;border-radius:12px;padding:14px;text-align:center;font-family:Syne,sans-serif;font-weight:800;font-size:.85rem;">{phase}</div>'
            f'<div style="background:#F8F8F6;border:1px solid #EBEBEB;border-radius:12px;padding:14px 16px;">'
            f'<div style="font-weight:800;color:#0D0D0D;font-size:.86rem;margin-bottom:4px;">{title}</div>'
            f'<div style="font-size:.74rem;color:#6B7280;line-height:1.5;">{desc}</div></div>'
            f'<div style="background:#fff;border:1.5px solid {AC_B};border-radius:12px;padding:14px 16px;">'
            f'<div style="font-size:.62rem;font-weight:800;letter-spacing:.09em;color:{AC};text-transform:uppercase;margin-bottom:5px;">Resultado CEO</div>'
            f'<div style="font-size:.72rem;color:#374151;line-height:1.45;">{outcome}</div></div></div>',
            unsafe_allow_html=True,
        )

with tab_risk:
    risks = [
        ("APIs limitadas", "Algunas plataformas limitan acceso a datos.", "Empezar con fuentes estables y combinar APIs, exports, scraping responsable y señales propias."),
        ("Ruido social", "No toda mención implica intención de compra.", "Clasificar intención, ponderar por fuente e influencer, y validar contra ventas reales post-drop."),
        ("Falsos positivos", "Un pico puede hacer sobrerreaccionar al equipo.", "Umbrales por severidad, confianza del modelo y aprobación humana en acciones sensibles."),
        ("Predicción imperfecta", "El forecasting inicial tendrá error.", "Mostrar rango, confianza y aprender con cada drop hasta tener histórico suficiente."),
    ]
    for title, risk, mitigation in risks:
        st.markdown(
            f'<div style="display:grid;grid-template-columns:170px 1fr 1fr;gap:12px;margin-bottom:10px;">'
            f'<div style="background:#111827;color:#fff;border-radius:10px;padding:12px;font-weight:800;font-size:.78rem;">{title}</div>'
            f'<div style="background:#FEF2F2;border:1px solid #FECACA;border-radius:10px;padding:12px;font-size:.72rem;color:#7F1D1D;line-height:1.45;"><strong>Riesgo:</strong> {risk}</div>'
            f'<div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:10px;padding:12px;font-size:.72rem;color:#14532D;line-height:1.45;"><strong>Mitigación:</strong> {mitigation}</div></div>',
            unsafe_allow_html=True,
        )

_footer()
