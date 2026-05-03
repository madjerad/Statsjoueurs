import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from io import BytesIO
from PIL import Image

st.set_page_config(
    page_title="BHB – Fiches Joueurs",
    page_icon="🤾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Charte couleur BHB ────────────────────────────────────────────────────────
# Bleu marine foncé / bleu roi / rouge club / blanc
C = {
    "navy":    "#1a2744",   # bleu marine BHB (fond)
    "blue":    "#1e4d9b",   # bleu roi BHB
    "blue2":   "#2d65c4",   # bleu clair accentuation
    "red":     "#c0272d",   # rouge BHB
    "white":   "#ffffff",
    "offwhite":"#f4f6fb",
    "gray":    "#e8ecf4",
    "text":    "#1a2744",
    "muted":   "#6b7a99",
    "green":   "#1a7a3c",
    "orange":  "#d97706",
}

# ── CSS global ────────────────────────────────────────────────────────────────
st.markdown(f"""
<meta name="color-scheme" content="light only">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

  /* Force mode clair sur tous supports */
  :root {{ color-scheme: light only !important; }}
  html, body, [data-testid="stApp"], [class*="css"] {{
    font-family: 'Inter', sans-serif !important;
    background-color: {C['offwhite']} !important;
    color: {C['text']} !important;
  }}

  /* Sidebar */
  section[data-testid="stSidebar"] {{
    background: {C['navy']} !important;
    min-width: 220px !important;
    max-width: 220px !important;
  }}
  section[data-testid="stSidebar"] * {{ color: {C['white']} !important; }}
  section[data-testid="stSidebar"] .stSelectbox > div > div,
  section[data-testid="stSidebar"] .stMultiSelect > div > div {{
    background: rgba(255,255,255,0.12) !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    color: {C['white']} !important;
  }}
  section[data-testid="stSidebar"] label {{ color: rgba(255,255,255,0.75) !important; font-size:0.78rem !important; }}
  section[data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,0.15) !important; }}

  /* Padding page */
  .block-container {{ padding: 0.6rem 1rem 0.4rem !important; }}

  /* Cartes stats */
  .stat-card {{
    background: {C['white']};
    border-left: 3px solid {C['blue']};
    border-radius: 8px;
    padding: 8px 12px 7px;
    margin-bottom: 7px;
    box-shadow: 0 1px 4px rgba(26,39,68,0.07);
  }}
  .stat-card h3 {{
    margin: 0 0 7px 0; font-size: 0.7rem; text-transform: uppercase;
    letter-spacing: 1px; color: {C['blue']}; font-weight: 700;
  }}
  .kpi-row {{ display: flex; gap: 6px; flex-wrap: wrap; }}
  .kpi {{
    background: {C['offwhite']}; border-radius: 6px; padding: 5px 8px;
    text-align: center; flex: 1; min-width: 60px;
  }}
  .kpi .val {{ font-size: 1.3rem; font-weight: 800; color: {C['navy']}; line-height: 1.1; }}
  .kpi .lbl {{ font-size: 0.6rem; color: {C['muted']}; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 1px; }}
  .kpi.green .val  {{ color: {C['green']}; }}
  .kpi.orange .val {{ color: {C['orange']}; }}
  .kpi.red .val    {{ color: {C['red']}; }}
  .kpi.blue .val   {{ color: {C['blue']}; }}

  /* Badge filtre */
  .filter-badge {{
    display:inline-block; background:{C['blue2']}22; color:{C['blue']};
    border:1px solid {C['blue2']}55; border-radius:5px; padding:2px 8px;
    font-size:0.7rem; font-weight:600; margin-bottom:6px;
  }}

  /* Header joueur */
  .player-header {{
    background: linear-gradient(120deg, {C['navy']} 0%, {C['blue']} 100%);
    border-radius: 10px; padding: 10px 14px;
    display: flex; align-items: center; gap: 14px;
    margin-bottom: 10px;
  }}
  .player-header img {{
    border-radius: 8px;
    border: 2px solid rgba(255,255,255,0.4);
    object-fit: cover;
    /* Haute résolution : on affiche à 90px mais charge en haute def */
    width: 90px; height: 108px;
    image-rendering: -webkit-optimize-contrast;
    image-rendering: crisp-edges;
  }}
  .player-no-photo {{
    width:90px; height:108px; border-radius:8px;
    background: rgba(255,255,255,0.15);
    display:flex; align-items:center; justify-content:center;
    font-size:2.5rem; border:2px solid rgba(255,255,255,0.3);
    flex-shrink:0;
  }}
  .player-info {{ flex:1; min-width:0; }}
  .player-info .numero {{ font-size:0.72rem; color:rgba(255,255,255,0.6); text-transform:uppercase; letter-spacing:1px; }}
  .player-info .nom {{ font-size:1.35rem; font-weight:800; color:#fff; line-height:1.15; word-break:break-word; }}
  .player-info .poste {{
    display:inline-block; margin-top:4px;
    background: {C['red']}; color:#fff;
    font-size:0.65rem; font-weight:700; letter-spacing:1px;
    text-transform:uppercase; border-radius:4px; padding:2px 7px;
  }}

  /* Désactiver zoom plotly sur mobile */
  .js-plotly-plot .plotly {{ touch-action: pan-y !important; }}
  .plotly-graph-div {{ touch-action: pan-y !important; }}

  /* Responsive mobile */
  @media (max-width: 768px) {{
    .block-container {{ padding: 0.4rem 0.5rem !important; }}
    .player-header {{ padding: 8px 10px; gap:10px; }}
    .player-header img {{ width:70px; height:84px; }}
    .player-info .nom {{ font-size:1.1rem; }}
    .kpi .val {{ font-size:1.1rem; }}
    section[data-testid="stSidebar"] {{ min-width:200px !important; max-width:200px !important; }}
  }}
</style>
""", unsafe_allow_html=True)

# ── Config ────────────────────────────────────────────────────────────────────
GITHUB_RAW  = "https://raw.githubusercontent.com/madjerad/Statsjoueurs/main"
DATA_URL    = f"{GITHUB_RAW}/StatsJoueurs2526.xlsx"
PHOTOS_BASE = f"{GITHUB_RAW}/Photos"
LOGO_URL    = f"{GITHUB_RAW}/logo.png"
GARDIENS    = {12, 16}

JOURNEE_ORDER = [f"J{i}" for i in range(1, 30)]

REF_JOUEURS = pd.DataFrame({
    'Numéro': [2,3,4,5,7,8,9,10,12,13,15,16,19,21,24,25,33,92],
    'Nom':    ['NAUDIN','NAUDIN','HERMAND','BON','PLISSONNIER','PANIC','MINANA',
               'GREGULSKI','STEPHAN','THELCIDE','COSNIER','MAI','GOSTOMSKI',
               'CHAZALON','MINY','FAVERIN','NAUDIN','PHAROSE'],
    'Prénom': ['Paul','Théo','Mathieu','Gabriel','Jean','Milan','Lilian','Vincent',
               'Corentin','Axel','Lubin','François','Sasha','Marius','Gabin',
               'Léan','Hugo','Kylian'],
    'Poste':  ['DEMI-CENTRE','AILIER','PIVOT','ARRIERE','AILIER','ARRIERE','ARRIERE',
               'ARRIERE','GARDIEN','ARRIERE','DEMI-CENTRE','GARDIEN','PIVOT',
               'ARRIERE','PIVOT','AILIER','ARRIERE','AILIER'],
})


@st.cache_data(ttl=0)
def load_data():
    resp = requests.get(DATA_URL, timeout=20)
    resp.raise_for_status()
    buf = BytesIO(resp.content)
    xl  = pd.ExcelFile(buf, engine='openpyxl')

    tb         = pd.read_excel(xl, sheet_name='Tirs & Buts par Match')
    disc       = pd.read_excel(xl, sheet_name='Discipline')
    arrets     = pd.read_excel(xl, sheet_name='Arrêts')
    ref_matchs = pd.read_excel(xl, sheet_name='RefMatchs')

    arrets['Numéro'] = arrets['Gardiens'].apply(
        lambda g: 16 if 'Mai' in str(g) else (12 if 'Stephan' in str(g) else None)
    )
    col_arr = [c for c in arrets.columns
               if 'Arr' in c and c not in ('Numéro', 'Gardiens', 'Match', 'Journée')]
    if col_arr:
        arrets.rename(columns={col_arr[0]: 'Arrêts'}, inplace=True)

    disc['Numéro'] = disc['Joueurs'].str.extract(r'^(\d+)').astype(float)

    # Rang chronologique (toutes les feuilles ont déjà la colonne Journée)
    for df in (tb, disc, arrets):
        df['_ordre'] = pd.Categorical(df['Journée'], categories=JOURNEE_ORDER, ordered=True)

    return tb, disc, arrets, ref_matchs


@st.cache_data(ttl=3600)
def load_logo():
    try:
        r = requests.get(LOGO_URL, timeout=5)
        if r.status_code == 200:
            return r.content
    except Exception:
        pass
    return None


@st.cache_data(ttl=3600)
def load_photo(num):
    """Charge en haute résolution — l'affichage est réduit côté CSS."""
    try:
        r = requests.get(f"{PHOTOS_BASE}/{num}.jpg", timeout=6)
        if r.status_code == 200:
            img = Image.open(BytesIO(r.content))
            # Resize à max 600px (haute def pour les écrans Retina)
            max_dim = 600
            w, h = img.size
            if max(w, h) > max_dim:
                ratio = max_dim / max(w, h)
                img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
            buf = BytesIO()
            img.save(buf, format='JPEG', quality=92)
            buf.seek(0)
            return buf.read()
    except Exception:
        pass
    return None


tb, disc, arrets, ref_matchs = load_data()


def kpi(val, label, cls=""):
    return (f'<div class="kpi {cls}">'
            f'<div class="val">{val}</div>'
            f'<div class="lbl">{label}</div></div>')


def safe_int_series(s):
    """Convertit en int en remplaçant NaN par 0 — évite IntCastingNaNError."""
    return s.fillna(0).astype(int)


def make_label(df):
    """Tri chronologique. Journée est déjà dans df — pas de merge nécessaire."""
    df = df.sort_values('_ordre')
    df['label'] = df['Journée'].astype(str) + '<br>' + df['Match']
    return df


def plotly_cfg(height=210, r=8):
    """Config layout commune + désactivation zoom/pan."""
    return dict(
        plot_bgcolor=C['white'], paper_bgcolor=C['offwhite'],
        height=height, margin=dict(t=32, b=4, l=4, r=r),
        font=dict(family='Inter', size=10, color=C['text']),
        legend=dict(orientation='h', y=1.16, font_size=9),
        xaxis=dict(tickfont_size=8, fixedrange=True),   # désactive zoom X
        yaxis=dict(fixedrange=True),                    # désactive zoom Y
        dragmode=False,
    )


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    logo_bytes = load_logo()
    if logo_bytes:
        st.markdown(
            f'<div style="text-align:center;padding:12px 0 4px">'
            f'<img src="data:image/png;base64,{__import__("base64").b64encode(logo_bytes).decode()}"'
            f' style="max-width:110px;max-height:110px;object-fit:contain"></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div style="text-align:center;padding:14px 0 6px;font-size:1.1rem;'
            f'font-weight:800;color:#fff;letter-spacing:2px">BHB</div>',
            unsafe_allow_html=True,
        )

    st.markdown(f'<div style="text-align:center;color:rgba(255,255,255,0.5);'
                f'font-size:0.65rem;margin-bottom:10px">Saison 2025–2026</div>',
                unsafe_allow_html=True)
    st.markdown("---")

    joueurs_tri = REF_JOUEURS.sort_values('Nom')
    options = joueurs_tri.apply(
        lambda r: f"{r['Numéro']} – {r['Prénom']} {r['Nom']}", axis=1
    ).tolist()
    sel     = st.selectbox("Joueur", options, label_visibility="collapsed")
    num_sel = int(sel.split("–")[0].strip())

    st.markdown("---")
    phases = ['Toutes'] + sorted(ref_matchs['Phase'].dropna().unique())
    lieux  = ['Tous']   + sorted(ref_matchs['Lieu'].dropna().unique())
    filtre_phase = st.selectbox("Phase", phases)
    filtre_lieu  = st.selectbox("Lieu",  lieux)

    rm = ref_matchs.copy()
    if filtre_phase != 'Toutes': rm = rm[rm['Phase'] == filtre_phase]
    if filtre_lieu  != 'Tous':   rm = rm[rm['Lieu']  == filtre_lieu]

    matchs_dispo  = sorted(rm['Match'].unique())
    sel_matchs    = st.multiselect("Matchs", matchs_dispo, placeholder="Tous")
    matchs_actifs = sel_matchs if sel_matchs else matchs_dispo

# ── Données filtrées ──────────────────────────────────────────────────────────
tb_f     = tb[tb['Match'].isin(matchs_actifs)         & (tb['Numéro']   == num_sel)]
disc_f   = disc[disc['Match'].isin(matchs_actifs)     & (disc['Numéro'] == num_sel)]
arrets_f = arrets[arrets['Match'].isin(matchs_actifs) & (arrets['Numéro'] == num_sel)]

matchs_joues = arrets_f['Match'].nunique() if num_sel in GARDIENS else disc_f['Match'].nunique()

# ── Header joueur ─────────────────────────────────────────────────────────────
jinfo      = REF_JOUEURS[REF_JOUEURS['Numéro'] == num_sel].iloc[0]
photo_data = load_photo(num_sel)

if photo_data:
    import base64
    photo_b64  = base64.b64encode(photo_data).decode()
    photo_html = (f'<img src="data:image/jpeg;base64,{photo_b64}" '
                  f'alt="{jinfo["Prénom"]} {jinfo["Nom"]}">')
else:
    photo_html = '<div class="player-no-photo">👤</div>'

# Badge filtres
filtre_txt = []
if filtre_phase != 'Toutes': filtre_txt.append(filtre_phase)
if filtre_lieu  != 'Tous':   filtre_txt.append(filtre_lieu)
if sel_matchs:               filtre_txt.append(f"{len(sel_matchs)} matchs")
badge = (f'<span class="filter-badge">🔎 {" · ".join(filtre_txt)}</span><br>'
         if filtre_txt else "")

st.markdown(f"""
{badge}
<div class="player-header">
  {photo_html}
  <div class="player-info">
    <div class="numero">#{jinfo['Numéro']}</div>
    <div class="nom">{jinfo['Prénom']}<br>{jinfo['Nom']}</div>
    <div class="poste">{jinfo['Poste']}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Layout : KPI gauche | graphiques droite ───────────────────────────────────
col_kpi, col_charts = st.columns([1, 2.8])

with col_kpi:
    st.markdown(f"""
    <div class="stat-card">
      <h3>📅 Général</h3>
      <div class="kpi-row">{kpi(matchs_joues, "Matchs joués", "blue")}</div>
    </div>""", unsafe_allow_html=True)

    # ── GARDIENS ──────────────────────────────────────────────────────────────
    if num_sel in GARDIENS:
        # FIX : fillna avant sum/mean pour éviter IntCastingNaNError
        arrets_clean = arrets_f['Arrêts'].fillna(0)
        total_arrets = int(arrets_clean.sum())
        moy_arrets   = round(float(arrets_clean.mean()), 1) if matchs_joues > 0 else 0.0
        st.markdown(f"""
        <div class="stat-card">
          <h3>🧤 Arrêts</h3>
          <div class="kpi-row">
            {kpi(total_arrets, "Total",     "green")}
            {kpi(moy_arrets,   "Moy/match")}
          </div>
        </div>""", unsafe_allow_html=True)

    # ── JOUEURS DE CHAMP ──────────────────────────────────────────────────────
    else:
        total_2mn   = int(disc_f['2mn'].fillna(0).sum())
        total_rouge = int(disc_f['Dis'].fillna(0).sum())
        st.markdown(f"""
        <div class="stat-card">
          <h3>🟨 Discipline</h3>
          <div class="kpi-row">
            {kpi(total_2mn,   "Excl. 2mn", "orange")}
            {kpi(total_rouge, "Rouges",     "red")}
          </div>
        </div>""", unsafe_allow_html=True)

        total_tirs = int(tb_f['Tirs'].fillna(0).sum())
        total_buts = int(tb_f['Buts'].fillna(0).sum())
        eff_pct    = round(total_buts / total_tirs * 100, 1) if total_tirs > 0 else 0.0
        efficacite = f"{eff_pct}%" if total_tirs > 0 else "—"
        moy_buts   = round(total_buts / matchs_joues, 1) if matchs_joues > 0 else 0.0
        st.markdown(f"""
        <div class="stat-card">
          <h3>🎯 Attaque</h3>
          <div class="kpi-row">
            {kpi(total_tirs,  "Tirs")}
            {kpi(total_buts,  "Buts",   "green")}
            {kpi(efficacite,  "Eff. %", "green")}
            {kpi(moy_buts,    "Buts/M")}
          </div>
        </div>""", unsafe_allow_html=True)

# ── Graphiques ────────────────────────────────────────────────────────────────
with col_charts:

    # ── GARDIENS ──────────────────────────────────────────────────────────────
    if num_sel in GARDIENS:
        if not arrets_f.empty:
            df_plot = make_label(arrets_f.copy())
            df_plot['Arrêts'] = df_plot['Arrêts'].fillna(0)   # FIX NaN
            moy_v = round(float(df_plot['Arrêts'].mean()), 1)

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_plot['label'],
                y=df_plot['Arrêts'],
                marker_color=C['blue2'],
                text=safe_int_series(df_plot['Arrêts']),
                textposition='outside', textfont_size=9,
                hovertemplate='%{x}<br>Arrêts : %{y}<extra></extra>',
            ))
            fig.add_hline(y=moy_v, line_dash='dot', line_color=C['orange'],
                          annotation_text=f"Moy {moy_v}",
                          annotation_font_size=9, annotation_position="top left")
            fig.update_layout(
                title=dict(text="Arrêts par match", font_size=11),
                showlegend=False,
                yaxis=dict(fixedrange=True, gridcolor=C['gray'], title=None),
                **plotly_cfg(height=430),
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # ── JOUEURS DE CHAMP ──────────────────────────────────────────────────────
    else:
        # Graphique Tirs & Buts
        if not tb_f.empty:
            df_tb = make_label(tb_f.copy())
            df_tb['Tirs']    = df_tb['Tirs'].fillna(0)
            df_tb['Buts']    = df_tb['Buts'].fillna(0)
            df_tb['Manqués'] = df_tb['Tirs'] - df_tb['Buts']
            df_tb['Eff%']    = (df_tb['Buts'] / df_tb['Tirs'].replace(0, float('nan')) * 100).round(1)

            fig_att = go.Figure()
            fig_att.add_trace(go.Bar(
                name='Buts', x=df_tb['label'], y=df_tb['Buts'],
                marker_color=C['green'],
                text=safe_int_series(df_tb['Buts']),
                textposition='inside', textfont_color='white', textfont_size=9,
                hovertemplate='%{x}<br>Buts : %{y}<extra></extra>',
            ))
            fig_att.add_trace(go.Bar(
                name='Manqués', x=df_tb['label'], y=df_tb['Manqués'],
                marker_color=C['gray'],
                hovertemplate='%{x}<br>Manqués : %{y}<extra></extra>',
            ))
            fig_att.add_trace(go.Scatter(
                name='Eff. %', x=df_tb['label'], y=df_tb['Eff%'],
                mode='lines+markers', line=dict(color=C['orange'], width=2),
                marker=dict(size=5), yaxis='y2',
                hovertemplate='%{x}<br>Efficacité : %{y}%<extra></extra>',
            ))
            cfg_att = plotly_cfg(height=235, r=42)
            cfg_att['yaxis2'] = dict(
                title=None, overlaying='y', side='right',
                range=[0, 115], showgrid=False, ticksuffix='%',
                tickfont_size=8, fixedrange=True,
            )
            fig_att.update_layout(
                title=dict(text="🎯 Tirs & Buts par match", font_size=11),
                barmode='stack',
                yaxis=dict(fixedrange=True, gridcolor=C['gray'], title=None),
                **cfg_att,
            )
            st.plotly_chart(fig_att, use_container_width=True, config={'displayModeBar': False})

        # Ligne basse : gauge + discipline
        cg, cd = st.columns([1, 1.4])

        with cg:
            eff_val = eff_pct if total_tirs > 0 else 0.0
            fig_g = go.Figure(go.Indicator(
                mode="gauge+number",
                value=eff_val,
                number={'suffix': '%', 'font': {'size': 22, 'color': C['navy']}},
                title={'text': "Efficacité tir", 'font': {'size': 10}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickfont': {'size': 8}},
                    'bar': {'color': C['blue']},
                    'bgcolor': C['white'],
                    'steps': [
                        {'range': [0,  40], 'color': '#fde8e8'},
                        {'range': [40, 60], 'color': '#fef3d0'},
                        {'range': [60,100], 'color': '#d4edda'},
                    ],
                    'threshold': {'line': {'color': C['red'], 'width': 3},
                                  'thickness': 0.75, 'value': eff_val},
                }
            ))
            fig_g.update_layout(
                height=185, margin=dict(t=22, b=4, l=14, r=14),
                paper_bgcolor=C['offwhite'], font=dict(family='Inter'),
            )
            st.plotly_chart(fig_g, use_container_width=True, config={'displayModeBar': False})

        with cd:
            if not disc_f.empty and (total_2mn > 0 or total_rouge > 0):
                df_disc = make_label(disc_f.copy())
                df_disc['2mn'] = df_disc['2mn'].fillna(0).astype(int)
                df_disc['Dis'] = df_disc['Dis'].fillna(0).astype(int)
                df_agg = df_disc.groupby('label', sort=False).agg(
                    excl=('2mn', 'sum'), rouge=('Dis', 'sum')
                ).reset_index()

                fig_d = go.Figure()
                fig_d.add_trace(go.Bar(
                    name='2 mn', x=df_agg['label'], y=df_agg['excl'],
                    marker_color=C['orange'],
                    text=df_agg['excl'], textposition='outside', textfont_size=8,
                ))
                if df_agg['rouge'].sum() > 0:
                    fig_d.add_trace(go.Bar(
                        name='Rouge', x=df_agg['label'], y=df_agg['rouge'],
                        marker_color=C['red'],
                        text=df_agg['rouge'], textposition='outside', textfont_size=8,
                    ))
                fig_d.update_layout(
                    title=dict(text="🟨 Discipline par match", font_size=11),
                    barmode='stack',
                    yaxis=dict(fixedrange=True, gridcolor=C['gray'], dtick=1, title=None),
                    **plotly_cfg(height=185),
                )
                st.plotly_chart(fig_d, use_container_width=True, config={'displayModeBar': False})
            else:
                st.markdown(
                    f'<div style="height:185px;display:flex;align-items:center;'
                    f'justify-content:center;color:{C["muted"]};font-size:0.8rem;'
                    f'background:{C["white"]};border-radius:8px;margin-top:4px">'
                    f'Aucune sanction</div>',
                    unsafe_allow_html=True,
                )

st.markdown(
    f'<div style="text-align:center;color:{C["muted"]};font-size:0.65rem;margin-top:4px">'
    f'BHB Analytics · Saison 2025–2026</div>',
    unsafe_allow_html=True,
)
