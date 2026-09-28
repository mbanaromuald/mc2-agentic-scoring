"""Génération de données alternatives SYNTHÉTIQUES (démo). En production, ces
fonctions sont remplacées par des connecteurs : API MoMo/Orange Money, registre
de la tontine, fournisseurs d'intrants, relevés de coopérative."""
import zlib
import numpy as np
import pandas as pd

BENCHMARK_KG_HA = {"cacao": 600, "cafe": 700, "tomate": 20000, "manioc": 15000, "plantain": 9000}

PROFILES = {
    "C001": dict(nom="Marie Ngo Bassong", activite="Cacaoculture", localite="Mbalmayo (Centre)",
                 culture="cacao", surface_ha=3.5, anciennete=8, demande=1_500_000, operateur="MTN MoMo",
                 objet="Engrais, fongicides et main-d'œuvre de récolte",
                 fiabilite=0.92, revenu=145_000, volatilite=0.25, rendement=1.12),
    "C002": dict(nom="Jean-Pierre Tchoumi", activite="Maraîchage (tomate, piment)", localite="Dschang (Ouest)",
                 culture="tomate", surface_ha=1.2, anciennete=4, demande=800_000, operateur="Orange Money",
                 objet="Semences certifiées et système d'irrigation goutte-à-goutte",
                 fiabilite=0.72, revenu=90_000, volatilite=0.45, rendement=0.98),
    "C003": dict(nom="Aïcha Bello", activite="Transformation de manioc (gari)", localite="Bafia (Centre)",
                 culture="manioc", surface_ha=2.0, anciennete=5, demande=600_000, operateur="MTN MoMo",
                 objet="Achat d'une râpeuse et fonds de roulement",
                 fiabilite=0.55, revenu=62_000, volatilite=0.55, rendement=0.88),
    "C004": dict(nom="Étienne Fotso", activite="Caféiculture (arabica)", localite="Foumbot (Ouest)",
                 culture="cafe", surface_ha=2.0, anciennete=1, demande=2_000_000, operateur="Orange Money",
                 objet="Renouvellement des plants et séchoir",
                 fiabilite=0.30, revenu=55_000, volatilite=0.70, rendement=0.70),
    "C005": dict(nom="Pauline Mvondo", activite="Plantain & commerce vivrier", localite="Obala (Centre)",
                 culture="plantain", surface_ha=2.5, anciennete=6, demande=1_000_000, operateur="MTN MoMo",
                 objet="Extension de parcelle et stockage",
                 fiabilite=0.82, revenu=112_000, volatilite=0.35, rendement=1.03),
}


def build_raw(cid: str, p: dict) -> dict:
    rng = np.random.default_rng(zlib.crc32(f"{cid}{p['fiabilite']}{p['revenu']}".encode()))
    fi, vol = p["fiabilite"], p["volatilite"]
    months = pd.period_range(end="2026-08", periods=12, freq="M")

    # Mobile Money
    rows = []
    phase = rng.uniform(0, 6.28)
    for i, m in enumerate(months):
        active = rng.random() < (0.72 + 0.28 * fi)
        season = 1 + vol * 0.9 * np.sin(2 * np.pi * i / 12 + phase)
        entrees = max(0, p["revenu"] * season * (1 + rng.normal(0, vol * 0.35))) if active else rng.uniform(2_000, 15_000)
        ratio = float(np.clip(0.93 - 0.28 * fi + rng.normal(0, 0.05), 0.4, 1.05))
        rows.append(dict(mois=str(m), entrees=round(entrees), sorties=round(entrees * ratio),
                         nb_tx=int(entrees / 9_000 + rng.integers(0, 4)) if active else int(rng.integers(0, 4))))
    mm = pd.DataFrame(rows)

    # Tontine
    cot = int(np.clip(p["revenu"] * 0.18, 10_000, 40_000) // 5_000 * 5_000)
    tont = pd.DataFrame([dict(mois=str(m), cotisation=cot,
                              retard_jours=0 if rng.random() < fi else int(rng.integers(4, 26)))
                         for m in months])

    # Intrants agricoles
    fournisseurs = ["AgriPlus", "Comptoir Semences Centre", "SCDP Intrants", "Coop. Agri-Ouest"]
    intr = pd.DataFrame([dict(date=str(months[int(k)].asfreq("D", "start")),
                              fournisseur=fournisseurs[int(rng.integers(0, 4))],
                              montant=int(rng.integers(40, 250) * 1000),
                              retard_jours=0 if rng.random() < fi else int(rng.integers(5, 46)))
                         for k in sorted(rng.choice(12, 6, replace=False))])

    # Récoltes (4 dernières saisons)
    bench = BENCHMARK_KG_HA[p["culture"]]
    rec = pd.DataFrame([dict(saison=s, rendement_kg_ha=round(bench * p["rendement"] * (1 + rng.normal(0, vol * 0.2))),
                             reference_locale=bench)
                        for s in ["2024 A", "2024 B", "2025 A", "2025 B"]])
    return dict(mobile_money=mm, tontine=tont, intrants=intr, recoltes=rec)
