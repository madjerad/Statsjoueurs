@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

:root {
  color-scheme: light only !important;
  --bhb-navy:    #1a2744;
  --bhb-blue:    #1e4d9b;
  --bhb-blue2:   #2d65c4;
  --bhb-red:     #c0272d;
  --bhb-offwhite:#f4f6fb;
  --bhb-white:   #ffffff;
  --bhb-gray:    #e8ecf4;
  --bhb-muted:   #6b7a99;
  --bhb-green:   #1a7a3c;
  --bhb-orange:  #d97706;
}

html, body, [data-testid="stApp"] {
  font-family: 'Inter', sans-serif !important;
  background-color: var(--bhb-offwhite) !important;
  color: var(--bhb-navy) !important;
}

.block-container {
  padding: 0.6rem 1rem 0.4rem !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
  background: var(--bhb-navy) !important;
  min-width: 220px !important;
  max-width: 220px !important;
}
section[data-testid="stSidebar"] * {
  color: var(--bhb-white) !important;
}
section[data-testid="stSidebar"] .stSelectbox > div > div,
section[data-testid="stSidebar"] .stMultiSelect > div > div {
  background: rgba(255,255,255,0.12) !important;
  border: 1px solid rgba(255,255,255,0.25) !important;
  color: var(--bhb-white) !important;
}
section[data-testid="stSidebar"] label {
  color: rgba(255,255,255,0.75) !important;
  font-size: 0.78rem !important;
}
section[data-testid="stSidebar"] hr {
  border-color: rgba(255,255,255,0.15) !important;
}

/* ── Cartes stats ── */
.stat-card {
  background: var(--bhb-white);
  border-left: 3px solid var(--bhb-blue);
  border-radius: 8px;
  padding: 8px 12px 7px;
  margin-bottom: 7px;
  box-shadow: 0 1px 4px rgba(26,39,68,0.07);
}
.stat-card h3 {
  margin: 0 0 7px 0;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--bhb-blue);
  font-weight: 700;
}

/* ── KPI ── */
.kpi-row {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
.kpi {
  background: var(--bhb-offwhite);
  border-radius: 6px;
  padding: 5px 8px;
  text-align: center;
  flex: 1;
  min-width: 60px;
}
.kpi .val {
  font-size: 1.3rem;
  font-weight: 800;
  color: var(--bhb-navy);
  line-height: 1.1;
}
.kpi .lbl {
  font-size: 0.6rem;
  color: var(--bhb-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-top: 1px;
}
.kpi.green .val  { color: var(--bhb-green); }
.kpi.orange .val { color: var(--bhb-orange); }
.kpi.red .val    { color: var(--bhb-red); }
.kpi.blue .val   { color: var(--bhb-blue); }

/* ── Badge filtre ── */
.filter-badge {
  display: inline-block;
  background: rgba(45,101,196,0.1);
  color: var(--bhb-blue);
  border: 1px solid rgba(45,101,196,0.3);
  border-radius: 5px;
  padding: 2px 8px;
  font-size: 0.7rem;
  font-weight: 600;
  margin-bottom: 6px;
}

/* ── Header joueur ── */
.player-header {
  background: linear-gradient(120deg, var(--bhb-navy) 0%, var(--bhb-blue) 100%);
  border-radius: 10px;
  padding: 10px 14px;
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 10px;
}
.player-header img {
  border-radius: 8px;
  border: 2px solid rgba(255,255,255,0.4);
  object-fit: cover;
  width: 90px;
  height: 108px;
  image-rendering: -webkit-optimize-contrast;
  image-rendering: crisp-edges;
  flex-shrink: 0;
}
.player-no-photo {
  width: 90px;
  height: 108px;
  border-radius: 8px;
  background: rgba(255,255,255,0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  border: 2px solid rgba(255,255,255,0.3);
  flex-shrink: 0;
}
.player-info {
  flex: 1;
  min-width: 0;
}
.player-info .numero {
  font-size: 0.72rem;
  color: rgba(255,255,255,0.6);
  text-transform: uppercase;
  letter-spacing: 1px;
}
.player-info .nom {
  font-size: 1.35rem;
  font-weight: 800;
  color: #ffffff;
  line-height: 1.15;
  word-break: break-word;
}
.player-info .poste {
  display: inline-block;
  margin-top: 4px;
  background: var(--bhb-red);
  color: #fff;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  border-radius: 4px;
  padding: 2px 7px;
}

/* ── Désactiver zoom Plotly (touch) ── */
.js-plotly-plot .plotly { touch-action: pan-y !important; }
.plotly-graph-div       { touch-action: pan-y !important; }

/* ── Responsive mobile ── */
@media (max-width: 768px) {
  .block-container       { padding: 0.4rem 0.5rem !important; }
  .player-header         { padding: 8px 10px; gap: 10px; }
  .player-header img     { width: 70px; height: 84px; }
  .player-info .nom      { font-size: 1.1rem; }
  .kpi .val              { font-size: 1.1rem; }
  section[data-testid="stSidebar"] {
    min-width: 200px !important;
    max-width: 200px !important;
  }
}
