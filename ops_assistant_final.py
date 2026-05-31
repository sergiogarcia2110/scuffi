# ops_assistant_final.py  ·  Ops Assistant Demo · Scuffers
# Run: python3 -m streamlit run ops_assistant_final.py

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
    "bot":          '<path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/>',
    "book-open":    '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
    "arrow-right":  '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    "check":        '<path d="M20 6 9 17l-5-5"/>',
    "zap":          '<path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.81a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.81a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"/>',
    "clock":        '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "users":        '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "refresh-cw":   '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/>',
    "bar-chart-2":  '<line x1="18" x2="18" y1="20" y2="10"/><line x1="12" x2="12" y1="20" y2="4"/><line x1="6" x2="6" y1="20" y2="14"/>',
    "database":     '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19A9 3 0 0 0 21 19V5"/><path d="M3 12A9 3 0 0 0 21 12"/>',
    "alert-circle": '<circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/>',
    "arrow-up-right":'<path d="M7 7h10v10"/><path d="M7 17 17 7"/>',
    "file-text":    '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/>',
    "shield":       '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/>',
    "message-circle":'<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/>',
}

def _icon(name, size=16, color="currentColor", **kw):
    return _lucide_svg(_L.get(name, ""), size=size, color=color, **kw)


# ─── LOGO HANDLING ─────────────────────────────────────────────────────────────
@functools.lru_cache(maxsize=1)
def _fallback_page_icon_path():
    p = Path(__file__).resolve().parent / "_ops_tab_fallback.png"
    if not p.is_file():
        im = _PILImg.new("RGBA", (64, 64), (0, 0, 0, 0))
        from PIL import ImageDraw
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([8, 8, 56, 56], radius=10, fill=(59, 130, 246, 255))
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
AC   = "#3B82F6"
AC_D = "#2563EB"
AC_L = "#EFF6FF"
AC_B = "#BFDBFE"

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Ops Assistant · Demo",
    page_icon=_LOG_FAV if _LOG_FAV else _fallback_page_icon_path(),
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── SESSION STATE ─────────────────────────────────────────────────────────────
def _ss(k, v):
    if k not in st.session_state:
        st.session_state[k] = v

_ss("qa_answered", False)
_ss("qa_current", None)

# ─── Q&A DATA ─────────────────────────────────────────────────────────────────
QA_PAIRS = [
    {
        "q": "¿Cuál es la política de devoluciones?",
        "a": "Los clientes tienen 30 días desde la recepción para iniciar una devolución. El primer cambio en España es gratuito. Segundo cambio o internacional: 4,95€ deducidos del reembolso. Para iniciar: returns.reveni.io/scuffers con el nº de pedido.",
        "source": "📄 Política de Devoluciones v2.3 · Enero 2026",
        "confidence": 98,
        "category": "Devoluciones",
        "time": "0.3s",
        "escalate": False,
    },
    {
        "q": "¿Las prendas del Drop Sombra son true to size?",
        "a": "No. Todas las prendas del Drop Sombra son oversized. Se recomienda bajar una talla respecto al uso habitual. Ejemplo: si usas M normalmente, pide S. La guía de tallas completa está en la ficha de cada producto.",
        "source": "📏 Guía de Tallas · Drop Sombra 2026",
        "confidence": 95,
        "category": "Tallas",
        "time": "0.4s",
        "escalate": False,
    },
    {
        "q": "Un cliente lleva 10 días sin actualización de tracking. ¿Qué hago?",
        "a": "Protocolo de pedido bloqueado:\n1. Verificar en panel MRW/GLS con el nº de guía.\n2. Si sin actualización >10 días laborables: abrir ticket PRIORITARIO en Gorgias con tag 'tracking-frozen'.\n3. Notificar al cliente proactivamente con disculpa y plazo de resolución (48h).\n4. Si no se localiza en 48h: reenvío exprés automático o reembolso completo a elección del cliente.",
        "source": "⚠️ Protocolo Logística · Incidencias de Tracking v1.4",
        "confidence": 92,
        "category": "Logística",
        "time": "0.5s",
        "escalate": False,
    },
    {
        "q": "¿Cuándo es el próximo drop y qué podemos decir a los clientes?",
        "a": "Drop Sombra: viernes 7 de junio de 2026 a las 20:00h.\n\nSe puede confirmar a clientes: (1) Fecha y hora. (2) 'Habrá piezas oversized, edición limitada'. NO confirmar número exacto de piezas ni precios antes del anuncio oficial (viernes 19:30h). Los accesos anticipados OG/Founder se activan a las 18:00h.",
        "source": "📅 Calendario de Drops 2026 · Actualizado: 28 mayo",
        "confidence": 97,
        "category": "Drops",
        "time": "0.4s",
        "escalate": False,
    },
    {
        "q": "¿Tienen descuento los empleados?",
        "a": "Sí. 30% de descuento en todas las compras online con el código de empleado personal (solicitar a RRHH si no lo tienes). No aplica sobre prendas ya descontadas ni en los primeros 3 días de un drop. Máximo 3 prendas por drop a precio de empleado.",
        "source": "👥 Política de Empleados · Beneficios v1.1",
        "confidence": 99,
        "category": "Políticas Internas",
        "time": "0.3s",
        "escalate": False,
    },
    {
        "q": "Un cliente quiere hablar con el responsable de tienda urgente",
        "a": "Esta consulta necesita atención directa del equipo de gestión. Te paso el contexto al responsable de turno ahora mismo.\n\nEscalando a: Gerente de Tienda · Canal: WhatsApp interno\n\nAsegúrate de tener el nombre del cliente y el motivo de la urgencia para agilizar la atención.",
        "source": "🔴 Escalado a equipo humano",
        "confidence": None,
        "category": "Escalado",
        "time": "0.2s",
        "escalate": True,
    },
]

QUESTIONS = [qa["q"] for qa in QA_PAIRS]
QA_MAP = {qa["q"]: qa for qa in QA_PAIRS}

KB_DOMAINS = [
    {"icon": "📦", "title": "Pedidos y Logística",    "items": ["Estados de pedido", "Tracking y transportistas", "Protocolos incidencia", "Reenvíos y reembolsos"],         "color": "#F97316"},
    {"icon": "🔄", "title": "Devoluciones",            "items": ["Política de cambios", "Portal Reveni", "Plazos y condiciones", "Devoluciones internacionales"],            "color": "#A855F7"},
    {"icon": "👕", "title": "Producto y Tallas",       "items": ["Guías de tallas por drop", "Materiales y composición", "Cuidado de prendas", "Oversized vs regular"],       "color": AC},
    {"icon": "📅", "title": "Drops y Calendario",      "items": ["Calendario 2026", "Early access OG/Founder", "Comunicación pre-drop", "Información no pública"],           "color": "#EF4444"},
    {"icon": "👥", "title": "Políticas de Empleados",  "items": ["Descuentos empleados", "Protocolos de tienda", "Onboarding nuevo empleado", "Beneficios y RRHH"],          "color": "#22C55E"},
    {"icon": "🏪", "title": "Operaciones de Tienda",   "items": ["Apertura y cierre", "Gestión de caja", "Protocolo quejas en tienda", "Stock y reposición"],               "color": "#6B7280"},
]

# Question frequency data
TOP_QUESTIONS = [
    ("¿Cómo gestiono una devolución?",        89),
    ("¿Cuándo llega el próximo drop?",         74),
    ("¿Son oversized las prendas?",            67),
    ("¿Cómo sigo un pedido sin tracking?",     58),
    ("¿Cuál es el código de empleado?",        43),
    ("Protocolo cliente muy enfadado",         38),
    ("¿Qué talla recomiendas para X prenda?",  31),
]

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
.kpi-card.blue{{border-top:3px solid {AC}}}
.kpi-card.green{{border-top:3px solid #22C55E}}
.insight-card{{background:#fff;border:1.5px solid #E5E5E5;border-radius:12px;padding:18px;border-left:4px solid #EF4444;height:100%;transition:border-color .2s}}
.insight-card:hover{{border-left-color:{AC};box-shadow:0 4px 16px rgba(59,130,246,.08)}}
.insight-cat{{font-family:'Syne',sans-serif;font-size:.85rem;font-weight:700;margin-bottom:4px}}
.insight-finding{{font-size:.78rem;color:#6B7280;line-height:1.5;margin-bottom:8px}}
.insight-action{{font-size:.75rem;font-weight:600;color:{AC};background:{AC_L};padding:5px 10px;border-radius:6px;display:inline-block}}
.ans-card{{background:{AC_L};border:1.5px solid {AC_B};border-radius:12px;padding:20px 24px;margin-top:8px;animation:fadeIn .4s ease both}}
.ans-label{{font-size:.62rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:{AC};margin-bottom:10px;display:flex;align-items:center;gap:7px}}
.ans-body{{font-size:.88rem;color:#1F2937;line-height:1.7;white-space:pre-wrap}}
.ans-source{{margin-top:12px;padding-top:10px;border-top:1px solid {AC_B};font-size:.72rem;color:#6B7280;display:flex;align-items:center;gap:10px;flex-wrap:wrap}}
.conf-bar-wrap{{height:4px;background:#E5E7EB;border-radius:2px;margin-top:4px;overflow:hidden}}
.kb-card{{background:#F8F8F6;border:1px solid #EBEBEB;border-radius:12px;padding:16px;height:100%;transition:box-shadow .2s}}
.kb-card:hover{{box-shadow:0 4px 16px rgba(59,130,246,.1);border-color:{AC_B}}}
.kb-icon{{font-size:1.5rem;margin-bottom:8px;line-height:1}}
.kb-title{{font-family:'Syne',sans-serif;font-size:.82rem;font-weight:800;color:#0D0D0D;margin-bottom:8px}}
.kb-item{{font-size:.72rem;color:#6B7280;line-height:1.6;display:flex;align-items:center;gap:6px}}
.stTabs [data-baseweb="tab-list"]{{gap:0;border-bottom:1px solid #E5E5E5}}
.stTabs [data-baseweb="tab"]{{font-size:.82rem;font-weight:500;color:#6B7280;padding:10px 20px;border-bottom:2px solid transparent}}
.stTabs [aria-selected="true"]{{color:{AC}!important;border-bottom-color:{AC}!important;font-weight:600!important}}
.stButton>button{{font-size:.82rem!important;border-radius:8px!important;border:1.5px solid {AC}!important;background:{AC}!important;color:#fff!important;padding:6px 16px!important}}
.stButton>button:hover{{background:{AC_D}!important;border-color:{AC_D}!important}}
.escalate-card{{background:#FEF2F2;border:1.5px solid #FECACA;border-radius:12px;padding:20px 24px;margin-top:8px}}
.pipe-wrap{{background:linear-gradient(180deg,#F8F8F6 0%,#fff 100%);border:1px solid #E5E5E5;border-radius:16px;padding:1.35rem 1.25rem 1.5rem;margin-bottom:1.5rem}}
.pipe-flow{{display:flex;flex-wrap:nowrap;align-items:stretch;justify-content:center;gap:0;overflow-x:auto;padding-bottom:6px}}
.pipe-step{{flex:1;min-width:90px;max-width:150px;text-align:center;padding:10px 8px}}
.pipe-step-num{{width:28px;height:28px;margin:0 auto 8px;border-radius:50%;background:linear-gradient(135deg,{AC},{AC_D});color:#fff;font-family:'Syne',sans-serif;font-size:.72rem;font-weight:800;line-height:28px;animation:pipeGlow 2.8s ease-in-out infinite}}
.pipe-step-num:nth-child(2){{animation-delay:.35s}}
.pipe-step-ttl{{font-size:.72rem;font-weight:700;color:#0D0D0D;margin-bottom:4px}}
.pipe-step-desc{{font-size:.65rem;color:#6B7280;line-height:1.4}}
.pipe-arrow{{display:flex;align-items:center;color:#C5DED2;font-size:1.1rem;padding:0 2px}}
@keyframes pipeGlow{{0%,100%{{box-shadow:0 4px 14px rgba(59,130,246,.25)}}50%{{box-shadow:0 4px 22px rgba(59,130,246,.5)}}}}
@keyframes fadeIn{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:translateY(0)}}}}
</style>
""", unsafe_allow_html=True)


# ─── NAVBAR ───────────────────────────────────────────────────────────────────
_nav_logo = f'<img src="{_LOGO_NAV}" alt="Scuffers" style="height:22px;width:auto;vertical-align:middle;margin-right:10px;">' if _LOGO_NAV else ""
_hl, _ = st.columns([3, 1], gap="medium")
with _hl:
    st.markdown(
        f'<div style="padding:6px 0 10px;"><div style="display:flex;align-items:center;flex-wrap:wrap;gap:14px;">'
        f'<div style="font-family:\'Syne\',sans-serif;font-size:1rem;font-weight:800;letter-spacing:.04em;display:flex;align-items:center;">'
        f'{_nav_logo}OPS ASSISTANT <span style="font-weight:400;color:#9CA3AF;font-size:.85rem;">· Bot Interno del Equipo Scuffers</span></div>'
        f'<div class="demo-badge">{_icon("bot",14,"#9CA3AF")} Demo · 6 dominios de conocimiento · Claude Haiku 4.5</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )
st.markdown('<div style="border-bottom:1px solid #E5E5E5;margin:0 0 10px 0;"></div>', unsafe_allow_html=True)


def _footer():
    _fl = f'<img src="{_LOGO_FOOT}" alt="" style="height:18px;width:auto;vertical-align:middle;margin-right:8px;">' if _LOGO_FOOT else ""
    st.markdown(
        f'<div style="text-align:center;margin-top:3rem;padding-top:1.5rem;border-top:1px solid #E5E5E5;'
        f'font-size:.68rem;color:#9CA3AF;letter-spacing:.06em;display:flex;align-items:center;justify-content:center;gap:4px;">'
        f'{_fl}OPS ASSISTANT · Demo · Fase 1 Quick Win · ~40€/mes</div>',
        unsafe_allow_html=True,
    )


# =============================================================================
# HERO
# =============================================================================
st.markdown('<div style="padding:1.8rem 0 1.2rem;">', unsafe_allow_html=True)
hero_l, hero_r = st.columns([1.35, 1])

with hero_l:
    st.markdown(
        f'<div style="font-size:.68rem;font-weight:700;letter-spacing:.16em;text-transform:uppercase;'
        f'color:{AC};margin-bottom:.8rem;display:flex;align-items:center;gap:8px;">'
        f'<span style="display:inline-block;width:20px;height:2px;background:{AC};"></span>FASE 1 · QUICK WIN · ~40€/MES</div>'
        '<div style="font-family:\'Syne\',sans-serif;font-size:clamp(1.8rem,3vw,2.7rem);font-weight:800;'
        'line-height:1.15;color:#0D0D0D;margin-bottom:1rem;">'
        f'Elimina las preguntas<br><span style="color:{AC};">repetitivas del equipo</span><br>'
        '<span style="font-size:.55em;font-weight:400;color:#6B7280;">y acelera el onboarding.</span></div>'
        '<div style="font-size:.9rem;color:#6B7280;line-height:1.65;max-width:480px;">'
        'Un asistente interno disponible por WhatsApp y Slack que responde en lenguaje natural con la fuente citada. '
        f'<strong style="color:#0D0D0D;">Los managers dejan de responder las mismas preguntas.</strong></div>',
        unsafe_allow_html=True,
    )

with hero_r:
    h1, h2 = st.columns(2)
    with h1:
        st.markdown(f'<div class="kpi-card blue"><div class="kpi-lbl">Tiempo managers liberado</div><div class="kpi-val" style="color:{AC};">8h</div><div class="kpi-sub">por semana estimado</div></div>', unsafe_allow_html=True)
    with h2:
        st.markdown(f'<div class="kpi-card blue"><div class="kpi-lbl">Preguntas resueltas</div><div class="kpi-val" style="color:{AC};">87%</div><div class="kpi-sub">sin escalar a manager</div></div>', unsafe_allow_html=True)
    st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
    h3, h4 = st.columns(2)
    with h3:
        st.markdown('<div class="kpi-card green"><div class="kpi-lbl">Tiempo de respuesta</div><div class="kpi-val" style="color:#22C55E;">&lt;5s</div><div class="kpi-sub">vs ~18 min con managers</div></div>', unsafe_allow_html=True)
    with h4:
        st.markdown(f'<div class="kpi-card blue"><div class="kpi-lbl">Dominios de conocimiento</div><div class="kpi-val" style="color:{AC};">6</div><div class="kpi-sub">Ops · Producto · Drops · RRHH</div></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


# =============================================================================
# SECTION 01 — EL PROBLEMA
# =============================================================================
st.markdown('<div class="sec-hdr"><span class="sec-num">01</span><h2 class="sec-ttl">EL PROBLEMA ACTUAL</h2><div class="sec-line"></div></div>', unsafe_allow_html=True)

ins_cols = st.columns(3)
for i, (icon_name, cat, finding, action) in enumerate([
    ("message-circle", "Preguntas repetitivas por WhatsApp",      "Con 10-50 empleados entre tiendas y oficinas, los managers responden las mismas preguntas cada semana. Logística, tallas, políticas, drops.",             f"{_icon('arrow-right',13,AC)} Ops Assistant responde en segundos con la fuente citada"),
    ("users",          "Onboarding lento e inconsistente",         "Cada nuevo empleado hace las mismas preguntas durante semanas. El onboarding depende de a quién le toque explicarlo — y varía según el día.",          f"{_icon('arrow-right',13,AC)} Guía paso a paso + quiz informal a los 7 días"),
    ("alert-circle",   "Documentación dispersa y desactualizada",  "Las políticas están en emails, en Notion, en conversaciones de WhatsApp. Nadie sabe cuál es la versión válida. Los errores operativos lo reflejan.",   f"{_icon('arrow-right',13,AC)} Base de conocimiento centralizada y siempre actualizada"),
]):
    with ins_cols[i]:
        st.markdown(
            f'<div class="insight-card"><div style="margin-bottom:8px;">{_icon(icon_name,22,"#6B7280")}</div>'
            f'<div class="insight-cat">{cat}</div><div class="insight-finding">{finding}</div>'
            f'<div class="insight-action">{action}</div></div>',
            unsafe_allow_html=True,
        )

# Time chart
fig_time = go.Figure()
fig_time.add_trace(go.Bar(
    name="Sin Ops Assistant", y=["Política devoluciones", "Talla de prenda", "Protocolo incidencia", "Info próximo drop", "Descuento empleado"],
    x=[18, 12, 25, 8, 10], orientation="h",
    marker_color="#E5E7EB",
    text=["18 min", "12 min", "25 min", "8 min", "10 min"], textposition="outside",
    textfont=dict(color="#6B7280", size=11),
))
fig_time.add_trace(go.Bar(
    name="Con Ops Assistant", y=["Política devoluciones", "Talla de prenda", "Protocolo incidencia", "Info próximo drop", "Descuento empleado"],
    x=[0.3, 0.3, 0.5, 0.3, 0.3], orientation="h",
    marker_color=AC,
    text=["3s", "3s", "5s", "3s", "3s"], textposition="outside",
    textfont=dict(color="#0D0D0D", size=11),
))
fig_time.update_layout(
    barmode="group", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(248,248,246,1)",
    xaxis=dict(title=dict(text="Minutos hasta respuesta", font=dict(size=12, color="#4B5563")),
               gridcolor="rgba(0,0,0,.05)", tickfont=dict(color="#6B7280", size=11)),
    yaxis=dict(showgrid=False, tickfont=dict(color="#111827", size=12)),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#374151", size=12)),
    margin=dict(t=20, b=12, l=8, r=80), height=240,
    title=dict(text="TIEMPO HASTA RESPUESTA POR TIPO DE PREGUNTA", font=dict(size=11, color="#374151"), x=0),
    hoverlabel=dict(bgcolor="#fff", bordercolor="#E5E5E5", font=dict(color="#0D0D0D", size=12)),
)
st.plotly_chart(fig_time, use_container_width=True)


# =============================================================================
# SECTION 02 — PREGUNTAR AL ASISTENTE
# =============================================================================
st.markdown('<div class="sec-hdr"><span class="sec-num">02</span><h2 class="sec-ttl">PREGUNTAR AL ASISTENTE</h2><div class="sec-line"></div></div>', unsafe_allow_html=True)

col_q, col_a = st.columns([1, 1.6])
with col_q:
    st.markdown('<div style="padding-top:8px;">', unsafe_allow_html=True)
    selected_q = st.selectbox(
        "Selecciona una pregunta del equipo",
        QUESTIONS,
        key="qa_sel",
        help="Simula las preguntas reales del equipo de tienda y oficinas",
    )
    qa = QA_MAP[selected_q]
    cat_colors = {"Devoluciones": "#A855F7", "Tallas": AC, "Logística": "#F97316",
                  "Drops": "#EF4444", "Políticas Internas": "#22C55E", "Escalado": "#6B7280"}
    cat_color = cat_colors.get(qa["category"], AC)
    st.markdown(
        f'<div style="font-size:.72rem;margin:6px 0 14px;padding:8px 12px;background:#F8F8F6;border-radius:8px;'
        f'border-left:3px solid {cat_color};display:flex;align-items:center;gap:8px;">'
        f'<span style="font-weight:700;font-size:.65rem;color:{cat_color};">{qa["category"].upper()}</span>'
        f'<span style="color:#9CA3AF;">·</span>'
        f'<span style="font-size:.65rem;color:#9CA3AF;">{_icon("clock",11,"#9CA3AF")} Respuesta en {qa["time"]}</span></div>',
        unsafe_allow_html=True,
    )
    if st.button("Preguntar al Ops Assistant", key="qa_btn"):
        st.session_state.qa_answered = True
        st.session_state.qa_current = selected_q
    st.markdown('</div>', unsafe_allow_html=True)

with col_a:
    if st.session_state.qa_answered and st.session_state.qa_current:
        cur_qa = QA_MAP.get(st.session_state.qa_current, qa)
        if cur_qa["escalate"]:
            st.markdown(
                f'<div class="escalate-card">'
                f'<div style="font-size:.62rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;'
                f'color:#EF4444;margin-bottom:10px;display:flex;align-items:center;gap:7px;">'
                f'{_icon("arrow-up-right",14,"#EF4444")} Ops Assistant · escalando a equipo humano</div>'
                f'<div style="font-size:.88rem;color:#1F2937;line-height:1.7;white-space:pre-wrap;">{cur_qa["a"]}</div>'
                f'<div style="margin-top:12px;padding-top:10px;border-top:1px solid #FECACA;'
                f'font-size:.72rem;color:#6B7280;">{cur_qa["source"]}</div></div>',
                unsafe_allow_html=True,
            )
        else:
            conf = cur_qa["confidence"]
            st.markdown(
                f'<div class="ans-card">'
                f'<div class="ans-label">{_icon("bot",14,AC)} Ops Assistant · {cur_qa["time"]}</div>'
                f'<div class="ans-body">{cur_qa["a"]}</div>'
                f'<div class="ans-source">'
                f'<span style="font-weight:600;color:#0D0D0D;">{cur_qa["source"]}</span>'
                f'<span style="margin-left:auto;display:flex;align-items:center;gap:6px;">'
                f'<span style="font-size:.65rem;color:#9CA3AF;">Confianza: {conf}%</span>'
                f'<div style="width:60px;height:4px;background:#E5E7EB;border-radius:2px;overflow:hidden;">'
                f'<div style="height:100%;width:{conf}%;background:{AC};border-radius:2px;"></div></div>'
                f'</span></div></div>',
                unsafe_allow_html=True,
            )
    else:
        # Animated iframe demo
        demo_css = (
            "* { box-sizing:border-box; margin:0; padding:0; }"
            "body { font-family:'Segoe UI',sans-serif; background:#F8F8F6; padding:16px 16px 20px; }"
            ".hd { display:flex; align-items:center; gap:10px; padding-bottom:10px; border-bottom:1px solid #E5E5E5; margin-bottom:14px; }"
            ".hd-av { width:28px; height:28px; border-radius:50%; background:#DBEAFE; display:flex; align-items:center; justify-content:center; font-size:.62rem; font-weight:700; color:#2563EB; flex-shrink:0; }"
            ".hd-name { font-weight:700; font-size:.85rem; color:#0D0D0D; } .hd-st { font-size:.68rem; color:#3B82F6; }"
            ".row { display:flex; gap:8px; margin-bottom:10px; align-items:flex-end; }"
            ".row-r { flex-direction:row-reverse; }"
            ".av { width:24px; height:24px; border-radius:50%; background:#E5E5E5; display:flex; align-items:center; justify-content:center; font-size:.58rem; font-weight:700; color:#6B7280; flex-shrink:0; }"
            ".bbl { max-width:78%; padding:8px 12px; font-size:.78rem; line-height:1.5; border-radius:14px; }"
            ".bbl-l { background:#fff; border:1px solid #E5E5E5; border-radius:4px 14px 14px 14px; color:#0D0D0D; }"
            ".bbl-r { background:#2563EB; color:#fff; border-radius:14px 4px 14px 14px; }"
            ".src { background:#EFF6FF; border:1px solid #BFDBFE; border-radius:8px; padding:7px 10px; margin-top:8px; font-size:.65rem; color:#1D4ED8; font-weight:600; }"
            "@keyframes chatL { from { opacity:0; transform:translateX(-12px); } to { opacity:1; transform:translateX(0); } }"
            "@keyframes chatR { from { opacity:0; transform:translateX(12px); } to { opacity:1; transform:translateX(0); } }"
            ".m1 { animation:chatR .5s .4s ease both; } .m2 { animation:chatL .5s 1.4s ease both; }"
            ".m3 { animation:chatL .5s 2.6s ease both; } .m4 { animation:chatR .5s 3.8s ease both; }"
        )
        demo_body = (
            '<div class="hd"><div class="hd-av">OA</div>'
            '<div><div class="hd-name">Ops Assistant</div><div class="hd-st">● activo · responde en &lt;5s</div></div></div>'
            '<div class="row row-r m1"><div class="bbl bbl-r">Ey, ¿qué hago si un cliente quiere devolver y no tiene el ticket de compra?</div></div>'
            '<div class="row m2"><div class="av">OA</div><div><div class="bbl bbl-l">¡Hola! Para devoluciones sin ticket, el cliente puede usar el email de confirmación del pedido o el número de pedido. Con cualquiera de los dos puedes iniciar la devolución en returns.reveni.io/scuffers. El plazo es 30 días desde recepción.</div>'
            '<div class="src">📄 Política de Devoluciones v2.3 · Confianza: 98%</div></div></div>'
            '<div class="row row-r m3"><div class="bbl bbl-r">¿Y si han pasado 35 días?</div></div>'
            '<div class="row m4"><div class="av">OA</div><div><div class="bbl bbl-l">En ese caso está fuera del plazo estándar. Puedes escalarlo al responsable de tienda para valorar excepciones caso a caso. No hagas la devolución sin aprobación.</div>'
            '<div class="src">⚠️ Escalado recomendado · Fuera de plazo estándar</div></div></div>'
        )
        _comps.html(
            '<!DOCTYPE html><html><head><meta charset="utf-8"><style>' + demo_css + '</style></head>'
            '<body>' + demo_body + '</body></html>',
            height=380, scrolling=False,
        )


# =============================================================================
# SECTION 03 — BASE DE CONOCIMIENTO
# =============================================================================
st.markdown('<div class="sec-hdr"><span class="sec-num">03</span><h2 class="sec-ttl">BASE DE CONOCIMIENTO</h2><div class="sec-line"></div></div>', unsafe_allow_html=True)

st.markdown(
    '<div style="font-size:.88rem;color:#6B7280;margin:-8px 0 20px;max-width:760px;line-height:1.6;">'
    'Un único repositorio en Notion/Google Drive sincronizado automáticamente con el asistente. '
    '<strong style="color:#0D0D0D;">Cuando el equipo actualiza un documento, el asistente lo sabe al instante.</strong>'
    '</div>',
    unsafe_allow_html=True,
)

kb_cols = st.columns(3)
for i, domain in enumerate(KB_DOMAINS):
    with kb_cols[i % 3]:
        items_html = "".join(
            f'<div class="kb-item">'
            f'<span style="color:{domain["color"]};font-size:.6rem;">●</span>{item}</div>'
            for item in domain["items"]
        )
        st.markdown(
            f'<div class="kb-card"><div class="kb-icon">{domain["icon"]}</div>'
            f'<div class="kb-title" style="border-bottom:2px solid {domain["color"]};padding-bottom:6px;margin-bottom:8px;">'
            f'{domain["title"]}</div>{items_html}</div>',
            unsafe_allow_html=True,
        )
    if i == 2:
        st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
        kb_cols = st.columns(3)


# =============================================================================
# SECTION 04 — ANALYTICS DE PREGUNTAS
# =============================================================================
st.markdown('<div class="sec-hdr"><span class="sec-num">04</span><h2 class="sec-ttl">LO QUE MÁS PREGUNTA EL EQUIPO</h2><div class="sec-line"></div></div>', unsafe_allow_html=True)

col_q_chart, col_insight = st.columns([1.5, 1])

with col_q_chart:
    qs, counts = zip(*TOP_QUESTIONS)
    colors_q = [AC if i == 0 else "#E5E7EB" for i in range(len(qs))]
    fig_qs = go.Figure(go.Bar(
        x=list(counts), y=list(qs), orientation="h",
        marker=dict(color=colors_q, line=dict(width=0)),
        text=[str(c) for c in counts], textposition="outside",
        textfont=dict(color="#1F2937", size=12),
        hovertemplate="<b>%{y}</b><br>%{x} preguntas este mes<extra></extra>",
    ))
    fig_qs.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,.05)", tickfont=dict(color="#6B7280", size=11), range=[0, 110]),
        yaxis=dict(showgrid=False, tickfont=dict(color="#111827", size=11)),
        margin=dict(t=20, b=12, l=8, r=50), height=280,
        title=dict(text="PREGUNTAS MÁS FRECUENTES · ESTE MES", font=dict(size=11, color="#374151"), x=0),
        hoverlabel=dict(bgcolor="#fff", bordercolor="#E5E5E5", font=dict(color="#0D0D0D", size=12)),
    )
    st.plotly_chart(fig_qs, use_container_width=True)

with col_insight:
    st.markdown(
        f'<div style="background:#0D0D0D;border-radius:16px;padding:22px;color:#fff;height:100%;">'
        f'<div style="font-family:\'Syne\',sans-serif;font-size:.72rem;font-weight:800;text-transform:uppercase;'
        f'letter-spacing:.12em;color:rgba(255,255,255,.3);margin-bottom:12px;">INSIGHT DEL MES</div>'
        + "".join(
            f'<div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);'
            f'border-radius:10px;padding:10px 12px;margin-bottom:8px;">'
            f'<div style="font-size:.75rem;font-weight:600;color:#fff;margin-bottom:3px;">{title}</div>'
            f'<div style="font-size:.7rem;color:rgba(255,255,255,.5);line-height:1.45;">{desc}</div></div>'
            for title, desc in [
                ("Devoluciones = 28% de preguntas",     "Documentación clara pero el proceso de Reveni genera fricción. Revisar los pasos del portal con el equipo."),
                ("Tallas: siempre en los primeros días", "Pico de preguntas sobre tallas en las 72h post-drop. Preparar FAQ de tallas antes de cada lanzamiento."),
                ("0 preguntas sin responder este mes",   "El asistente resolvió el 87% directamente. Solo 13% necesitó escalado a manager."),
            ]
        )
        + '</div>',
        unsafe_allow_html=True,
    )


# =============================================================================
# SECTION 05 — ONBOARDING 7 DÍAS
# =============================================================================
st.markdown('<div class="sec-hdr"><span class="sec-num">05</span><h2 class="sec-ttl">ONBOARDING AUTOMATIZADO · 7 DÍAS</h2><div class="sec-line"></div></div>', unsafe_allow_html=True)

st.markdown(
    '<div style="font-size:.88rem;color:#6B7280;margin:-8px 0 18px;max-width:760px;line-height:1.6;">'
    'El asistente guía al nuevo empleado durante los primeros 7 días con mensajes proactivos, respuestas a sus preguntas '
    'y un quiz informal para confirmar que ha asimilado los puntos clave.</div>',
    unsafe_allow_html=True,
)

onboarding_steps = [
    ("1",  "Día 1",   "Bienvenida + accesos",      "Presenta la marca, envía los accesos y explica la estructura del equipo."),
    ("2",  "Día 2",   "Producto y tallas",          "Guía completa de producto, cómo funciona el catálogo y cómo recomendar tallas."),
    ("3",  "Día 3",   "Devoluciones y logística",   "Protocolo paso a paso con Reveni, incidencias de tracking y cómo hablar con el cliente."),
    ("4",  "Día 5",   "Drops y comunicación",       "Cómo funcionan los drops, qué se puede decir y qué no antes del anuncio oficial."),
    ("5",  "Día 7",   "Quiz + primeras dudas",      "Quiz informal de 5 preguntas para detectar gaps. Informe al manager con áreas de mejora."),
]

cells = []
for i, (num, day, title, desc) in enumerate(onboarding_steps):
    cells.append(
        f'<div class="pipe-step">'
        f'<div class="pipe-step-num" style="animation-delay:{i*0.35}s;">{num}</div>'
        f'<div class="pipe-step-ttl">{day} · {title}</div>'
        f'<div class="pipe-step-desc">{desc}</div>'
        f'</div>'
    )
    if i < len(onboarding_steps) - 1:
        cells.append(f'<div class="pipe-arrow">{_icon("arrow-right", 18, "#BFDBFE")}</div>')

st.markdown(
    f'<div class="pipe-wrap">'
    f'<div style="font-family:\'Syne\',sans-serif;font-size:.72rem;font-weight:800;text-transform:uppercase;'
    f'letter-spacing:.12em;color:#9CA3AF;margin-bottom:14px;text-align:center;">Del día 1 a la autonomía completa</div>'
    f'<div class="pipe-flow">{"".join(cells)}</div></div>',
    unsafe_allow_html=True,
)

imp_cols = st.columns(3)
for col, (val, lbl, sub, color) in zip(imp_cols, [
    ("8h/sem", "Tiempo de managers recuperado", "Actualmente en preguntas repetitivas", AC),
    ("7 días",  "Onboarding completo",            "vs 3-4 semanas sin asistente",         "#22C55E"),
    ("40€/mes", "Coste total del stack",          "vs ~200€/mes por hora de manager",     "#F97316"),
]):
    with col:
        st.markdown(
            f'<div style="background:{AC_L};border:1px solid {AC_B};border-radius:12px;padding:18px;text-align:center;">'
            f'<div style="font-family:\'Syne\',sans-serif;font-size:1.8rem;font-weight:800;color:{color};line-height:1;margin-bottom:4px;">{val}</div>'
            f'<div style="font-size:.75rem;font-weight:600;color:#0D0D0D;margin-bottom:3px;">{lbl}</div>'
            f'<div style="font-size:.65rem;color:#9CA3AF;">{sub}</div></div>',
            unsafe_allow_html=True,
        )

# =============================================================================
# SECTION 06 — ARQUITECTURA OPERATIVA
# =============================================================================
st.markdown('<div class="sec-hdr"><span class="sec-num">06</span><h2 class="sec-ttl">ARQUITECTURA OPERATIVA · CÓMO SE IMPLEMENTA</h2><div class="sec-line"></div></div>', unsafe_allow_html=True)

st.markdown(
    '<div style="font-size:.88rem;color:#6B7280;margin:-8px 0 18px;max-width:880px;line-height:1.6;">'
    'Ops Assistant es una capa de conocimiento operativo para tiendas, oficinas y CX. La clave es que no inventa: '
    '<strong style="color:#0D0D0D;">responde con fuentes, detecta cuándo escalar y convierte cada duda repetida en mejora de procesos.</strong></div>',
    unsafe_allow_html=True,
)

ops_arch = [
    ("1", "Fuentes oficiales", "Notion/Drive, políticas, guías de tallas, protocolos, calendario de drops y documentos RRHH.", "book-open"),
    ("2", "Indexación", "Python limpia documentos, separa versiones, crea chunks y guarda embeddings/metadatos en SQL/vector store.", "database"),
    ("3", "Consulta", "WhatsApp, Slack o web interna. El empleado pregunta en lenguaje natural desde tienda u oficina.", "message-circle"),
    ("4", "Respuesta con fuente", "Claude responde solo con información encontrada, muestra confianza y cita documento/version.", "bot"),
    ("5", "Escalado y aprendizaje", "Si falta información, escala a manager y crea tarea para actualizar la base de conocimiento.", "refresh-cw"),
]

arch_cols = st.columns(5)
for col, (n, title, desc, icon_name) in zip(arch_cols, ops_arch):
    with col:
        st.markdown(
            f'<div style="background:#fff;border:1.5px solid #E5E5E5;border-radius:12px;padding:16px;height:100%;text-align:center;">'
            f'<div style="margin:0 auto 10px;width:34px;height:34px;border-radius:50%;background:{AC_L};color:{AC};display:flex;align-items:center;justify-content:center;">{_icon(icon_name,17,AC)}</div>'
            f'<div style="font-family:\'Syne\',sans-serif;font-size:1.2rem;font-weight:800;color:{AC};line-height:1;">{n}</div>'
            f'<div style="font-size:.78rem;font-weight:700;color:#0D0D0D;margin:8px 0 5px;">{title}</div>'
            f'<div style="font-size:.68rem;color:#6B7280;line-height:1.45;">{desc}</div></div>',
            unsafe_allow_html=True,
        )

col_stack, col_guard = st.columns([1.2, 1])
with col_stack:
    stack_rows = [
        ("Canales", "WhatsApp / Slack / Web", "Entrada natural para tienda, oficina, CX y managers."),
        ("Orquestación", "n8n", "Sincroniza documentos, manda recordatorios, escala casos y registra métricas."),
        ("IA", "Claude Haiku/Sonnet", "Haiku para FAQ barata; Sonnet para casos complejos y resúmenes."),
        ("Datos", "SQL + vector store", "Preguntas, fuentes, confianza, escalados, gaps y uso por equipo."),
        ("Dashboards", "Grafana", "Volumen de dudas, temas recurrentes, tiempos ahorrados y documentos obsoletos."),
        ("Construcción", "Codex / Claude Code", "Módulos, conectores, tests, prompts versionados y mejoras semanales."),
    ]
    st.markdown(
        '<div style="background:#F8F8F6;border:1px solid #EBEBEB;border-radius:14px;padding:18px 20px;">'
        '<div style="font-family:\'Syne\',sans-serif;font-size:.75rem;font-weight:800;text-transform:uppercase;letter-spacing:.12em;color:#9CA3AF;margin-bottom:12px;">Stack propuesto para fase 1</div>'
        + "".join(
            f'<div style="display:grid;grid-template-columns:110px 145px 1fr;gap:10px;border-top:1px solid #E5E5E5;padding:10px 0;align-items:start;">'
            f'<div style="font-size:.72rem;font-weight:700;color:#0D0D0D;">{area}</div>'
            f'<div style="font-size:.72rem;color:{AC};font-weight:700;">{tool}</div>'
            f'<div style="font-size:.7rem;color:#6B7280;line-height:1.4;">{why}</div></div>'
            for area, tool, why in stack_rows
        )
        + '</div>',
        unsafe_allow_html=True,
    )
with col_guard:
    guardrails = [
        ("No responde sin fuente", "Si no encuentra documento válido, reconoce límite y escala."),
        ("Versionado", "Cada respuesta cita documento y fecha para evitar políticas antiguas."),
        ("Permisos", "RRHH, descuentos y datos internos solo para perfiles autorizados."),
        ("Feedback", "El empleado puede marcar respuesta útil, incorrecta o incompleta."),
    ]
    st.markdown(
        f'<div style="background:#0D0D0D;border-radius:16px;padding:22px;color:#fff;height:100%;">'
        f'<div style="font-family:\'Syne\',sans-serif;font-size:.72rem;font-weight:800;text-transform:uppercase;letter-spacing:.12em;color:rgba(255,255,255,.35);margin-bottom:14px;">Guardrails del asistente</div>'
        + "".join(
            f'<div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:10px;padding:10px 12px;margin-bottom:9px;">'
            f'<div style="font-size:.76rem;font-weight:800;color:#fff;margin-bottom:3px;">{title}</div>'
            f'<div style="font-size:.7rem;color:rgba(255,255,255,.55);line-height:1.45;">{desc}</div></div>'
            for title, desc in guardrails
        )
        + '</div>',
        unsafe_allow_html=True,
    )


# =============================================================================
# SECTION 07 — CASOS DE USO Y VALOR POR EQUIPO
# =============================================================================
st.markdown('<div class="sec-hdr"><span class="sec-num">07</span><h2 class="sec-ttl">CASOS DE USO · VALOR POR EQUIPO</h2><div class="sec-line"></div></div>', unsafe_allow_html=True)

use_cols = st.columns(4)
for col, (team, pain, solution, impact, color) in zip(use_cols, [
    ("Tienda", "Dudas en directo con cliente delante.", "Respuestas inmediatas sobre tallas, devoluciones, stock y discurso de drop.", "Más confianza y menos errores.", AC),
    ("CX", "Tickets repetidos y criterios distintos.", "Protocolos claros, macros sugeridas y escalado cuando hay excepción.", "Menos tiempo por ticket.", "#F97316"),
    ("Managers", "Interrupciones constantes por WhatsApp.", "Resumen semanal de dudas, gaps y documentos que actualizar.", "8h/sem liberadas.", "#22C55E"),
    ("RRHH", "Onboarding depende de quien forme.", "Ruta de 7 días, quiz, seguimiento y checklist de accesos.", "Ramp-up más rápido.", "#A855F7"),
]):
    with col:
        st.markdown(
            f'<div style="background:#fff;border:1.5px solid #E5E5E5;border-radius:12px;padding:16px;height:100%;">'
            f'<div style="font-family:\'Syne\',sans-serif;font-weight:800;color:{color};font-size:.86rem;margin-bottom:9px;">{team}</div>'
            f'<div style="font-size:.64rem;font-weight:800;letter-spacing:.08em;color:#9CA3AF;text-transform:uppercase;margin-bottom:3px;">Dolor actual</div>'
            f'<div style="font-size:.72rem;color:#6B7280;line-height:1.45;margin-bottom:10px;">{pain}</div>'
            f'<div style="font-size:.64rem;font-weight:800;letter-spacing:.08em;color:#9CA3AF;text-transform:uppercase;margin-bottom:3px;">Solución</div>'
            f'<div style="font-size:.72rem;color:#374151;line-height:1.45;margin-bottom:12px;">{solution}</div>'
            f'<div style="border-top:1px solid #E5E5E5;padding-top:8px;font-size:.68rem;color:{color};font-weight:800;">{impact}</div></div>',
            unsafe_allow_html=True,
        )

col_before, col_after = st.columns(2)
with col_before:
    st.markdown(
        '<div style="background:#FEF2F2;border:1px solid #FECACA;border-radius:14px;padding:18px;">'
        '<div style="font-family:\'Syne\',sans-serif;font-weight:800;color:#7F1D1D;margin-bottom:10px;">Antes</div>'
        '<div style="font-size:.74rem;color:#7F1D1D;line-height:1.65;">'
        '• Preguntas por WhatsApp a cualquier hora<br>'
        '• Respuestas distintas según quién esté disponible<br>'
        '• Documentación perdida en emails o conversaciones<br>'
        '• Nuevo empleado tarda semanas en sentirse autónomo<br>'
        '• El manager no sabe qué dudas se repiten realmente</div></div>',
        unsafe_allow_html=True,
    )
with col_after:
    st.markdown(
        f'<div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:14px;padding:18px;">'
        f'<div style="font-family:\'Syne\',sans-serif;font-weight:800;color:#14532D;margin-bottom:10px;">Después</div>'
        f'<div style="font-size:.74rem;color:#14532D;line-height:1.65;">'
        f'• Respuesta en segundos con fuente citada<br>'
        f'• Misma política para todos los equipos<br>'
        f'• Gaps convertidos en tareas de documentación<br>'
        f'• Onboarding guiado y medible en 7 días<br>'
        f'• Managers ven analytics y atacan causas, no síntomas</div></div>',
        unsafe_allow_html=True,
    )


# =============================================================================
# SECTION 08 — ROADMAP, ROI Y RIESGOS
# =============================================================================
st.markdown('<div class="sec-hdr"><span class="sec-num">08</span><h2 class="sec-ttl">ROADMAP CEO · ROI Y RIESGOS</h2><div class="sec-line"></div></div>', unsafe_allow_html=True)

tab_road, tab_roi, tab_risks = st.tabs(["Roadmap 30-60-90", "ROI esperado", "Riesgos y control"])

with tab_road:
    roadmap = [
        ("0-30 días", "MVP interno", "Base de conocimiento inicial, 50-80 preguntas frecuentes, Slack/web demo, respuestas con fuente y escalado manual.", "Piloto con tienda + CX."),
        ("31-60 días", "Canales y métricas", "WhatsApp/Slack, n8n para sync de docs, logs SQL, dashboard Grafana y feedback de utilidad.", "Managers ven qué se pregunta y dónde falta proceso."),
        ("61-90 días", "Ops OS", "Onboarding completo, alertas de docs obsoletos, resúmenes semanales y automatización de tareas de mejora.", "El conocimiento operativo deja de depender de memoria individual."),
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

with tab_roi:
    fig_roi = go.Figure(go.Waterfall(
        orientation="v",
        measure=["relative", "relative", "relative", "relative", "total"],
        x=["Managers", "Onboarding", "Errores evitados", "Coste stack", "Valor neto/mes"],
        y=[960, 450, 300, -40, 1670],
        connector={"line": {"color": "#D1D5DB"}},
        increasing={"marker": {"color": "#22C55E"}},
        decreasing={"marker": {"color": "#EF4444"}},
        totals={"marker": {"color": AC}},
        text=["+960€", "+450€", "+300€", "-40€", "~1.670€"],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>%{y}€ estimados<extra></extra>",
    ))
    fig_roi.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(248,248,246,1)",
        yaxis=dict(title="Valor mensual estimado (€)", gridcolor="rgba(0,0,0,.05)", tickfont=dict(color="#6B7280", size=11)),
        xaxis=dict(tickfont=dict(color="#111827", size=11)),
        margin=dict(t=25, b=20, l=55, r=25), height=300,
        title=dict(text="ROI ESTIMADO · CONSERVADOR", font=dict(size=11, color="#374151"), x=0),
    )
    st.plotly_chart(fig_roi, use_container_width=True)
    st.markdown(
        f'<div style="font-size:.76rem;color:#6B7280;text-align:center;">Asumiendo 8h/semana de manager recuperadas, onboarding más corto y coste stack aproximado de <strong style="color:{AC};">40€/mes</strong>.</div>',
        unsafe_allow_html=True,
    )

with tab_risks:
    risks = [
        ("Respuesta incorrecta", "Una política mal interpretada puede generar errores con clientes.", "RAG con fuentes, confianza visible y escalado si no hay fuente clara."),
        ("Documentación obsoleta", "El asistente será tan bueno como la base de conocimiento.", "Dueño por dominio, fecha de revisión y alertas de documento antiguo."),
        ("Baja adopción", "El equipo puede seguir preguntando por WhatsApp al manager.", "Integrarlo en los canales existentes y medir/responder rápido desde el día uno."),
        ("Permisos internos", "No todos deben ver información de RRHH, costes o campañas futuras.", "Roles por usuario, logs y separación de documentos sensibles."),
    ]
    for title, risk, mitigation in risks:
        st.markdown(
            f'<div style="display:grid;grid-template-columns:170px 1fr 1fr;gap:12px;margin-bottom:10px;">'
            f'<div style="background:#111827;color:#fff;border-radius:10px;padding:12px;font-weight:800;font-size:.78rem;">{title}</div>'
            f'<div style="background:#FEF2F2;border:1px solid #FECACA;border-radius:10px;padding:12px;font-size:.72rem;color:#7F1D1D;line-height:1.45;"><strong>Riesgo:</strong> {risk}</div>'
            f'<div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:10px;padding:12px;font-size:.72rem;color:#14532D;line-height:1.45;"><strong>Control:</strong> {mitigation}</div></div>',
            unsafe_allow_html=True,
        )

_footer()
