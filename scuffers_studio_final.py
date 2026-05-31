# scuffers_studio_final.py  ·  Scuffers Studio Demo · Scuffers
# Run: python3 -m streamlit run scuffers_studio_final.py

import re, io, base64, functools
from pathlib import Path
from typing import Optional
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
    "sparkles":   '<path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3z"/><path d="M5 3v4"/><path d="M19 17v4"/><path d="M3 5h4"/><path d="M17 19h4"/>',
    "mail":       '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
    "instagram":  '<rect width="20" height="20" x="2" y="2" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" x2="17.51" y1="6.5" y2="6.5"/>',
    "globe":      '<circle cx="12" cy="12" r="10"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/><path d="M2 12h20"/>',
    "newspaper":  '<path d="M4 3h16a2 2 0 0 1 2 2v15a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V5a2 2 0 0 1 2-2z"/><path d="M8 7h6"/><path d="M8 11h8"/><path d="M8 15h6"/>',
    "zap":        '<path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.81a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.81a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"/>',
    "dollar-sign":'<line x1="12" x2="12" y1="2" y2="22"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>',
    "arrow-right":'<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    "clock":      '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "check":      '<path d="M20 6 9 17l-5-5"/>',
    "database":   '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19A9 3 0 0 0 21 19V5"/><path d="M3 12A9 3 0 0 0 21 12"/>',
    "layers":     '<path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/>',
}

def _icon(name, size=16, color="currentColor", **kw):
    return _lucide_svg(_L.get(name, ""), size=size, color=color, **kw)


# ─── LOGO HANDLING ─────────────────────────────────────────────────────────────
@functools.lru_cache(maxsize=1)
def _fallback_page_icon_path():
    p = Path(__file__).resolve().parent / "_studio_tab_fallback.png"
    if not p.is_file():
        im = _PILImg.new("RGBA", (64, 64), (0, 0, 0, 0))
        from PIL import ImageDraw
        d = ImageDraw.Draw(im)
        d.rectangle([8, 8, 56, 56], fill=(124, 58, 237, 255))
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
AC   = "#7C3AED"
AC_D = "#5B21B6"
AC_L = "#F5F3FF"
AC_B = "#DDD6FE"

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Scuffers Studio · Demo",
    page_icon=_LOG_FAV if _LOG_FAV else _fallback_page_icon_path(),
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── SESSION STATE ─────────────────────────────────────────────────────────────
def _ss(k, v):
    if k not in st.session_state:
        st.session_state[k] = v

_ss("email_gen", False); _ss("email_seg", "Champions")
_ss("caption_gen", False); _ss("caption_type", "Drop reveal")
_ss("news_gen", False)
_ss("trans_gen", False); _ss("trans_lang", "Inglés")

# ─── CONTENT DATA ─────────────────────────────────────────────────────────────
def _md(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    return text.replace('\n', '<br>')

EMAIL_OUTPUTS = {
    "Champions": {
        "subject": "Vosotros primero — Drop Sombra 🖤",
        "body": "Crew,\n\nNo se lo hemos dicho a nadie todavía.\n\nPero vosotros lleváis con Scuffers desde el principio, y eso merece algo que no va a salir en Instagram hasta el viernes por la tarde.\n\n**Drop Sombra llega este viernes a las 18:00h.**\nPara vosotros, 2 horas antes que el resto.\n\n12 piezas. Sin restock. Sin segunda oportunidad.\n\n→ **[Acceso anticipado — solo para ti]**\n\nGracias por hacer que esto sea real.\n— Scuffers",
        "seg": "Champions · top 15% compradores por gasto anual",
        "time": "0.8s",
    },
    "En Riesgo": {
        "subject": "¿Sigues aquí? 👋",
        "body": "Hola,\n\nHace 94 días que no sabemos de ti — y la verdad es que te echamos de menos.\n\nMucho ha pasado: nuevo drop, nueva tienda en Valencia, y el que más se habló este otoño en Madrid.\n\nPara que te pongas al día — y para agradecerte que hayas sido parte de esto:\n\n**15% en tu próxima compra con el código: DEVUELTA15**\nVálido 7 días. Solo para ti.\n\n→ **[Ver lo que te has perdido]**\n\n— Scuffers",
        "seg": "En Riesgo · sin compra en 90+ días",
        "time": "1.1s",
    },
    "Primera Compra": {
        "subject": "Bienvenido a la Crew 🤍",
        "body": "Hola,\n\nTu pedido está en camino — pero queremos aprovechar para contarte algo.\n\nScuffers no nació para ser una marca más. Nació en Madrid en 2018 porque había algo que los de aquí no encontraban en ningún otro sitio: ropa que se siente tan tuya como la ciudad.\n\nAcabas de entrar. **Bienvenido a la Crew.**\n\nLo que no se dice en público:\n→ Los drops se anuncian 48h antes en la newsletter\n→ Los OGs tienen acceso antes que nadie\n→ Cada pieza lleva una historia detrás\n\n→ **[Explorar el universo Scuffers]**\n\n— Scuffers",
        "seg": "Primera Compra · cliente nuevo",
        "time": "0.9s",
    },
}

CAPTION_OUTPUTS = {
    "Drop reveal": "Drop Sombra 👁️\n\nLo que ves no es todo lo que es.\n\nViernes. 20:00h.\n12 piezas. Sin restock.\n\nEl que lo vio, sabe.\nEl que no... activa la campana. 🔔\n\n#Scuffers #DropSombra #Streetwear #Madrid #DropAlert #NuevaColeccion",
    "Behind the scenes": "Así nace un drop. 🎬\n\nMeses de trabajo resumidos en 60 segundos 👀\n\nNo todo empieza en un estudio perfecto. Empieza en conversaciones, bocetos en servilletas, en decir que no diez veces antes de decir sí.\n\nEste es el Drop Sombra. Esto es lo que hay detrás.\n\n5 de junio en YouTube.\n\n#Scuffers #BehindTheScenes #DropSombra #MadeInMadrid",
    "Restock anuncio": "Atención, Crew 🚨\n\nSí. Habéis hablado.\n\nLas tallas S y M del Drop Sombra vuelven el miércoles a las 12:00h.\nStock limitado — no hay segunda vuelta.\n\nSi no lo pillaste la primera vez, este es tu momento.\n\n→ Link en bio para activar notificación.\n\n#Scuffers #Restock #DropSombra #AgotadoDeNuevo",
}

NEWSLETTER_SECTION = """**NUEVO DROP · SOMBRA**

Algunas prendas no se diseñan para gustarte.

Se diseñan para que no puedas dejar de mirarlas.

El Drop Sombra nació de una conversación sobre qué pasa cuando el streetwear deja de intentar gustar y empieza a decir algo. Son 12 piezas. Cada una con una historia que no vamos a contar en voz alta — porque hay cosas que se sienten o no se sienten.

**Este viernes, 20:00h.** Sin aviso previo en Instagram. Sin restock.

→ [Ver el drop]

---

**BEHIND THE SCENES · LA HISTORIA**

Habría sido fácil hacer otro drop de sudaderas oversized. Lo difícil era encontrar el punto donde la comodidad deja de ser comodidad y empieza a ser actitud.

El 5 de junio, el documental completo en YouTube.

---

**COMUNIDAD · LO QUE PASÓ ESTE MES**

Nathy Peluso llevó la Sombra Hoodie en su último show en Madrid. Sin contrato. Sin acuerdo. Solo porque le gustó. Y eso, en 2026, vale más que cualquier campaña."""

TRANSLATIONS = {
    "Inglés": {
        "orig": "Drop Sombra 👁️\n\nLo que ves no es todo lo que es.\n\nViernes. 20:00h. 12 piezas. Sin restock.\n\n#Scuffers #DropSombra #Streetwear",
        "trans": "Drop Shadow 👁️\n\nWhat you see isn't all there is.\n\nFriday. 8pm CET. 12 pieces. No restock.\n\n#Scuffers #DropShadow #Streetwear #Madrid",
        "note": "Tono mantenido: misterioso, directo, exclusivo. 'Sin restock' adaptado culturalmente.",
    },
    "Alemán": {
        "orig": "Drop Sombra 👁️\n\nLo que ves no es todo lo que es.\n\nViernes. 20:00h. 12 piezas. Sin restock.",
        "trans": "Drop Shadow 👁️\n\nWas du siehst, ist nicht alles.\n\nFreitag. 20:00 Uhr. 12 Teile. Kein Restock.\n\n#Scuffers #DropShadow #Streetwear #Madrid",
        "note": "Alemán directo y conciso. Formato de hora europeo. Estética de marca conservada.",
    },
    "Francés": {
        "orig": "Drop Sombra 👁️\n\nLo que ves no es todo lo que es.\n\nViernes. 20:00h. 12 piezas. Sin restock.",
        "trans": "Drop Ombre 👁️\n\nCe que tu vois n'est pas tout ce qu'il y a.\n\nVendredi. 20h00. 12 pièces. Pas de restock.\n\n#Scuffers #DropOmbre #Streetwear #Madrid",
        "note": "'Sombra' adaptado a 'Ombre' para resonancia cultural. Tono editorial mantenido.",
    },
    "Italiano": {
        "orig": "Drop Sombra 👁️\n\nLo que ves no es todo lo que es.\n\nViernes. 20:00h. 12 piezas. Sin restock.",
        "trans": "Drop Ombra 👁️\n\nQuello che vedi non è tutto ciò che è.\n\nVenerdì. 20:00. 12 pezzi. Nessun restock.\n\n#Scuffers #DropOmbra #Streetwear #Madrid",
        "note": "Cadencia poética natural en italiano. Tone of voice Scuffers al 100%.",
    },
}

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
.kpi-card.purple{{border-top:3px solid {AC}}}
.kpi-card.green{{border-top:3px solid #22C55E}}
.insight-card{{background:#fff;border:1.5px solid #E5E5E5;border-radius:12px;padding:18px;border-left:4px solid #EF4444;height:100%;transition:border-color .2s,box-shadow .2s}}
.insight-card:hover{{border-left-color:{AC};box-shadow:0 4px 16px rgba(124,58,237,.08)}}
.insight-cat{{font-family:'Syne',sans-serif;font-size:.85rem;font-weight:700;margin-bottom:4px}}
.insight-finding{{font-size:.78rem;color:#6B7280;line-height:1.5;margin-bottom:8px}}
.insight-action{{font-size:.75rem;font-weight:600;color:{AC};background:{AC_L};padding:5px 10px;border-radius:6px;display:inline-block}}
.gen-card{{background:{AC_L};border:1.5px solid {AC_B};border-radius:12px;padding:20px 24px;margin-top:8px;animation:fadeIn .5s ease both}}
.gen-label{{font-size:.62rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:{AC};margin-bottom:10px;display:flex;align-items:center;gap:7px}}
.gen-body{{font-size:.86rem;color:#1F2937;line-height:1.75}}
.gen-meta{{margin-top:12px;padding-top:10px;border-top:1px solid {AC_B};display:flex;align-items:center;gap:12px;flex-wrap:wrap}}
.gen-tag{{font-size:.65rem;font-weight:600;background:rgba(124,58,237,.08);color:{AC};padding:2px 8px;border-radius:99px}}
.gen-time{{font-size:.65rem;color:#9CA3AF}}
.subj-lbl{{font-size:.6rem;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:#9CA3AF;margin-bottom:3px}}
.subj-line{{background:#fff;border:1px solid #E5E5E5;border-radius:8px;padding:10px 14px;margin-bottom:12px;font-size:.85rem;font-weight:600;color:#0D0D0D}}
.stTabs [data-baseweb="tab-list"]{{gap:0;border-bottom:1px solid #E5E5E5}}
.stTabs [data-baseweb="tab"]{{font-size:.82rem;font-weight:500;color:#6B7280;padding:10px 20px;border-bottom:2px solid transparent}}
.stTabs [aria-selected="true"]{{color:{AC}!important;border-bottom-color:{AC}!important;font-weight:600!important}}
.stButton>button{{font-size:.82rem!important;border-radius:8px!important;border:1.5px solid {AC}!important;background:{AC}!important;color:#fff!important;padding:6px 16px!important}}
.stButton>button:hover{{background:{AC_D}!important;border-color:{AC_D}!important}}
.empty-state{{background:#F8F8F6;border:1px dashed #E5E5E5;border-radius:12px;padding:40px;text-align:center;margin-top:8px}}
.cache-box{{background:#0D0D0D;border-radius:16px;padding:24px 28px;color:#fff}}
@keyframes fadeIn{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:translateY(0)}}}}
</style>
""", unsafe_allow_html=True)


# ─── NAVBAR ───────────────────────────────────────────────────────────────────
_nav_logo = f'<img src="{_LOGO_NAV}" alt="Scuffers" style="height:22px;width:auto;vertical-align:middle;margin-right:10px;">' if _LOGO_NAV else ""
_hl, _ = st.columns([3, 1], gap="medium")
with _hl:
    st.markdown(
        '<div style="padding:6px 0 10px;"><div style="display:flex;align-items:center;flex-wrap:wrap;gap:14px;">'
        f'<div style="font-family:\'Syne\',sans-serif;font-size:1rem;font-weight:800;letter-spacing:.04em;display:flex;align-items:center;">'
        f'{_nav_logo}SCUFFERS STUDIO <span style="font-weight:400;color:#9CA3AF;font-size:.85rem;">· Herramienta Interna de Contenido IA</span></div>'
        f'<div class="demo-badge">{_icon("sparkles", 14, "#9CA3AF")} Demo · Contenido generado con Claude API</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )
st.markdown('<div style="border-bottom:1px solid #E5E5E5;margin:0 0 10px 0;"></div>', unsafe_allow_html=True)


def _footer():
    _fl = f'<img src="{_LOGO_FOOT}" alt="" style="height:18px;width:auto;vertical-align:middle;margin-right:8px;">' if _LOGO_FOOT else ""
    st.markdown(
        f'<div style="text-align:center;margin-top:3rem;padding-top:1.5rem;border-top:1px solid #E5E5E5;'
        f'font-size:.68rem;color:#9CA3AF;letter-spacing:.06em;display:flex;align-items:center;justify-content:center;gap:4px;">'
        f'{_fl}SCUFFERS STUDIO · Demo · Fase 1 Quick Win · ~100€/mes</div>',
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
        f'<span style="display:inline-block;width:20px;height:2px;background:{AC};"></span>FASE 1 · QUICK WIN · ~100€/MES</div>'
        '<div style="font-family:\'Syne\',sans-serif;font-size:clamp(1.8rem,3vw,2.7rem);font-weight:800;'
        'line-height:1.15;color:#0D0D0D;margin-bottom:1rem;">'
        f'El equipo produce en <br><span style="color:{AC};">1 hora</span> lo que<br>'
        '<span style="font-size:.55em;font-weight:400;color:#6B7280;">antes costaba un día completo.</span></div>'
        '<div style="font-size:.9rem;color:#6B7280;line-height:1.65;max-width:480px;">'
        'Scuffers Studio es la herramienta interna donde el tono de marca, el brand book y el conocimiento de '
        f'la comunidad están precargados. <strong style="color:#0D0D0D;">Claude genera. El equipo aprueba.</strong></div>',
        unsafe_allow_html=True,
    )

with hero_r:
    h1, h2 = st.columns(2)
    with h1:
        st.markdown(f'<div class="kpi-card purple"><div class="kpi-lbl">Producción</div><div class="kpi-val" style="color:{AC};">×10</div><div class="kpi-sub">1h vs 1 día por pieza</div></div>', unsafe_allow_html=True)
    with h2:
        st.markdown(f'<div class="kpi-card purple"><div class="kpi-lbl">Idiomas activos</div><div class="kpi-val" style="color:{AC};">4+1</div><div class="kpi-sub">ES · EN · DE · FR · IT</div></div>', unsafe_allow_html=True)
    st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
    h3, h4 = st.columns(2)
    with h3:
        st.markdown('<div class="kpi-card green"><div class="kpi-lbl">Ahorro vs agencias</div><div class="kpi-val" style="color:#22C55E;">-2k€</div><div class="kpi-sub">por mes (copywriting)</div></div>', unsafe_allow_html=True)
    with h4:
        st.markdown(f'<div class="kpi-card purple"><div class="kpi-lbl">Consistencia de tono</div><div class="kpi-val" style="color:{AC};">100%</div><div class="kpi-sub">Brand book siempre activo</div></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


# =============================================================================
# SECTION 01 — EL PROBLEMA ACTUAL
# =============================================================================
st.markdown('<div class="sec-hdr"><span class="sec-num">01</span><h2 class="sec-ttl">EL PROBLEMA ACTUAL</h2><div class="sec-line"></div></div>', unsafe_allow_html=True)

fig_time = go.Figure()
fig_time.add_trace(go.Bar(
    name="Sin Studio", x=["Email de Drop", "Caption IG/TT", "Newsletter completa", "Traducción"],
    y=[480, 120, 360, 90], marker_color="#E5E7EB",
    text=["480 min", "120 min", "360 min", "90 min"], textposition="outside",
    textfont=dict(color="#6B7280", size=11),
))
fig_time.add_trace(go.Bar(
    name="Con Studio", x=["Email de Drop", "Caption IG/TT", "Newsletter completa", "Traducción"],
    y=[45, 12, 30, 8], marker_color=AC,
    text=["45 min", "12 min", "30 min", "8 min"], textposition="outside",
    textfont=dict(color="#0D0D0D", size=11),
))
fig_time.update_layout(
    barmode="group", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(248,248,246,1)",
    xaxis=dict(gridcolor="rgba(0,0,0,.04)", color="#6B7280", tickfont=dict(color="#111827", size=12)),
    yaxis=dict(title=dict(text="Minutos", font=dict(size=12, color="#4B5563")),
               gridcolor="rgba(0,0,0,.05)", tickfont=dict(color="#6B7280", size=11)),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#374151", size=12)),
    margin=dict(t=20, b=12, l=52, r=24), height=260,
    title=dict(text="TIEMPO POR TIPO DE CONTENIDO (minutos)", font=dict(size=11, color="#374151"), x=0),
    hoverlabel=dict(bgcolor="#fff", bordercolor="#E5E5E5", font=dict(color="#0D0D0D", size=12)),
)
st.plotly_chart(fig_time, use_container_width=True)

ins_cols = st.columns(3)
for i, (icon_name, cat, finding, action) in enumerate([
    ("zap",        "Herramientas sin contexto de marca",    "ChatGPT y Claude se usan sin brand book, sin historial, sin tono Scuffers. Cada pieza empieza desde cero.",           f"{_icon('arrow-right',13,AC)} Studio tiene el brand book precargado como contexto fijo"),
    ("globe",      "Traducciones sin alma de marca",        "Las traducciones actuales son genéricas. El tono de Scuffers se pierde en alemán, francés e italiano.",              f"{_icon('arrow-right',13,AC)} Traductor de Marca: 4 idiomas con tono Scuffers propio"),
    ("dollar-sign","500-2.000€/mes en agencias",           "Para un nivel de calidad inconsistente. El copy de los drops más importantes sale de fuera, sin garantía de tono.",   f"{_icon('arrow-right',13,AC)} Studio produce internamente en horas, no días"),
]):
    with ins_cols[i]:
        st.markdown(
            f'<div class="insight-card"><div style="margin-bottom:8px;">{_icon(icon_name,22,"#6B7280")}</div>'
            f'<div class="insight-cat">{cat}</div><div class="insight-finding">{finding}</div>'
            f'<div class="insight-action">{action}</div></div>',
            unsafe_allow_html=True,
        )

st.markdown(
    f'<div style="background:{AC_L};border:1.5px solid {AC_B};border-radius:14px;padding:20px 28px;'
    f'margin:2.5rem 0;display:flex;align-items:center;gap:20px;">'
    f'<div style="font-size:2rem;flex-shrink:0;">✍️</div>'
    f'<div><div style="font-family:\'Syne\',sans-serif;font-weight:700;font-size:1rem;color:#0D0D0D;margin-bottom:4px;">'
    f'Scuffers Studio: el tono de marca siempre activo, en todos los canales</div>'
    f'<div style="font-size:.84rem;color:#6B7280;">Una herramienta interna donde el brand book, los textos validados y el conocimiento de la comunidad están precargados. '
    f'<strong style="color:{AC};">Claude genera contenido de marca real, no genérico.</strong></div></div></div>',
    unsafe_allow_html=True,
)


# =============================================================================
# SECTION 02 — STUDIO EN ACCIÓN
# =============================================================================
st.markdown('<div class="sec-hdr"><span class="sec-num">02</span><h2 class="sec-ttl">STUDIO EN ACCIÓN</h2><div class="sec-line"></div></div>', unsafe_allow_html=True)

tab_email, tab_caption, tab_news, tab_trans = st.tabs(["📧 Email de Drop", "📱 Caption IG/TikTok", "📰 Newsletter", "🌍 Traducción de Marca"])

# ── EMAIL ──────────────────────────────────────────────────────────────────────
with tab_email:
    cl, cr = st.columns([1, 1.6])
    with cl:
        st.markdown('<div style="padding-top:8px;">', unsafe_allow_html=True)
        seg = st.selectbox("Segmento de cliente", ["Champions", "En Riesgo", "Primera Compra"], key="email_seg_sel")
        desc = {"Champions": "Top 15% compradores · Acceso anticipado · Tono insider exclusivo",
                "En Riesgo": "Sin compra 90+ días · Incentivo personalizado · Tono de reencuentro",
                "Primera Compra": "Cliente nuevo · Presentación de marca · Tono de bienvenida"}[seg]
        st.markdown(f'<div style="font-size:.75rem;color:#6B7280;margin:4px 0 14px;padding:8px 12px;background:#F8F8F6;border-radius:8px;border-left:3px solid {AC};">{desc}</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:.75rem;color:#9CA3AF;margin-bottom:8px;"><strong>Drop:</strong> Drop Sombra · Viernes 20:00h · 12 piezas</div>', unsafe_allow_html=True)
        if st.button("Generar email", key="gen_email_btn"):
            st.session_state.email_gen = True
            st.session_state.email_seg = seg
        st.markdown('</div>', unsafe_allow_html=True)
    with cr:
        if st.session_state.email_gen:
            out = EMAIL_OUTPUTS.get(st.session_state.email_seg, EMAIL_OUTPUTS["Champions"])
            st.markdown(
                f'<div class="gen-card"><div class="gen-label">{_icon("sparkles",14,AC)} Claude API · generado en {out["time"]}</div>'
                f'<div class="subj-lbl">Asunto</div><div class="subj-line">{out["subject"]}</div>'
                f'<div class="gen-body">{_md(out["body"])}</div>'
                f'<div class="gen-meta"><span class="gen-tag">{out["seg"]}</span>'
                f'<span class="gen-time">{_icon("clock",12,"#9CA3AF")} {out["time"]}</span></div></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown('<div class="empty-state"><div style="font-size:2rem;margin-bottom:8px;">✉️</div><div style="font-size:.85rem;color:#9CA3AF;">Selecciona un segmento y genera el email</div></div>', unsafe_allow_html=True)

# ── CAPTION ────────────────────────────────────────────────────────────────────
with tab_caption:
    cl2, cr2 = st.columns([1, 1.6])
    with cl2:
        st.markdown('<div style="padding-top:8px;">', unsafe_allow_html=True)
        cap_type = st.selectbox("Tipo de publicación", ["Drop reveal", "Behind the scenes", "Restock anuncio"], key="cap_sel")
        st.markdown('<div style="font-size:.75rem;color:#9CA3AF;margin:6px 0 14px;">Instagram + TikTok · Hashtags optimizados por plataforma</div>', unsafe_allow_html=True)
        if st.button("Generar caption", key="gen_cap_btn"):
            st.session_state.caption_gen = True
            st.session_state.caption_type = cap_type
        st.markdown('</div>', unsafe_allow_html=True)
    with cr2:
        if st.session_state.caption_gen:
            out_cap = CAPTION_OUTPUTS.get(st.session_state.caption_type, CAPTION_OUTPUTS["Drop reveal"])
            st.markdown(
                f'<div class="gen-card"><div class="gen-label">{_icon("sparkles",14,AC)} Claude API · 0.6s</div>'
                f'<div class="gen-body">{_md(out_cap)}</div>'
                f'<div class="gen-meta"><span class="gen-tag">Instagram</span><span class="gen-tag">TikTok</span>'
                f'<span class="gen-time">{_icon("clock",12,"#9CA3AF")} 0.6s</span></div></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown('<div class="empty-state"><div style="font-size:2rem;margin-bottom:8px;">📱</div><div style="font-size:.85rem;color:#9CA3AF;">Selecciona el tipo y genera el caption</div></div>', unsafe_allow_html=True)

# ── NEWSLETTER ─────────────────────────────────────────────────────────────────
with tab_news:
    cl3, cr3 = st.columns([1, 1.6])
    with cl3:
        st.markdown('<div style="padding-top:8px;">', unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:.78rem;color:#6B7280;margin-bottom:12px;padding:12px;background:#F8F8F6;border-radius:8px;">'
            '<strong>Brief cargado:</strong><br>• Drop Sombra · 12 piezas oversized<br>'
            '• Inspiración: actitud vs. estética<br>• Collab orgánica Nathy Peluso<br>'
            '• Lanzamiento: viernes 20:00h</div>',
            unsafe_allow_html=True,
        )
        if st.button("Generar newsletter", key="gen_news_btn"):
            st.session_state.news_gen = True
        st.markdown('</div>', unsafe_allow_html=True)
    with cr3:
        if st.session_state.news_gen:
            st.markdown(
                f'<div class="gen-card"><div class="gen-label">{_icon("sparkles",14,AC)} Claude API · 2.1s · 3 secciones</div>'
                f'<div class="gen-body">{_md(NEWSLETTER_SECTION)}</div>'
                f'<div class="gen-meta"><span class="gen-tag">Newsletter mensual</span><span class="gen-tag">3 secciones</span>'
                f'<span class="gen-time">{_icon("clock",12,"#9CA3AF")} 2.1s</span></div></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown('<div class="empty-state"><div style="font-size:2rem;margin-bottom:8px;">📰</div><div style="font-size:.85rem;color:#9CA3AF;">Brief cargado. Haz clic en "Generar newsletter"</div></div>', unsafe_allow_html=True)

# ── TRADUCCIÓN ─────────────────────────────────────────────────────────────────
with tab_trans:
    cl4, cr4 = st.columns([1, 1.6])
    with cl4:
        st.markdown('<div style="padding-top:8px;">', unsafe_allow_html=True)
        lang = st.selectbox("Idioma de destino", ["Inglés", "Alemán", "Francés", "Italiano"], key="trans_sel")
        st.markdown(f'<div style="font-size:.75rem;color:#9CA3AF;margin:6px 0 14px;">No es una traducción genérica. El tono de Scuffers viaja con el texto.</div>', unsafe_allow_html=True)
        if st.button("Traducir con tono Scuffers", key="gen_trans_btn"):
            st.session_state.trans_gen = True
            st.session_state.trans_lang = lang
        st.markdown('</div>', unsafe_allow_html=True)
    with cr4:
        if st.session_state.trans_gen:
            used = st.session_state.trans_lang
            t = TRANSLATIONS.get(used, TRANSLATIONS["Inglés"])
            o1, o2 = st.columns(2)
            with o1:
                st.markdown(
                    f'<div style="background:#F8F8F6;border:1px solid #E5E5E5;border-radius:10px;padding:14px;height:100%;">'
                    f'<div style="font-size:.6rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#9CA3AF;margin-bottom:8px;">ORIGINAL (ES)</div>'
                    f'<div style="font-size:.82rem;color:#374151;line-height:1.6;white-space:pre-wrap;">{t["orig"]}</div></div>',
                    unsafe_allow_html=True,
                )
            with o2:
                st.markdown(
                    f'<div class="gen-card" style="height:100%;margin-top:0;">'
                    f'<div class="gen-label">{_icon("sparkles",14,AC)} {used.upper()} · 0.4s</div>'
                    f'<div style="font-size:.82rem;color:#1F2937;line-height:1.6;white-space:pre-wrap;">{t["trans"]}</div>'
                    f'<div style="margin-top:10px;padding-top:8px;border-top:1px solid {AC_B};font-size:.65rem;color:{AC};font-style:italic;">{t["note"]}</div></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown('<div class="empty-state"><div style="font-size:2rem;margin-bottom:8px;">🌍</div><div style="font-size:.85rem;color:#9CA3AF;">Selecciona idioma y traduce con el tono de Scuffers</div></div>', unsafe_allow_html=True)


# =============================================================================
# SECTION 03 — POR QUÉ ES BARATO Y PRECISO
# =============================================================================
st.markdown('<div class="sec-hdr"><span class="sec-num">03</span><h2 class="sec-ttl">POR QUÉ ES BARATO Y PRECISO</h2><div class="sec-line"></div></div>', unsafe_allow_html=True)

col_cache, col_cost = st.columns([1.4, 1])
with col_cache:
    steps_html = "".join(
        f'<div style="display:flex;gap:14px;align-items:flex-start;">'
        f'<div style="background:{AC};color:#fff;font-family:Syne,sans-serif;font-weight:800;font-size:.72rem;'
        f'width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0;">{n}</div>'
        f'<div><div style="font-weight:600;font-size:.82rem;color:#fff;margin-bottom:2px;">{title}</div>'
        f'<div style="font-size:.75rem;color:rgba(255,255,255,.5);line-height:1.5;">{desc}</div></div></div>'
        for n, title, desc in [
            ("1", "Brand Book como contexto fijo",    "El tono de Scuffers, los valores, el vocabulario y ejemplos de textos buenos entran en el sistema UNA vez."),
            ("2", "Prompt Caching de Claude API",      "Las lecturas repetidas del contexto fijo cuestan un 90% menos. Cada generación lo usa sin pagarlo de nuevo."),
            ("3", "Consistencia garantizada",          "Cada email, caption o newsletter parte del mismo brand book. El tono no varía entre el community del lunes y el del viernes."),
        ]
    )
    st.markdown(
        f'<div class="cache-box"><div style="font-family:\'Syne\',sans-serif;font-size:.72rem;font-weight:800;'
        f'text-transform:uppercase;letter-spacing:.12em;color:rgba(255,255,255,.3);margin-bottom:14px;">PROMPT CACHING · CÓMO FUNCIONA</div>'
        f'<div style="display:flex;flex-direction:column;gap:12px;">{steps_html}</div></div>',
        unsafe_allow_html=True,
    )

with col_cost:
    fig_cost = go.Figure(go.Pie(
        labels=["Brand Book (cacheado)", "Generación de contenido", "Hosting Railway"],
        values=[5, 75, 20],
        marker=dict(colors=[AC, "#A78BFA", AC_B], line=dict(color="#fff", width=2)),
        hole=0.55,
        textfont=dict(size=11),
        hovertemplate="<b>%{label}</b><br>€%{value}/mes<extra></extra>",
    ))
    fig_cost.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", showlegend=True,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#374151", size=11)),
        margin=dict(t=12, b=12, l=12, r=12), height=220,
        annotations=[dict(text="~100€<br>/mes", x=0.5, y=0.5, font_size=14, showarrow=False, font_color=AC, font_family="Syne")],
    )
    st.plotly_chart(fig_cost, use_container_width=True)
    st.markdown(f'<div style="text-align:center;font-size:.72rem;color:#6B7280;margin-top:-8px;">Coste mensual total del stack · <strong style="color:{AC};">~100€</strong></div>', unsafe_allow_html=True)


# =============================================================================
# SECTION 04 — IMPACTO ESPERADO
# =============================================================================
st.markdown('<div class="sec-hdr"><span class="sec-num">04</span><h2 class="sec-ttl">IMPACTO ESPERADO</h2><div class="sec-line"></div></div>', unsafe_allow_html=True)

imp_cols = st.columns(4)
for col, (val, lbl, sub) in zip(imp_cols, [
    ("×10",   "Velocidad de producción",  "1h vs 1 día por pieza de contenido"),
    ("−2k€",  "Ahorro mensual máximo",    "vs agencias externas de copywriting"),
    ("100%",  "Consistencia de tono",     "Brand book en cada generación"),
    ("4+1",   "Idiomas activos",          "ES · EN · DE · FR · IT con tono propio"),
]):
    with col:
        st.markdown(
            f'<div style="background:{AC_L};border:1px solid {AC_B};border-radius:12px;padding:18px;text-align:center;">'
            f'<div style="font-family:\'Syne\',sans-serif;font-size:1.8rem;font-weight:800;color:{AC};line-height:1;margin-bottom:4px;">{val}</div>'
            f'<div style="font-size:.75rem;font-weight:600;color:#0D0D0D;margin-bottom:3px;">{lbl}</div>'
            f'<div style="font-size:.65rem;color:#9CA3AF;">{sub}</div></div>',
            unsafe_allow_html=True,
        )

# =============================================================================
# SECTION 05 — IMPLEMENTACIÓN Y STACK
# =============================================================================
st.markdown('<div class="sec-hdr"><span class="sec-num">05</span><h2 class="sec-ttl">IMPLEMENTACIÓN · STACK Y FLUJO REAL</h2><div class="sec-line"></div></div>', unsafe_allow_html=True)

st.markdown(
    '<div style="font-size:.88rem;color:#6B7280;margin:-8px 0 18px;max-width:860px;line-height:1.6;">'
    'La propuesta no es "usar IA para escribir textos". Es construir un sistema interno con memoria de marca, flujos de aprobación, métricas y automatizaciones. '
    '<strong style="color:#0D0D0D;">Codex/Claude Code construye la herramienta, Claude genera, n8n automatiza, SQL mide y Grafana da visibilidad.</strong></div>',
    unsafe_allow_html=True,
)

arch_cols = st.columns(5)
for col, (n, title, desc, icon_name) in zip(arch_cols, [
    ("1", "Brief del equipo", "Drop, producto, objetivo, canal, segmento y restricciones de comunicación.", "newspaper"),
    ("2", "Brand Brain", "Brand book, ejemplos aprobados, palabras prohibidas, tono por canal e histórico de campañas.", "database"),
    ("3", "Claude API", "Generación con prompts versionados, cache de contexto y variantes A/B listas para revisar.", "sparkles"),
    ("4", "Aprobación humana", "Marketing edita, aprueba y marca qué outputs son buenos para entrenar el sistema.", "check"),
    ("5", "Activación", "Klaviyo/email, Shopify, Instagram/TikTok, newsletter y traducciones sincronizadas por n8n.", "zap"),
]):
    with col:
        st.markdown(
            f'<div style="background:#fff;border:1.5px solid #E5E5E5;border-radius:12px;padding:16px;height:100%;text-align:center;">'
            f'<div style="margin:0 auto 10px;width:34px;height:34px;border-radius:50%;background:{AC_L};color:{AC};display:flex;align-items:center;justify-content:center;">{_icon(icon_name,17,AC)}</div>'
            f'<div style="font-family:\'Syne\',sans-serif;font-size:1.2rem;font-weight:800;color:{AC};line-height:1;">{n}</div>'
            f'<div style="font-size:.78rem;font-weight:700;color:#0D0D0D;margin:8px 0 5px;">{title}</div>'
            f'<div style="font-size:.68rem;color:#6B7280;line-height:1.45;">{desc}</div></div>',
            unsafe_allow_html=True,
        )

stack_l, stack_r = st.columns([1.2, 1])
with stack_l:
    stack_rows = [
        ("Frontend interno", "Streamlit o Next.js", "Panel privado para marketing, e-commerce y brand."),
        ("Orquestación", "n8n", "Generar, aprobar, publicar, traducir y guardar cada pieza automáticamente."),
        ("Modelos", "Claude Sonnet + Haiku", "Sonnet para creatividad; Haiku para clasificar, validar y resumir barato."),
        ("Datos", "SQL + archivos versionados", "Prompts, briefs, outputs, campañas, costes, aprobaciones y performance."),
        ("Observabilidad", "Grafana", "Coste por generación, ratio de aprobación, tiempo ahorrado y rendimiento por canal."),
        ("Construcción", "Codex / Claude Code", "Iteración rápida de módulos, tests, conectores y documentación interna."),
    ]
    st.markdown(
        '<div style="background:#F8F8F6;border:1px solid #EBEBEB;border-radius:14px;padding:18px 20px;">'
        '<div style="font-family:\'Syne\',sans-serif;font-size:.75rem;font-weight:800;text-transform:uppercase;letter-spacing:.12em;color:#9CA3AF;margin-bottom:12px;">Stack propuesto fase 1</div>'
        + "".join(
            f'<div style="display:grid;grid-template-columns:130px 135px 1fr;gap:10px;border-top:1px solid #E5E5E5;padding:10px 0;align-items:start;">'
            f'<div style="font-size:.72rem;font-weight:700;color:#0D0D0D;">{area}</div>'
            f'<div style="font-size:.72rem;color:{AC};font-weight:700;">{tool}</div>'
            f'<div style="font-size:.7rem;color:#6B7280;line-height:1.4;">{why}</div></div>'
            for area, tool, why in stack_rows
        )
        + '</div>',
        unsafe_allow_html=True,
    )
with stack_r:
    fig_quality = go.Figure(go.Scatterpolar(
        r=[92, 88, 86, 95, 82, 90],
        theta=["Tono", "Velocidad", "Idiomas", "Coste", "Medición", "Escalabilidad"],
        fill="toself",
        line=dict(color=AC, width=3),
        fillcolor="rgba(124,58,237,.16)",
        hovertemplate="<b>%{theta}</b><br>%{r}/100<extra></extra>",
    ))
    fig_quality.update_layout(
        polar=dict(
            bgcolor="rgba(248,248,246,1)",
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=9, color="#9CA3AF"), gridcolor="#E5E5E5"),
            angularaxis=dict(tickfont=dict(size=11, color="#374151"), gridcolor="#E5E5E5"),
        ),
        paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=20, b=20, l=30, r=30), height=300,
        title=dict(text="MADUREZ OBJETIVO DEL SISTEMA", font=dict(size=11, color="#374151"), x=0.02),
    )
    st.plotly_chart(fig_quality, use_container_width=True)


# =============================================================================
# SECTION 06 — ROADMAP, BENEFICIOS Y RIESGOS
# =============================================================================
st.markdown('<div class="sec-hdr"><span class="sec-num">06</span><h2 class="sec-ttl">ROADMAP CEO · BENEFICIOS, RIESGOS Y DECISIÓN</h2><div class="sec-line"></div></div>', unsafe_allow_html=True)

tab_road, tab_benefits, tab_risks = st.tabs(["Roadmap 30-60-90", "Beneficios para Scuffers", "Riesgos y control"])

with tab_road:
    roadmap = [
        ("0-30 días", "MVP usable", "Brand book, generador de emails/captions/newsletter, traducción de marca, guardado de outputs y coste por uso.", "Demo interna con 3 campañas reales y aprobación del equipo."),
        ("31-60 días", "Conexiones", "n8n con Klaviyo/Shopify/Drive, biblioteca de campañas, prompts versionados y reporting básico en Grafana.", "El equipo usa Studio en drops reales sin depender de agencia para primera versión."),
        ("61-90 días", "Sistema operativo de contenido", "A/B testing, scoring de tono, reutilización de aprendizajes, calendario editorial y traducción multi-mercado.", "Studio se convierte en la capa de producción y aprendizaje de marketing."),
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

with tab_benefits:
    benefit_cols = st.columns(3)
    for col, (title, points, metric) in zip(benefit_cols, [
        ("Marca", ["Tono consistente en todos los canales", "Menos dependencia de personas concretas", "Más velocidad sin perder criterio creativo"], "100% piezas con brand context"),
        ("Equipo", ["Menos bloqueos por página en blanco", "Más tiempo para estrategia y cultura", "Aprendizaje acumulado campaña a campaña"], "6-10h/sem recuperadas"),
        ("Negocio", ["Más campañas por mes", "Internacionalización más barata", "Testing de asuntos, hooks y copies antes de publicar"], "−60/80% coste de copy"),
    ]):
        with col:
            st.markdown(
                f'<div style="background:{AC_L};border:1px solid {AC_B};border-radius:12px;padding:18px;height:100%;">'
                f'<div style="font-family:\'Syne\',sans-serif;font-weight:800;color:#0D0D0D;margin-bottom:10px;">{title}</div>'
                + "".join(f'<div style="font-size:.74rem;color:#374151;line-height:1.55;margin-bottom:7px;">{_icon("check",12,"#22C55E")} {p}</div>' for p in points)
                + f'<div style="margin-top:12px;border-top:1px solid {AC_B};padding-top:10px;font-size:.7rem;font-weight:800;color:{AC};">{metric}</div></div>',
                unsafe_allow_html=True,
            )

with tab_risks:
    risks = [
        ("Contenido genérico", "Si el brand book es pobre, la IA sonará como cualquier marca.", "Crear un Brand Brain con ejemplos reales aprobados, negativos y reglas de tono por canal."),
        ("Publicar sin revisión", "Riesgo reputacional por claims, precios, fechas o tono incorrecto.", "Human-in-the-loop obligatorio: borrador, aprobación, publicación y log de responsable."),
        ("Coste fuera de control", "Muchos usuarios generando variantes pueden subir el coste.", "Límites por rol, cache de contexto, modelo barato para tareas simples y dashboard de gasto."),
        ("Datos sensibles", "Briefs, campañas o colaboraciones no anunciadas deben protegerse.", "Entorno privado, permisos, logs y separación entre información pública y confidencial."),
    ]
    for title, risk, mitigation in risks:
        st.markdown(
            f'<div style="display:grid;grid-template-columns:180px 1fr 1fr;gap:12px;margin-bottom:10px;">'
            f'<div style="background:#111827;color:#fff;border-radius:10px;padding:12px;font-weight:800;font-size:.78rem;">{title}</div>'
            f'<div style="background:#FEF2F2;border:1px solid #FECACA;border-radius:10px;padding:12px;font-size:.72rem;color:#7F1D1D;line-height:1.45;"><strong>Riesgo:</strong> {risk}</div>'
            f'<div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:10px;padding:12px;font-size:.72rem;color:#14532D;line-height:1.45;"><strong>Control:</strong> {mitigation}</div></div>',
            unsafe_allow_html=True,
        )

_footer()
