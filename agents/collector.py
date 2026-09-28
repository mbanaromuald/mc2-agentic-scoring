"""Agent 1 — Collecteur & Analyse de Données Alternatives."""
import numpy as np
from core.data import build_raw


def extract_features(raw: dict, p: dict) -> dict:
    mm, t, i, r = raw["mobile_money"], raw["tontine"], raw["intrants"], raw["recoltes"]
    inflow = mm["entrees"]
    cv = float(inflow.std() / inflow.mean()) if inflow.mean() > 0 else 1.0
    ratio = (r["rendement_kg_ha"] / r["reference_locale"]).values
    f = dict(
        mm_regularite=float(1 - min(1, cv / 0.8)),
        mm_mois_actifs=int((mm["nb_tx"] >= 5).sum()),
        mm_epargne=float(np.clip((inflow - mm["sorties"]).sum() / max(inflow.sum(), 1), -1, 1)),
        revenu_median=float(inflow.median()),
        revenu_moyen=float(inflow.mean()),
        tontine_ponctualite=float((t["retard_jours"] <= 3).mean()),
        tontine_retard_moyen=float(t["retard_jours"].mean()),
        intrants_ponctualite=float((i["retard_jours"] <= 0).mean()),
        intrants_retard_moyen=float(i["retard_jours"].mean()),
        intrants_volume=int(i["montant"].sum()),
        rendement_ratio=float(ratio.mean()),
        rendement_stabilite=float(1 - min(1, ratio.std() / max(ratio.mean(), 1e-6) * 3)),
        anciennete=p["anciennete"],
    )
    return f


def run(cid: str, p: dict) -> dict:
    raw = build_raw(cid, p)
    return {"raw": raw, "features": extract_features(raw, p)}
