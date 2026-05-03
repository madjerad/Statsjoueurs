import streamlit as st
import pandas as pd
import requests
from io import BytesIO
from PIL import Image

st.set_page_config(
    page_title="BHB – Fiches Joueurs",
    page_icon="🤾",
    layout="centered",
)

# ── Styles ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  .bhb-header {
    background: linear-gradient(135deg, #1a2e4a 0%, #1F4E79 100%);
    border-radius: 16px;
    padding: 28px 32px 20px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 24px;
  }
  .bhb-header img { border-radius: 50%; width: 110px; height: 110px; object-fit: cover; border: 3px solid #4A90D9; }
  .bhb-header-info h1 { color: #fff; margin: 0; font-size: 1.7rem; font-weight: 700; }
  .bhb-header-info .poste { color: #90c4f8; font-size: 0.95rem; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; margin-top: 4px; }
  .bhb-header-info .numero { color: #cde; font-size: 0.88rem; margin-top: 2px; }

  .stat-card {
    background: #f0f4fa;
    border-left: 4px solid #1F4E79;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 14px;
  }
  .stat-card h3 { margin: 0 0 12px 0; font-size: 0.85rem; text-transform: uppercase;
                  letter-spacing: 1px; color: #1F4E79; font-weight: 700; }
  .kpi-row { display: flex; gap: 16px; flex-wrap: wrap; }
  .kpi { background: white; border-radius: 8px; padding: 12px 18px; text-align: center;
         flex: 1; min-width: 80px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
  .kpi .val { font-size: 1.8rem; font-weight: 700; color: #1a2e4a; line-height: 1.1; }
  .kpi .lbl { font-size: 0.72rem; color: #666; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 4px; }
  .kpi.green .val { color: #1a7a3c; }
  .kpi.orange .val { color: #b85e00; }
  .kpi.red .val   { color: #c0392b; }

  .no-photo { width: 110px; height: 110px; border-radius: 50%; background: #2d5a8e;
              display: flex; align-items: center; justify-content: center;
              font-size: 2.2rem; border: 3px solid #4A90D9; }

  .section-divider { border: none; border-top: 1px solid #dde4ef; margin: 18px 0; }
  .match-badge { display: inline-block; background: #e8f0fb; color: #1F4E79; border-radius: 6px;
                 padding: 2px 8px; font-size: 0.78rem; font-weight: 600; margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)

# ── Config GitHub ────────────────────────────────────────────────────────────
GITHUB_RAW = "https://raw.githubusercontent.com/madjerad/dma/main"
DATA_URL = f"{GITHUB_RAW}/StatsJoueurs2526.xlsx"
PHOTOS_BASE = f"{GITHUB_RAW}/Photos"
GARDIENS = {12, 16}

# ── Chargement données ───────────────────────────────────────────────────────
@st.cache_data(ttl=0)
def load_data():
    resp = requests.get(DATA_URL, timeout=20)
    buf = BytesIO(resp.content)
    xl = pd.ExcelFile(buf)

    ref_joueurs = pd.DataFrame({
        'Numéro': [5,21,15,25,19,10,4,16,9,24,2,3,33,8,92,7,12,13],
        'Nom':    ['BON','CHAZALON','COSNIER','FAVERIN','GOSTOMSKI','GREGULSKI',
                   'HERMAND','MAI','MINANA','MINY','NAUDIN','NAUDIN','NAUDIN',
                   'PANIC','PHAROSE','PLISSONNIER','STEPHAN','THELCIDE'],
        'Prénom': ['Gabriel','Marius','Lubin','Léan','Sasha','Vincent','Mathieu',
                   'François','Lilian','Gabin','Paul','Théo','Hugo','Milan',
                   'Kylian','Jean','Corentin','Axel'],
        'Joueur': ['5 BON','21 CHAZALON','15 COSNIER','25 FAVERIN','19 GOSTOMSKI',
                   '10 GREGULSKI V.','4 HERMAND','16 MAI','9 MINANA','24 MINY',
                   '2 NAUDIN P.','3 NAUDIN T.','33 NAUDIN H.','8 PANIC',
                   '92 PHAROSE','7 PLISSONNIER','12 STEPHAN','13 THELCIDE'],
        'Poste':  ['ARRIERE','ARRIERE','DEMI-CENTRE','AILIER','PIVOT','ARRIERE',
                   'PIVOT','GARDIEN','ARRIERE','PIVOT','DEMI-CENTRE','AILIER',
                   'ARRIERE','ARRIERE','AILIER','AILIER','GARDIEN','ARRIERE'],
    })

    tb = pd.read_excel(xl, sheet_name='Tirs & Buts par Match')
    disc = pd.read_excel(xl, sheet_name='Discipline')
    arrets = pd.read_excel(xl, sheet_name='Arrêts')
    ref_matchs = pd.read_excel(xl, sheet_name='RefMatchs')

    # Normalise noms gardiens dans Arrêts → numéro
    arrets['Numéro'] = arrets['Gardiens'].apply(
        lambda g: 16 if 'Mai' in str(g) else (12 if 'Stephan' in str(g) else None)
    )
    arrets.rename(columns={'Arrêt ': 'Arrêts'}, inplace=True)

    # Jointure numéro dans Discipline (ex: '2 NAUDIN P.' → 2)
    disc['Numéro'] = disc['Joueurs'].str.extract(r'^(\d+)').astype(float)

    return ref_joueurs, tb, disc, arrets, ref_matchs

ref_joueurs, tb, disc, arrets, ref_matchs = load_data()

# ── Sidebar : sélection joueur + filtres ─────────────────────────────────────
with st.sidebar:
    st.markdown("### 🤾 BHB – Fiches Joueurs")
    st.markdown("---")

    joueurs_tri = ref_joueurs.sort_values('Nom')
    options_joueurs = joueurs_tri.apply(
        lambda r: f"{r['Numéro']} – {r['Prénom']} {r['Nom']}", axis=1
    ).tolist()
    sel = st.selectbox("Joueur", options_joueurs, index=0)
    num_sel = int(sel.split("–")[0].strip())

    st.markdown("---")
    st.markdown("**Filtres**")

    matchs_dispo = sorted(ref_matchs['Match'].unique())
    phases = ['Toutes'] + sorted(ref_matchs['Phase'].dropna().unique())
    lieux  = ['Tous'] + sorted(ref_matchs['Lieu'].dropna().unique())

    filtre_phase = st.selectbox("Phase", phases)
    filtre_lieu  = st.selectbox("Lieu", lieux)

    rm_filtre = ref_matchs.copy()
    if filtre_phase != 'Toutes':
        rm_filtre = rm_filtre[rm_filtre['Phase'] == filtre_phase]
    if filtre_lieu != 'Tous':
        rm_filtre = rm_filtre[rm_filtre['Lieu'] == filtre_lieu]

    matchs_filtres_options = sorted(rm_filtre['Match'].unique())
    sel_matchs = st.multiselect(
        "Matchs (vide = tous)",
        matchs_filtres_options,
        default=[],
        placeholder="Tous les matchs",
    )
    if sel_matchs:
        matchs_actifs = sel_matchs
    else:
        matchs_actifs = matchs_filtres_options

# ── Chargement photo ─────────────────────────────────────────────────────────
def load_photo(numero):
    url = f"{PHOTOS_BASE}/{numero}.jpg"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return Image.open(BytesIO(r.content))
    except Exception:
        pass
    return None

# ── Infos joueur ─────────────────────────────────────────────────────────────
joueur_info = ref_joueurs[ref_joueurs['Numéro'] == num_sel].iloc[0]
photo = load_photo(num_sel)

# ── Header ───────────────────────────────────────────────────────────────────
col_photo, col_info = st.columns([1, 2.8])
with col_photo:
    if photo:
        st.image(photo, width=130)
    else:
        st.markdown(f'<div class="no-photo">👤</div>', unsafe_allow_html=True)

with col_info:
    st.markdown(f"""
    <div style="padding-top:8px">
      <div style="font-size:0.8rem;color:#666;text-transform:uppercase;letter-spacing:1px">
        Numéro {joueur_info['Numéro']}
      </div>
      <div style="font-size:1.8rem;font-weight:700;color:#1a2e4a;line-height:1.1">
        {joueur_info['Prénom']} {joueur_info['Nom']}
      </div>
      <div style="font-size:0.95rem;color:#1F4E79;font-weight:600;text-transform:uppercase;
                  letter-spacing:1px;margin-top:4px">
        {joueur_info['Poste']}
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border:none;border-top:2px solid #1F4E79;margin:18px 0 20px'>",
            unsafe_allow_html=True)

# Filtre des données sur matchs actifs
tb_f    = tb[tb['Match'].isin(matchs_actifs) & (tb['Numéro'] == num_sel)]
disc_f  = disc[disc['Match'].isin(matchs_actifs) & (disc['Numéro'] == num_sel)]
arrets_f = arrets[arrets['Match'].isin(matchs_actifs) & (arrets['Numéro'] == num_sel)]

# Matchs joués (présent dans Discipline pour joueurs de champ, Arrêts pour gardiens)
if num_sel in GARDIENS:
    matchs_joues = arrets_f['Match'].nunique()
else:
    matchs_joues = disc_f['Match'].nunique()

# ── Badge filtre actif ────────────────────────────────────────────────────────
filtre_txt = []
if filtre_phase != 'Toutes': filtre_txt.append(filtre_phase)
if filtre_lieu != 'Tous': filtre_txt.append(filtre_lieu)
if sel_matchs: filtre_txt.append(f"{len(sel_matchs)} match(s) sélectionné(s)")
if filtre_txt:
    st.markdown(f'<span class="match-badge">🔎 {" · ".join(filtre_txt)}</span>',
                unsafe_allow_html=True)

# ── KPI : Matchs joués ───────────────────────────────────────────────────────
def kpi_html(val, label, cls=""):
    return f'<div class="kpi {cls}"><div class="val">{val}</div><div class="lbl">{label}</div></div>'

st.markdown(f"""
<div class="stat-card">
  <h3>📅 Général</h3>
  <div class="kpi-row">
    {kpi_html(matchs_joues, "Matchs joués")}
  </div>
</div>
""", unsafe_allow_html=True)

# ── Gardiens ─────────────────────────────────────────────────────────────────
if num_sel in GARDIENS:
    total_arrets = int(arrets_f['Arrêts'].sum())
    moy_arrets = round(arrets_f['Arrêts'].mean(), 1) if matchs_joues > 0 else 0

    st.markdown(f"""
    <div class="stat-card">
      <h3>🧤 Arrêts</h3>
      <div class="kpi-row">
        {kpi_html(total_arrets, "Total arrêts", "green")}
        {kpi_html(moy_arrets, "Moy / match")}
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── Joueurs de champ ──────────────────────────────────────────────────────────
else:
    # Discipline
    total_2mn = int(disc_f['2mn'].sum()) if disc_f['2mn'].notna().any() else 0
    total_rouge = int(disc_f['Dis'].sum()) if disc_f['Dis'].notna().any() else 0

    st.markdown(f"""
    <div class="stat-card">
      <h3>🟨 Discipline</h3>
      <div class="kpi-row">
        {kpi_html(total_2mn, "Exclusions 2 mn", "orange")}
        {kpi_html(total_rouge, "Cartons rouges", "red")}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Attaque
    total_tirs = int(tb_f['Tirs'].sum())
    total_buts = int(tb_f['Buts'].sum())
    efficacite = f"{round(total_buts / total_tirs * 100, 1)}%" if total_tirs > 0 else "—"
    moy_buts = round(total_buts / matchs_joues, 1) if matchs_joues > 0 else 0

    st.markdown(f"""
    <div class="stat-card">
      <h3>🎯 Attaque</h3>
      <div class="kpi-row">
        {kpi_html(total_tirs, "Tirs")}
        {kpi_html(total_buts, "Buts", "green")}
        {kpi_html(efficacite, "Efficacité tir", "green")}
        {kpi_html(moy_buts, "Buts / match")}
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── Détail par match ──────────────────────────────────────────────────────────
with st.expander("📋 Détail par match"):
    if num_sel in GARDIENS:
        detail = arrets_f[['Journée', 'Match', 'Arrêts']].sort_values('Journée')
        if detail.empty:
            st.info("Aucune donnée sur la sélection.")
        else:
            st.dataframe(detail.reset_index(drop=True), use_container_width=True, hide_index=True)
    else:
        d_disc = disc_f[['Journée', 'Match', '2mn', 'Dis']].rename(columns={'Dis': 'Rouge'})
        d_tirs = tb_f[['Journée', 'Match', 'Tirs', 'Buts']]
        # Merge on Journée+Match (outer pour avoir tous les matchs joués)
        all_matchs_joues = disc_f[['Journée', 'Match']].drop_duplicates()
        detail = all_matchs_joues.merge(d_tirs, on=['Journée', 'Match'], how='left') \
                                  .merge(d_disc, on=['Journée', 'Match'], how='left') \
                                  .sort_values('Journée')
        detail['2mn'] = detail['2mn'].fillna(0).astype(int)
        detail['Rouge'] = detail['Rouge'].fillna(0).astype(int)
        detail['Tirs'] = detail['Tirs'].fillna(0).astype(int)
        detail['Buts'] = detail['Buts'].fillna(0).astype(int)
        if detail.empty:
            st.info("Aucune donnée sur la sélection.")
        else:
            st.dataframe(detail.reset_index(drop=True), use_container_width=True, hide_index=True)

st.markdown("<br><div style='text-align:center;color:#aaa;font-size:0.75rem'>BHB Analytics · Saison 2025-2026</div>",
            unsafe_allow_html=True)
