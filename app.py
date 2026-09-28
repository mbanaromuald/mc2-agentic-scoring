<<<<<<< HEAD
"""MC2 - Systeme Agentique de Credit Scoring Alternatif et de Conseil Rural."""
try:
    __import__("pysqlite3")
    import sys
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass  # environnement local avec un sqlite3 deja recent (ex: image Docker)

=======
>>>>>>> a06c9023fba643c4cb12587010ba021eb20b7d9e
import json
import os

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from agents.closer import execute_disbursement
from agents.pipeline import run_pipeline
from core import config
from core.data import PROFILES, BENCHMARK_KG_HA
from core.llm import ask, llm_available
from core.rag import retrieve

st.set_page_config(page_title="MC2 · Scoring agentique", page_icon="🌱", layout="wide")
fcfa = lambda x: f"{int(x):,}".replace(",", " ") + " FCFA"

# ───────────────────────── Design ─────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,800&family=Manrope:wght@400;500;700&display=swap');
:root{--nuit:#0D1B17;--canopee:#14282A;--feuille:#58B383;--or:#E0A93B;--ivoire:#EFE9DC;--brume:#9FB3A8;--indigo:#3D4E8C;--laterite:#D2694A}
html,body,[class*="css"],.stApp{font-family:'Manrope',sans-serif}
.stApp{background:radial-gradient(1100px 500px at 85% -10%,#1d4a3a55,transparent),var(--nuit)}
.block-container{padding-top:1.4rem;max-width:1250px}
h1,h2,h3{font-family:'Fraunces',serif!important;letter-spacing:-.01em}
[data-testid="stSidebar"]{background:#0a1512;border-right:1px solid #ffffff12}
header[data-testid="stHeader"]{background:transparent}

/* Hero */
.hero{position:relative;padding:3rem 2.6rem 2.4rem;border-radius:28px;overflow:hidden;
 background:linear-gradient(135deg,#14372c 0%,#0f2620 55%,#101e2e 100%);border:1px solid #ffffff14}
.hero:before{content:"";position:absolute;right:-90px;top:-90px;width:380px;height:380px;border-radius:50%;
 background:conic-gradient(from 200deg,var(--or),var(--feuille),var(--indigo),var(--or));filter:blur(70px);opacity:.42;animation:spin 26s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
@media(prefers-reduced-motion:reduce){.hero:before{animation:none}}
.hero .tag{color:var(--or);font-weight:700;font-size:.95rem;margin-bottom:.9rem}
.hero h1{font-size:clamp(2.1rem,4.6vw,3.7rem);line-height:1.04;font-weight:800;color:var(--ivoire);max-width:820px;margin:0 0 1rem}
.hero h1 span{font-style:italic;font-weight:400;color:var(--or)}
.hero p{color:#cfd9cf;max-width:640px;font-size:1.06rem;line-height:1.65}
.author{display:inline-flex;gap:.7rem;align-items:center;margin-top:1.4rem;padding:.55rem 1.05rem;border-radius:999px;
 background:#ffffff10;border:1px solid #E0A93B66;color:var(--ivoire);font-size:.95rem}
.author b{color:var(--or);font-family:'Fraunces',serif;font-size:1.05rem}
/* Bandeau tissé (élément signature) */
.weave{height:16px;margin:0 0 1.6rem;border-radius:0 0 12px 12px;
 background:
  repeating-linear-gradient(90deg,var(--or) 0 22px,var(--nuit) 22px 26px,var(--laterite) 26px 48px,var(--nuit) 48px 52px,var(--feuille) 52px 74px,var(--nuit) 74px 78px,var(--indigo) 78px 100px,var(--nuit) 100px 104px);
 -webkit-mask:repeating-linear-gradient(135deg,#000 0 6px,#0006 6px 8px);mask:repeating-linear-gradient(135deg,#000 0 6px,#0006 6px 8px)}
/* Cartes */
.card{background:linear-gradient(160deg,#173a35aa,#10231fcc);border:1px solid #ffffff14;border-radius:20px;padding:1.4rem 1.4rem 1.2rem;height:100%}
.card h4{font-family:'Fraunces',serif;font-size:1.25rem;color:var(--ivoire);margin:.1rem 0 .5rem}
.card p,.card li{color:#c4d0c8;font-size:.95rem;line-height:1.55}
.card .ic{font-size:1.9rem}
.card.agent1{border-top:3px solid var(--feuille)}.card.agent2{border-top:3px solid var(--or)}.card.agent3{border-top:3px solid var(--indigo)}
.eq{display:flex;gap:1rem;align-items:center;justify-content:center;flex-wrap:wrap;font-family:'Fraunces',serif;font-size:1.35rem;color:var(--ivoire);
 padding:1.1rem;border-radius:18px;border:1px dashed #E0A93B77;background:#ffffff07;margin:1.2rem 0}
.eq b{color:var(--or)}
/* KPI */
.kpi{background:#ffffff0a;border:1px solid #ffffff14;border-radius:18px;padding:1.1rem 1.2rem}
.kpi .l{color:var(--brume);font-size:.85rem}.kpi .v{font-family:'Fraunces',serif;font-size:1.75rem;color:var(--ivoire);font-weight:600;line-height:1.25}
.grade{display:inline-block;padding:.05rem .9rem;border-radius:12px;font-family:'Fraunces',serif;font-size:1.9rem;font-weight:800;color:#0D1B17}
.gA,.gB{background:var(--feuille)}.gC{background:var(--or)}.gD{background:var(--laterite)}.gE{background:#c0392b;color:#fff}
.pill{display:inline-block;padding:.3rem .8rem;margin:.2rem .3rem .2rem 0;border-radius:999px;font-size:.85rem}
.ok{background:#58B38326;color:#9be0bb;border:1px solid #58B38366}.warn{background:#D2694A26;color:#f3a58b;border:1px solid #D2694A66}
.foot{margin-top:2.5rem;padding:1.2rem 0;border-top:1px solid #ffffff14;text-align:center;color:var(--brume);font-size:.9rem}
.foot b{color:var(--or)}
.stButton>button{border-radius:14px;font-weight:700;border:1px solid #E0A93B99;padding:.6rem 1.3rem}
.stButton>button[kind="primary"]{background:linear-gradient(135deg,#E0A93B,#c98d1f);color:#1a1405;border:none}
.stTabs [data-baseweb="tab"]{font-weight:700;font-size:1rem}
</style>
""", unsafe_allow_html=True)


def plot_layout(fig, h=340):
    fig.update_layout(height=h, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#EFE9DC", family="Manrope"),
                      legend=dict(orientation="h", y=-0.15))
    return fig


# ───────────────────────── Sidebar ─────────────────────────
with st.sidebar:
    st.markdown("### 🌱 MC2 · Scoring agentique")
    st.caption("Groupe SAPA — inclusion financière rurale")
    options = {f"{p['nom']} · {p['activite']}": cid for cid, p in PROFILES.items()}
    options["✨ Dossier personnalisé"] = "CUSTOM"
    choix = st.selectbox("Dossier à instruire", list(options.keys()))
    cid = options[choix]
    profile = dict(PROFILES["C001"]) if cid == "CUSTOM" else dict(PROFILES[cid])

    if cid == "CUSTOM":
        st.markdown("**Simulez un profil**")
        profile.update(nom="Client simulé", activite="Activité agricole", localite="Zone rurale",
                       culture=st.selectbox("Culture", list(BENCHMARK_KG_HA), format_func=str.capitalize),
                       operateur=st.radio("Opérateur", ["MTN MoMo", "Orange Money"], horizontal=True),
                       fiabilite=st.slider("Fiabilité de paiement", 0.0, 1.0, 0.7, 0.05),
                       revenu=st.number_input("Revenu mensuel moyen (FCFA)", 20_000, 500_000, 90_000, 5_000),
                       volatilite=st.slider("Volatilité saisonnière", 0.1, 0.9, 0.4, 0.05),
                       rendement=st.slider("Rendement vs moyenne locale", 0.5, 1.4, 0.95, 0.05),
                       anciennete=st.slider("Ancienneté (ans)", 0, 15, 4),
                       demande=st.number_input("Montant demandé (FCFA)", 100_000, 5_000_000, 1_000_000, 100_000),
                       objet="Financement de campagne agricole", surface_ha=2.0)
    else:
        st.info(f"**Demande :** {fcfa(profile['demande'])}\n\n{profile['objet']}")

    st.divider()
    key = st.text_input("Clé API Groq", type="password", value=os.getenv("GROQ_API_KEY", ""),
                        help="Gratuite sur console.groq.com. Sans clé, le système fonctionne en mode déterministe.")
    if key:
        os.environ["GROQ_API_KEY"] = key
    st.caption("🟢 Llama actif via Groq" if llm_available() else "🟠 Mode hors-ligne (sans LLM)")
    st.caption("Données synthétiques de démonstration.")

# ───────────────────────── Hero ─────────────────────────
st.markdown(f"""
<div class="hero">
  <div class="tag">MC2 · Groupe SAPA · Microfinance rurale</div>
  <h1>Le crédit qui reconnaît <span>le travail de la terre</span></h1>
  <p>Trois agents d'IA transforment les traces de la vie économique rurale — Mobile Money, tontines,
  achats d'intrants, récoltes — en un score de confiance explicable, prêt pour le comité de crédit.</p>
  <div class="author">Conçu et réalisé par <b>{config.AUTHOR}</b></div>
</div>
<div class="weave"></div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["Le projet", "Analyse agentique", "Rapport & décaissement", "Conseiller rural"])

# ───────────────────────── Tab 1 ─────────────────────────
with tab1:
    st.markdown("### Le problème : des producteurs solvables, mais invisibles")
    st.write("En zone rurale, les petits agriculteurs et micro-entrepreneurs n'ont ni états financiers ni historique "
             "de crédit. Les dossiers s'allongent ou sont refusés, alors que leur discipline de paiement existe, "
             "mais dans d'autres traces que celles de la banque.")
    c1, c2, c3 = st.columns(3)
    c1.markdown("""<div class="card agent1"><div class="ic">🌾</div><h4>Agent Collecteur</h4>
    <p>Ingère et normalise les données alternatives :</p><ul><li>Flux MTN MoMo / Orange Money</li>
    <li>Régularité des tontines</li><li>Paiements des intrants agricoles</li><li>Rendements par saison</li></ul></div>""", unsafe_allow_html=True)
    c2.markdown("""<div class="card agent2"><div class="ic">⚖️</div><h4>Agent Évaluateur</h4>
    <p>Calcule un score de confiance de 0 à 1000, pondéré pour la réalité rurale (saisonnalité, médiane des revenus),
    puis le justifie à l'aide de la politique MC2 (RAG sur ChromaDB).</p></div>""", unsafe_allow_html=True)
    c3.markdown("""<div class="card agent3"><div class="ic">📨</div><h4>Agent de Clôture</h4>
    <p>Rédige le rapport d'aide à la décision, prépare l'ordre de décaissement vers la banque mère et notifie le client.
    Le comité garde la décision finale.</p></div>""", unsafe_allow_html=True)
    st.markdown('<div class="eq"><span>Compétences numérisées <b>(C)</b></span> ➜ <span>Moyens mieux gérés <b>(M)</b></span></div>', unsafe_allow_html=True)
    st.markdown("**Ce que le jury doit retenir :** l'inclusion financière s'accélère sans exposer MC2 à des risques "
                "inconsidérés. Le score est **transparent** (chaque point est traçable), le plafond est calculé sur la "
                "**capacité réelle** de remboursement, et un **humain valide** chaque décaissement.")

# ───────────────────────── Tab 2 ─────────────────────────
with tab2:
    left, right = st.columns([3, 1])
    left.markdown(f"#### Dossier : {profile['nom']} — {profile['activite']}")
    lancer = right.button("Lancer l'analyse", type="primary", width="stretch")
    if lancer:
        with st.status("Orchestration des agents…", expanded=True) as status:
            def on_step(agent, action, ms):
                st.write(f"**{agent}** — {action} ✓ ({ms} ms)")
            st.session_state["res"] = run_pipeline(cid, profile, on_step)
            st.session_state["cid"], st.session_state["profile"] = cid, profile
            st.session_state.pop("paid", None)
            status.update(label="Analyse terminée", state="complete", expanded=False)

    res = st.session_state.get("res")
    if not res:
        st.info("Choisissez un dossier dans le menu de gauche, puis lancez l'analyse.")
    else:
        s, f, raw = res["scoring"], res["collector"]["features"], res["collector"]["raw"]
        p = st.session_state["profile"]
        k1, k2, k3, k4 = st.columns(4)
        k1.markdown(f'<div class="kpi"><div class="l">Score de confiance</div><div class="v">{s["score"]} <small style="font-size:1rem;color:#9FB3A8">/ 1000</small></div></div>', unsafe_allow_html=True)
        k2.markdown(f'<div class="kpi"><div class="l">Grade</div><div class="grade g{s["grade"]}">{s["grade"]}</div></div>', unsafe_allow_html=True)
        k3.markdown(f'<div class="kpi"><div class="l">Décision proposée</div><div class="v" style="font-size:1.05rem">{s["decision"]}</div></div>', unsafe_allow_html=True)
        k4.markdown(f'<div class="kpi"><div class="l">Montant recommandé</div><div class="v">{fcfa(s["montant_recommande"])}</div></div>', unsafe_allow_html=True)
        st.write("")

        g, r = st.columns(2)
        gauge = go.Figure(go.Indicator(mode="gauge+number", value=s["score"], number=dict(font=dict(family="Fraunces", size=54)),
            gauge=dict(axis=dict(range=[0, 1000], tickcolor="#9FB3A8"), bar=dict(color="#EFE9DC", thickness=.22),
                       bgcolor="rgba(0,0,0,0)", borderwidth=0,
                       steps=[dict(range=[0, 450], color="#c0392b"), dict(range=[450, 550], color="#D2694A"),
                              dict(range=[550, 650], color="#E0A93B"), dict(range=[650, 750], color="#8fc98f"),
                              dict(range=[750, 1000], color="#58B383")])))
        g.plotly_chart(plot_layout(gauge, 320), width="stretch")
        cats = list(s["composantes"].keys())
        radar = go.Figure(go.Scatterpolar(r=list(s["composantes"].values()) + [list(s["composantes"].values())[0]],
                          theta=cats + [cats[0]], fill="toself", line=dict(color="#E0A93B"), fillcolor="rgba(224,169,59,.25)"))
        radar.update_layout(polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(range=[0, 100], gridcolor="#ffffff22"),
                                       angularaxis=dict(gridcolor="#ffffff22")))
        r.plotly_chart(plot_layout(radar, 320), width="stretch")

        mm = raw["mobile_money"]
        bar = go.Figure([go.Bar(x=mm["mois"], y=mm["entrees"], name="Entrées", marker_color="#58B383"),
                         go.Bar(x=mm["mois"], y=mm["sorties"], name="Sorties", marker_color="#3D4E8C")])
        bar.update_layout(barmode="group", title=f"Flux {p['operateur']} sur 12 mois (FCFA)")
        st.plotly_chart(plot_layout(bar, 300), width="stretch")

        a, b = st.columns(2)
        a.markdown("**Points forts**")
        a.markdown("".join(f'<span class="pill ok">{x}</span>' for x in s["forces"]) or "—", unsafe_allow_html=True)
        b.markdown("**Points de vigilance**")
        b.markdown("".join(f'<span class="pill warn">{x}</span>' for x in s["alertes"]) or "—", unsafe_allow_html=True)

        st.markdown("**Contribution de chaque composante**")
        st.dataframe(pd.DataFrame([{"Composante": k, "Note /100": v, "Poids": f"{s['poids'][k]:.0%}",
                                    "Points apportés": round(v * s["poids"][k] * 10)} for k, v in s["composantes"].items()]),
                     hide_index=True, width="stretch")
        with st.expander("Justification de l'agent Évaluateur" + (f" · modèle {s['modele']}" if s["modele"] else "")):
            st.write(s["justification"])
        with st.expander("Trace d'exécution des agents"):
            st.dataframe(pd.DataFrame(res["trace"]), hide_index=True, width="stretch")
        with st.expander("Données brutes collectées"):
            t1, t2, t3 = st.tabs(["Tontine", "Intrants", "Récoltes"])
            t1.dataframe(raw["tontine"], hide_index=True); t2.dataframe(raw["intrants"], hide_index=True)
            t3.dataframe(raw["recoltes"], hide_index=True)

# ───────────────────────── Tab 3 ─────────────────────────
with tab3:
    res = st.session_state.get("res")
    if not res:
        st.info("Lancez d'abord une analyse dans l'onglet « Analyse agentique ».")
    else:
        cl, s = res["closing"], res["scoring"]
        st.markdown(cl["rapport"])
        d1, d2 = st.columns(2)
        d1.download_button("Télécharger le rapport (.md)", cl["rapport"], f"{cl['ordre']['reference']}.md", width="stretch")
        d2.download_button("Télécharger l'ordre (.json)", json.dumps(cl["ordre"], ensure_ascii=False, indent=2),
                           f"{cl['ordre']['reference']}.json", width="stretch")
        st.markdown("### Décaissement via la banque mère")
        ordre = st.session_state.get("paid") or cl["ordre"]
        st.json(ordre)
        if not cl["ordre"]["autorise"]:
            st.error("Aucun décaissement possible pour ce dossier (grade E ou montant nul).")
        elif st.session_state.get("paid"):
            st.success(f"Fonds envoyés — transaction {ordre['transaction_id']}")
        else:
            ok = st.checkbox("Le comité de crédit valide ce dossier et autorise le décaissement")
            if st.button("Débloquer les fonds", type="primary", disabled=not ok):
                st.session_state["paid"] = execute_disbursement(cl["ordre"])
                st.rerun()
        st.markdown("**Notification SMS au bénéficiaire**")
        st.code(cl["sms"], language=None)

# ───────────────────────── Tab 4 ─────────────────────────
with tab4:
    st.markdown("#### Posez une question sur la politique MC2 ou sur les bonnes pratiques agricoles")
    st.caption("Réponses ancrées dans la base ChromaDB (politique de crédit et conseil rural).")
    st.session_state.setdefault("chat", [])
    for role, msg in st.session_state["chat"]:
        st.chat_message(role).write(msg)
    q = st.chat_input("Ex. : Comment améliorer mon score avant ma prochaine demande ?")
    if q:
        st.session_state["chat"].append(("user", q)); st.chat_message("user").write(q)
        docs = retrieve(q, k=3)
        ctx = "\n\n".join(d.page_content for d in docs)
        ans, model = ask("Tu es le conseiller rural de MC2. Réponds en français, simplement, en 5 phrases maximum, "
                         "uniquement à partir du contexte. Si l'information manque, dis-le.\n\nCONTEXTE:\n" + ctx, q)
        ans = ans or "Mode hors-ligne : voici les passages les plus pertinents de la base.\n\n" + ctx
        st.session_state["chat"].append(("assistant", ans)); st.chat_message("assistant").write(ans)
        with st.expander("Sources ChromaDB"):
            for d in docs: st.caption(f"📄 {d.metadata['source']}")

st.markdown(f'<div class="foot">Projet présenté à <b>SAPA</b> pour <b>MC2</b> · Conçu et réalisé par <b>{config.AUTHOR}</b> · '
            f'Streamlit · Llama via Groq · ChromaDB · LangChain · Docker</div>', unsafe_allow_html=True)
