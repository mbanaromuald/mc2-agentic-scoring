"""Orchestrateur : enchaîne les trois agents et trace chaque étape."""
import time
from agents import collector, scorer, closer


def run_pipeline(cid: str, profile: dict, on_step=None) -> dict:
    trace = []

    def step(agent, action, fn):
        t = time.time()
        out = fn()
        ms = int((time.time() - t) * 1000)
        trace.append({"Agent": agent, "Action": action, "Durée (ms)": ms})
        if on_step:
            on_step(agent, action, ms)
        return out

    col = step("Collecteur", "Ingestion et normalisation des données alternatives", lambda: collector.run(cid, profile))
    sc = step("Évaluateur", "Scoring pondéré + politique MC2 (RAG ChromaDB)", lambda: scorer.run(profile, col["features"]))
    cl = step("Clôture", "Rapport comité + ordre de décaissement + notification", lambda: closer.run(cid, profile, col["features"], sc))
    return {"collector": col, "scoring": sc, "closing": cl, "trace": trace}
