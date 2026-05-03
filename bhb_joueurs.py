import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="BHB – Fiches Joueurs", page_icon="🤾", layout="centered")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  .stat-card {
    background: #f0f4fa; border-left: 4px solid #1F4E79;
    border-radius: 10px; padding: 16px 20px 10px; margin-bottom: 18px;
  }
  .stat-card h3 {
    margin: 0 0 14px 0; font-size: 0.82rem; text-transform: uppercase;
    letter-spacing: 1px; color: #1F4E79; font-weight: 700;
  }
  .kpi-row { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 4px; }
  .kpi {
    background: white; border-radius: 8px; padding: 10px 16px;
    text-align: center; flex: 1; min-width: 80px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  }
  .kpi .val { font-size: 1.75rem; font-weight: 700; color: #1a2e4a; line-height: 1.1; }
  .kpi .lbl { font-size: 0.7rem; color: #666; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 3px; }
  .kpi.green .val  { color: #1a7a3c; }
  .kpi.orange .val { color: #b85e00; }
  .kpi.red .val    { color: #c0392b; }
  .match-badge {
    display: inline-block; background: #e8f0fb; color: #1F4E79;
    border-radius: 6px; padding: 2px 10px; font-size: 0.78rem;
    font-weight: 600; margin-bottom: 10px;
  }
</style>
""", unsafe_allow_html=True)

GITHUB_RAW  = "https://raw.githubusercontent.com/madjerad/Statsjoueurs/main"
DATA_URL    = f"{GITHUB_RAW}/StatsJoueurs2526.xlsx"
PHOTOS_BASE = f"{GITHUB_RAW}/Photos"
GARDIENS    = {12, 16}
C = {"primary": "#1F4E79", "accent": "#4A90D9", "green": "#1a7a3c",
     "orange": "#d97706", "red": "#c0392b", "bg": "#f0f4fa"}

REF_JOUEURS = pd.DataFrame({
    'Numéro': [2,3,4,5,7,8,9,10,12,13,15,16,19,21,24,25,33,92],
    'Nom':    ['NAUDIN','NAUDIN','HERMAND','BON','PLISSONNIER','PANIC','MINANA',
               'GREGULSKI','STEPHAN','THELCIDE','COSNIER','MAI','GOSTOMSKI',
               'CHAZALON','MINY','FAVERIN','NAUDIN','PHAROSE'],
    'Prénom': ['Paul','Théo','Mathieu','Gabriel','Jean','Milan','Lilian','Vincent',
               'Corentin','Axel','Lubin','François','Sasha','Marius','Gabin',
               'Léan','Hugo','Kylian'],
    'Joueur': ['2 NAUDIN P.','3 NAUDIN T.','4 HERMAND','5 BON','7 PLISSONNIER',
               '8 PANIC','9 MINANA','10 GREGULSKI V.','12 STEPHAN','13 THELCIDE',
               '15 COSNIER','16 MAI','19 GOSTOMSKI','21 CHAZALON','24 MINY',
               '25 FAVERIN','33 NAUDIN H.','92 PHAROSE'],
    'Poste':  ['DEMI-CENTRE','AILIER','PIVOT','ARRIERE','AILIER','ARRIERE','ARRIERE',
               'ARRIERE','GARDIEN','ARRIERE','DEMI-CENTRE','GARDIEN','PIVOT',
               'ARRIERE','PIVOT','AILIER','ARRIERE','AILIER'],
})


@st.cache_data(ttl=0)
def load_data():
    resp = requests.get(DATA_URL, timeout=20)
    resp.raise_for_status()
    buf = BytesIO(resp.content)
    # engine='openpyxl' obligatoire quand on passe un BytesIO (pas d'extension détectable)
    xl = pd.ExcelFile(buf, engine='openpyxl')

    tb         = pd.read_excel(xl, sheet_name='Tirs & Buts par Match')
    disc       = pd.read_excel(xl, sheet_name='Discipline')
    arrets     = pd.read_excel(xl, sheet_name='Arrêts')
    ref_matchs = pd.read_excel(xl, sheet_name='RefMatchs')

    # Numéro gardien depuis libellé
    arrets['Numéro'] = arrets['Gardiens'].apply(
        lambda g: 16 if 'Mai' in str(g) else (12 if 'Stephan' in str(g) else None)
    )
    # Colonne arrêts : nom variable (peut avoir espace trailing)
    col_arrets = [c for c in arrets.columns if 'Arr' in c and c != 'Numéro' and c != 'Gardiens' and c != 'Match' and c != 'Journée']
    if col_arrets:
        arrets.rename(columns={col_arrets[0]: 'Arrêts'}, inplace=True)

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


def layout_plotly(fig, title, height=300, right=10):
    fig.update_layout(
        title=title, title_font_size=13,
        plot_bgcolor='white', paper_bgcolor=C['bg'],
        height=height, margin=dict(t=42, b=8, l=8, r=right),
        font=dict(family='Inter'), legend=dict(orientation='h', y=1.14),
    )
    fig.update_yaxes(gridcolor='#e5e9f0')


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🤾 BHB – Fiches Joueurs")
    st.markdown("---")
    joueurs_tri = REF_JOUEURS.sort_values('Nom')
    options = joueurs_tri.apply(
        lambda r: f"{r['Numéro']} – {r['Prénom']} {r['Nom']}", axis=1
    ).tolist()
    sel = st.selectbox("Joueur", options)
    num_sel = int(sel.split("–")[0].strip())

    st.markdown("---")
    st.markdown("**Filtres**")
    phases = ['Toutes'] + sorted(ref_matchs['Phase'].dropna().unique())
    lieux  = ['Tous']   + sorted(ref_matchs['Lieu'].dropna().unique())
    filtre_phase = st.selectbox("Phase", phases)
    filtre_lieu  = st.selectbox("Lieu",  lieux)

    rm = ref_matchs.copy()
    if filtre_phase != 'Toutes': rm = rm[rm['Phase'] == filtre_phase]
    if filtre_lieu  != 'Tous':   rm = rm[rm['Lieu']  == filtre_lieu]

    matchs_dispo = sorted(rm['Match'].unique())
    sel_matchs   = st.multiselect("Matchs (vide = tous)", matchs_dispo, placeholder="Tous les matchs")
    matchs_actifs = sel_matchs if sel_matchs else matchs_dispo

# ── Header ────────────────────────────────────────────────────────────────────
jinfo = REF_JOUEURS[REF_JOUEURS['Numéro'] == num_sel].iloc[0]
photo = load_photo(num_sel)

c1, c2 = st.columns([1, 2.8])
with c1:
    if photo:
        st.image(photo, width=130)
    else:
        st.markdown('<div style="width:110px;height:110px;border-radius:50%;background:#2d5a8e;'
                    'display:flex;align-items:center;justify-content:center;font-size:2.2rem;'
                    'border:3px solid #4A90D9">👤</div>', unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div style="padding-top:8px">
      <div style="font-size:0.78rem;color:#888;text-transform:uppercase;letter-spacing:1px">Numéro {jinfo['Numéro']}</div>
      <div style="font-size:1.75rem;font-weight:700;color:#1a2e4a;line-height:1.15">{jinfo['Prénom']} {jinfo['Nom']}</div>
      <div style="font-size:0.92rem;color:#1F4E79;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin-top:4px">{jinfo['Poste']}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<hr style='border:none;border-top:2px solid #1F4E79;margin:18px 0 16px'>", unsafe_allow_html=True)

filtre_txt = []
if filtre_phase != 'Toutes': filtre_txt.append(filtre_phase)
if filtre_lieu  != 'Tous':   filtre_txt.append(filtre_lieu)
if sel_matchs:               filtre_txt.append(f"{len(sel_matchs)} match(s)")
if filtre_txt:
    st.markdown(f'<span class="match-badge">🔎 {" · ".join(filtre_txt)}</span>', unsafe_allow_html=True)

# ── Données filtrées ──────────────────────────────────────────────────────────
tb_f     = tb[tb['Match'].isin(matchs_actifs)         & (tb['Numéro']     == num_sel)]
disc_f   = disc[disc['Match'].isin(matchs_actifs)     & (disc['Numéro']   == num_sel)]
arrets_f = arrets[arrets['Match'].isin(matchs_actifs) & (arrets['Numéro'] == num_sel)]

matchs_joues = arrets_f['Match'].nunique() if num_sel in GARDIENS else disc_f['Match'].nunique()

st.markdown(f"""
<div class="stat-card">
  <h3>📅 Général</h3>
  <div class="kpi-row">{kpi(matchs_joues, "Matchs joués")}</div>
</div>""", unsafe_allow_html=True)

# helper : merge journée + tri chronologique
def add_journee_label(df):
    df = df.merge(ref_matchs[['Match', 'Journée']], on='Match', how='left')
    df = df.sort_values('Journée')
    df['label'] = df['Journée'].astype(str) + '<br>' + df['Match']
    return df


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
        df_plot = add_journee_label(arrets_f.copy())
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_plot['label'], y=df_plot['Arrêts'],
            marker_color=C['accent'],
            text=df_plot['Arrêts'].astype(int), textposition='outside',
            hovertemplate='%{x}<br>Arrêts : %{y}<extra></extra>',
        ))
        fig.add_hline(y=moy_arrets, line_dash='dot', line_color=C['orange'],
                      annotation_text=f"Moy {moy_arrets}", annotation_position="top left")
        layout_plotly(fig, "Arrêts par match")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════
# JOUEURS DE CHAMP
# ══════════════════════════════════════════════════════════
else:
    # ── Discipline ────────────────────────────────────────
    total_2mn   = int(disc_f['2mn'].sum()) if not disc_f.empty else 0
    total_rouge = int(disc_f['Dis'].sum()) if not disc_f.empty else 0

    st.markdown(f"""
    <div class="stat-card">
      <h3>🟨 Discipline</h3>
      <div class="kpi-row">
        {kpi(total_2mn,   "Exclusions 2 mn", "orange")}
        {kpi(total_rouge, "Cartons rouges",   "red")}
      </div>
    </div>""", unsafe_allow_html=True)

    if not disc_f.empty and (total_2mn > 0 or total_rouge > 0):
        df_disc = add_journee_label(disc_f.copy())
        df_disc['2mn'] = df_disc['2mn'].fillna(0).astype(int)
        df_disc['Dis'] = df_disc['Dis'].fillna(0).astype(int)
        df_agg = df_disc.groupby('label', sort=False).agg(
            excl=('2mn', 'sum'), rouge=('Dis', 'sum')
        ).reset_index()

        fig_d = go.Figure()
        fig_d.add_trace(go.Bar(
            name='2 mn', x=df_agg['label'], y=df_agg['excl'],
            marker_color=C['orange'], text=df_agg['excl'], textposition='outside',
            hovertemplate='%{x}<br>Exclusions 2mn : %{y}<extra></extra>',
        ))
        if df_agg['rouge'].sum() > 0:
            fig_d.add_trace(go.Bar(
                name='Rouge', x=df_agg['label'], y=df_agg['rouge'],
                marker_color=C['red'], text=df_agg['rouge'], textposition='outside',
                hovertemplate='%{x}<br>Carton rouge : %{y}<extra></extra>',
            ))
        layout_plotly(fig_d, "Discipline par match", height=280)
        fig_d.update_layout(barmode='stack')
        fig_d.update_yaxes(dtick=1)
        st.plotly_chart(fig_d, use_container_width=True)

    # ── Attaque ───────────────────────────────────────────
    total_tirs = int(tb_f['Tirs'].sum())
    total_buts = int(tb_f['Buts'].sum())
    eff_pct    = round(total_buts / total_tirs * 100, 1) if total_tirs > 0 else 0
    efficacite = f"{eff_pct}%" if total_tirs > 0 else "—"
    moy_buts   = round(total_buts / matchs_joues, 1) if matchs_joues > 0 else 0

    st.markdown(f"""
    <div class="stat-card">
      <h3>🎯 Attaque</h3>
      <div class="kpi-row">
        {kpi(total_tirs,  "Tirs")}
        {kpi(total_buts,  "Buts",           "green")}
        {kpi(efficacite,  "Efficacité tir",  "green")}
        {kpi(moy_buts,    "Buts / match")}
      </div>
    </div>""", unsafe_allow_html=True)

    if not tb_f.empty:
        df_tb = add_journee_label(tb_f.copy())
        df_tb['Manqués'] = df_tb['Tirs'] - df_tb['Buts']
        df_tb['Eff%']    = (df_tb['Buts'] / df_tb['Tirs'] * 100).round(1)

        # Barres empilées Buts / Manqués + ligne efficacité (axe 2)
        fig_att = go.Figure()
        fig_att.add_trace(go.Bar(
            name='Buts', x=df_tb['label'], y=df_tb['Buts'],
            marker_color=C['green'],
            text=df_tb['Buts'], textposition='inside', textfont_color='white',
            hovertemplate='%{x}<br>Buts : %{y}<extra></extra>',
        ))
        fig_att.add_trace(go.Bar(
            name='Tirs manqués', x=df_tb['label'], y=df_tb['Manqués'],
            marker_color='#c8d8e8',
            hovertemplate='%{x}<br>Manqués : %{y}<extra></extra>',
        ))
        fig_att.add_trace(go.Scatter(
            name='Efficacité %', x=df_tb['label'], y=df_tb['Eff%'],
            mode='lines+markers', line=dict(color=C['orange'], width=2),
            marker=dict(size=6), yaxis='y2',
            hovertemplate='%{x}<br>Efficacité : %{y}%<extra></extra>',
        ))
        layout_plotly(fig_att, "Tirs & Buts par match", height=320, right=50)
        fig_att.update_layout(
            barmode='stack',
            yaxis=dict(title='Tirs', gridcolor='#e5e9f0'),
            yaxis2=dict(title='Efficacité %', overlaying='y', side='right',
                        range=[0, 115], showgrid=False, ticksuffix='%'),
        )
        st.plotly_chart(fig_att, use_container_width=True)

        # Gauge efficacité globale
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number",
            value=eff_pct,
            number={'suffix': '%', 'font': {'size': 30, 'color': C['primary']}},
            title={'text': "Efficacité globale au tir", 'font': {'size': 13}},
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
            height=210, margin=dict(t=30, b=8, l=30, r=30),
            paper_bgcolor=C['bg'], font=dict(family='Inter'),
        )
        st.plotly_chart(fig_g, use_container_width=True)

st.markdown("<br><div style='text-align:center;color:#aaa;font-size:0.75rem'>"
            "BHB Analytics · Saison 2025–2026</div>", unsafe_allow_html=True)
