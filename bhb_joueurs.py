import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="BHB – Fiches Joueurs", page_icon="🤾", layout="wide")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  /* Réduction marges globales Streamlit */
  .block-container { padding: 0.8rem 1.2rem 0.5rem !important; max-width: 1100px; }
  div[data-testid="stVerticalBlock"] > div { gap: 0.3rem !important; }

  .stat-card {
    background: #f0f4fa; border-left: 3px solid #1F4E79;
    border-radius: 8px; padding: 10px 14px 8px; margin-bottom: 8px;
  }
  .stat-card h3 {
    margin: 0 0 8px 0; font-size: 0.72rem; text-transform: uppercase;
    letter-spacing: 1px; color: #1F4E79; font-weight: 700;
  }
  .kpi-row { display: flex; gap: 8px; flex-wrap: wrap; }
  .kpi {
    background: white; border-radius: 6px; padding: 6px 12px;
    text-align: center; flex: 1; min-width: 70px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.07);
  }
  .kpi .val { font-size: 1.4rem; font-weight: 700; color: #1a2e4a; line-height: 1.1; }
  .kpi .lbl { font-size: 0.62rem; color: #777; text-transform: uppercase; letter-spacing: 0.4px; margin-top: 2px; }
  .kpi.green .val  { color: #1a7a3c; }
  .kpi.orange .val { color: #b85e00; }
  .kpi.red .val    { color: #c0392b; }

  .player-name { font-size: 1.35rem; font-weight: 700; color: #1a2e4a; line-height: 1.15; margin: 0; }
  .player-poste { font-size: 0.8rem; color: #1F4E79; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-top: 2px; }
  .player-num { font-size: 0.72rem; color: #999; text-transform: uppercase; letter-spacing: 1px; }

  .match-badge {
    display: inline-block; background: #e8f0fb; color: #1F4E79;
    border-radius: 5px; padding: 1px 8px; font-size: 0.72rem;
    font-weight: 600; margin-bottom: 6px;
  }
  hr.divider { border: none; border-top: 2px solid #1F4E79; margin: 8px 0 10px; }

  /* Réduire hauteur des selectbox et widgets */
  div[data-testid="stSelectbox"] { margin-bottom: 4px !important; }
  div[data-testid="stMultiSelect"] { margin-bottom: 4px !important; }
</style>
""", unsafe_allow_html=True)

GITHUB_RAW  = "https://raw.githubusercontent.com/madjerad/Statsjoueurs/main"
DATA_URL    = f"{GITHUB_RAW}/StatsJoueurs2526.xlsx"
PHOTOS_BASE = f"{GITHUB_RAW}/Photos"
GARDIENS    = {12, 16}
C = {"primary": "#1F4E79", "accent": "#4A90D9", "green": "#1a7a3c",
     "orange": "#d97706", "red": "#c0392b", "bg": "#f0f4fa"}

JOURNEE_ORDER = [f"J{i}" for i in range(1, 23)]

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
    xl = pd.ExcelFile(BytesIO(resp.content), engine='openpyxl')

    tb         = pd.read_excel(xl, sheet_name='Tirs & Buts par Match')
    disc       = pd.read_excel(xl, sheet_name='Discipline')
    arrets     = pd.read_excel(xl, sheet_name='Arrêts')
    ref_matchs = pd.read_excel(xl, sheet_name='RefMatchs')

    arrets['Numéro'] = arrets['Gardiens'].apply(
        lambda g: 16 if 'Mai' in str(g) else (12 if 'Stephan' in str(g) else None)
    )
    col_arr = [c for c in arrets.columns if 'Arr' in c
               and c not in ('Numéro', 'Gardiens', 'Match', 'Journée')]
    if col_arr:
        arrets.rename(columns={col_arr[0]: 'Arrêts'}, inplace=True)

    disc['Numéro'] = disc['Joueurs'].str.extract(r'^(\d+)').astype(float)
    return tb, disc, arrets, ref_matchs


tb, disc, arrets, ref_matchs = load_data()


def load_photo(num):
    try:
        r = requests.get(f"{PHOTOS_BASE}/{num}.jpg", timeout=5)
        if r.status_code == 200:
            return Image.open(BytesIO(r.content))
    except Exception:
        pass
    return None


def kpi(val, label, cls=""):
    return (f'<div class="kpi {cls}">'
            f'<div class="val">{val}</div>'
            f'<div class="lbl">{label}</div></div>')


def sort_by_journee(df):
    """Trie un df qui possède déjà une colonne Journée, sans merge."""
    df = df.copy()
    df['_j_order'] = df['Journée'].apply(
        lambda j: JOURNEE_ORDER.index(str(j)) if str(j) in JOURNEE_ORDER else 99
    )
    df = df.sort_values('_j_order').drop(columns='_j_order')
    df['label'] = df['Journée'].astype(str) + ' · ' + df['Match'].astype(str)
    return df


def chart_layout(fig, title, height=220, right=10):
    fig.update_layout(
        title=dict(text=title, font=dict(size=11)),
        plot_bgcolor='white', paper_bgcolor=C['bg'],
        height=height, margin=dict(t=32, b=4, l=4, r=right),
        font=dict(family='Inter', size=10),
        legend=dict(orientation='h', y=1.18, font=dict(size=9)),
    )
    fig.update_yaxes(gridcolor='#e5e9f0')
    fig.update_xaxes(tickfont=dict(size=8))


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("#### 🤾 BHB – Fiches Joueurs")
    joueurs_tri = REF_JOUEURS.sort_values('Nom')
    options = joueurs_tri.apply(
        lambda r: f"{r['Numéro']} – {r['Prénom']} {r['Nom']}", axis=1
    ).tolist()
    sel     = st.selectbox("Joueur", options, label_visibility="collapsed")
    num_sel = int(sel.split("–")[0].strip())

    st.markdown("**Filtres**")
    phases = ['Toutes'] + sorted(ref_matchs['Phase'].dropna().unique())
    lieux  = ['Tous']   + sorted(ref_matchs['Lieu'].dropna().unique())
    filtre_phase = st.selectbox("Phase", phases)
    filtre_lieu  = st.selectbox("Lieu",  lieux)

    rm = ref_matchs.copy()
    if filtre_phase != 'Toutes': rm = rm[rm['Phase'] == filtre_phase]
    if filtre_lieu  != 'Tous':   rm = rm[rm['Lieu']  == filtre_lieu]

    matchs_dispo  = sorted(rm['Match'].unique())
    sel_matchs    = st.multiselect("Matchs", matchs_dispo, placeholder="Tous les matchs")
    matchs_actifs = sel_matchs if sel_matchs else matchs_dispo

# ── Données filtrées ──────────────────────────────────────────────────────────
tb_f     = tb[tb['Match'].isin(matchs_actifs)         & (tb['Numéro']     == num_sel)]
disc_f   = disc[disc['Match'].isin(matchs_actifs)     & (disc['Numéro']   == num_sel)]
arrets_f = arrets[arrets['Match'].isin(matchs_actifs) & (arrets['Numéro'] == num_sel)]
matchs_joues = arrets_f['Match'].nunique() if num_sel in GARDIENS else disc_f['Match'].nunique()

# ── Header : photo + infos + général (une ligne) ──────────────────────────────
jinfo = REF_JOUEURS[REF_JOUEURS['Numéro'] == num_sel].iloc[0]
photo = load_photo(num_sel)

col_ph, col_info, col_gen = st.columns([1, 2.5, 4])

with col_ph:
    if photo:
        st.image(photo, width=90)
    else:
        st.markdown('<div style="width:80px;height:80px;border-radius:50%;background:#2d5a8e;'
                    'display:flex;align-items:center;justify-content:center;font-size:1.8rem;'
                    'border:2px solid #4A90D9">👤</div>', unsafe_allow_html=True)

with col_info:
    st.markdown(f"""
    <div style="padding-top:6px">
      <div class="player-num">N° {jinfo['Numéro']}</div>
      <div class="player-name">{jinfo['Prénom']} {jinfo['Nom']}</div>
      <div class="player-poste">{jinfo['Poste']}</div>
    </div>""", unsafe_allow_html=True)

with col_gen:
    filtre_txt = []
    if filtre_phase != 'Toutes': filtre_txt.append(filtre_phase)
    if filtre_lieu  != 'Tous':   filtre_txt.append(filtre_lieu)
    if sel_matchs:               filtre_txt.append(f"{len(sel_matchs)} match(s)")
    badge = f'<span class="match-badge">🔎 {" · ".join(filtre_txt)}</span>' if filtre_txt else ""
    st.markdown(f"""
    <div style="padding-top:14px">
      {badge}
      <div class="stat-card" style="margin-top:4px">
        <h3>📅 Général</h3>
        <div class="kpi-row">{kpi(matchs_joues, "Matchs joués")}</div>
      </div>
    </div>""", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# GARDIENS
# ══════════════════════════════════════════════════════════
if num_sel in GARDIENS:
    total_arrets = int(arrets_f['Arrêts'].sum()) if not arrets_f.empty else 0
    moy_arrets   = round(arrets_f['Arrêts'].mean(), 1) if matchs_joues > 0 else 0

    st.markdown(f"""
    <div class="stat-card">
      <h3>🧤 Arrêts</h3>
      <div class="kpi-row">
        {kpi(total_arrets, "Total arrêts", "green")}
        {kpi(moy_arrets,   "Moy / match")}
      </div>
    </div>""", unsafe_allow_html=True)

    if not arrets_f.empty:
        df_plot = sort_by_journee(arrets_f)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_plot['label'], y=df_plot['Arrêts'],
            marker_color=C['accent'],
            text=df_plot['Arrêts'].astype(int), textposition='outside',
            textfont=dict(size=9),
            hovertemplate='%{x}<br>Arrêts : %{y}<extra></extra>',
        ))
        fig.add_hline(y=moy_arrets, line_dash='dot', line_color=C['orange'],
                      annotation_text=f"Moy {moy_arrets}",
                      annotation_position="top left",
                      annotation_font_size=9)
        chart_layout(fig, "Arrêts par match", height=230)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════
# JOUEURS DE CHAMP  —  2 colonnes côte à côte
# ══════════════════════════════════════════════════════════
else:
    total_2mn   = int(disc_f['2mn'].fillna(0).sum()) if not disc_f.empty else 0
    total_rouge = int(disc_f['Dis'].fillna(0).sum()) if not disc_f.empty else 0
    total_tirs  = int(tb_f['Tirs'].sum())
    total_buts  = int(tb_f['Buts'].sum())
    eff_pct     = round(total_buts / total_tirs * 100, 1) if total_tirs > 0 else 0
    efficacite  = f"{eff_pct}%" if total_tirs > 0 else "—"
    moy_buts    = round(total_buts / matchs_joues, 1) if matchs_joues > 0 else 0

    col_d, col_a = st.columns(2)

    # ── Colonne Discipline ────────────────────────────────
    with col_d:
        st.markdown(f"""
        <div class="stat-card">
          <h3>🟨 Discipline</h3>
          <div class="kpi-row">
            {kpi(total_2mn,   "Excl. 2 mn", "orange")}
            {kpi(total_rouge, "Cartons rouges", "red")}
          </div>
        </div>""", unsafe_allow_html=True)

        if not disc_f.empty and (total_2mn > 0 or total_rouge > 0):
            df_disc = sort_by_journee(disc_f)
            df_disc['2mn'] = df_disc['2mn'].fillna(0).astype(int)
            df_disc['Dis'] = df_disc['Dis'].fillna(0).astype(int)
            df_agg = df_disc.groupby('label', sort=False).agg(
                excl=('2mn', 'sum'), rouge=('Dis', 'sum')
            ).reset_index()

            fig_d = go.Figure()
            fig_d.add_trace(go.Bar(
                name='2 mn', x=df_agg['label'], y=df_agg['excl'],
                marker_color=C['orange'],
                text=df_agg['excl'], textposition='outside', textfont=dict(size=9),
                hovertemplate='%{x}<br>2mn : %{y}<extra></extra>',
            ))
            if df_agg['rouge'].sum() > 0:
                fig_d.add_trace(go.Bar(
                    name='Rouge', x=df_agg['label'], y=df_agg['rouge'],
                    marker_color=C['red'],
                    text=df_agg['rouge'], textposition='outside', textfont=dict(size=9),
                    hovertemplate='%{x}<br>Rouge : %{y}<extra></extra>',
                ))
            chart_layout(fig_d, "Discipline par match", height=230)
            fig_d.update_layout(barmode='stack')
            fig_d.update_yaxes(dtick=1)
            st.plotly_chart(fig_d, use_container_width=True)
        else:
            st.markdown('<div style="color:#aaa;font-size:0.8rem;padding:8px">Aucune sanction sur cette sélection.</div>',
                        unsafe_allow_html=True)

    # ── Colonne Attaque ───────────────────────────────────
    with col_a:
        st.markdown(f"""
        <div class="stat-card">
          <h3>🎯 Attaque</h3>
          <div class="kpi-row">
            {kpi(total_tirs,  "Tirs")}
            {kpi(total_buts,  "Buts",     "green")}
            {kpi(efficacite,  "Efficacité","green")}
            {kpi(moy_buts,    "Buts/match")}
          </div>
        </div>""", unsafe_allow_html=True)

        if not tb_f.empty:
            df_tb = sort_by_journee(tb_f)
            df_tb['Manqués'] = df_tb['Tirs'] - df_tb['Buts']
            df_tb['Eff%']    = (df_tb['Buts'] / df_tb['Tirs'] * 100).round(1)

            fig_att = go.Figure()
            fig_att.add_trace(go.Bar(
                name='Buts', x=df_tb['label'], y=df_tb['Buts'],
                marker_color=C['green'],
                text=df_tb['Buts'], textposition='inside',
                textfont=dict(color='white', size=9),
                hovertemplate='%{x}<br>Buts : %{y}<extra></extra>',
            ))
            fig_att.add_trace(go.Bar(
                name='Manqués', x=df_tb['label'], y=df_tb['Manqués'],
                marker_color='#c8d8e8',
                hovertemplate='%{x}<br>Manqués : %{y}<extra></extra>',
            ))
            fig_att.add_trace(go.Scatter(
                name='Eff %', x=df_tb['label'], y=df_tb['Eff%'],
                mode='lines+markers',
                line=dict(color=C['orange'], width=1.5),
                marker=dict(size=4), yaxis='y2',
                hovertemplate='%{x}<br>Eff : %{y}%<extra></extra>',
            ))
            chart_layout(fig_att, "Tirs & Buts par match", height=230, right=40)
            fig_att.update_layout(
                barmode='stack',
                yaxis=dict(title=None, gridcolor='#e5e9f0'),
                yaxis2=dict(overlaying='y', side='right', range=[0, 115],
                            showgrid=False, ticksuffix='%', tickfont=dict(size=8)),
            )
            st.plotly_chart(fig_att, use_container_width=True)

    # ── Gauge pleine largeur ──────────────────────────────
    if not tb_f.empty:
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number",
            value=eff_pct,
            number={'suffix': '%', 'font': {'size': 24, 'color': C['primary']}},
            title={'text': "Efficacité globale au tir", 'font': {'size': 11}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1},
                'bar': {'color': C['green']},
                'bgcolor': 'white',
                'steps': [
                    {'range': [0,  40], 'color': '#fde8e8'},
                    {'range': [40, 60], 'color': '#fef3d0'},
                    {'range': [60,100], 'color': '#d4edda'},
                ],
                'threshold': {'line': {'color': C['primary'], 'width': 3},
                              'thickness': 0.75, 'value': eff_pct},
            }
        ))
        fig_g.update_layout(
            height=160, margin=dict(t=20, b=4, l=60, r=60),
            paper_bgcolor=C['bg'], font=dict(family='Inter'),
        )
        st.plotly_chart(fig_g, use_container_width=True)

st.markdown("<div style='text-align:center;color:#ccc;font-size:0.68rem;margin-top:4px'>"
            "BHB Analytics · Saison 2025–2026</div>", unsafe_allow_html=True)
