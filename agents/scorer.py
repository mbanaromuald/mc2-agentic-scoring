"""Agent 2 — Évaluateur de Risque : score de confiance 0-1000, adapté au contexte rural."""
import numpy as np
from core.llm import ask
from core.rag import retrieve

WEIGHTS = {
    "Flux Mobile Money": 0.25,
    "Discipline de tontine": 0.25,
    "Paiement des intrants": 0.20,
    "Performance des récoltes": 0.20,
    "Ancienneté & stabilité": 0.10,
}
MULT = {"A": 1.0, "B": 0.9, "C": 0.7, "D": 0.4, "E": 0.0}
DECISIONS = {
    "A": "APPROBATION RECOMMANDÉE",
    "B": "APPROBATION RECOMMANDÉE",
    "C": "APPROBATION CONDITIONNELLE",
    "D": "EXAMEN APPROFONDI DU COMITÉ",
    "E": "REFUS MOTIVÉ · ACCOMPAGNEMENT",
}


def _grade(s: int) -> str:
    return "A" if s >= 750 else "B" if s >= 650 else "C" if s >= 550 else "D" if s >= 450 else "E"


def components(f: dict) -> dict:
    c = {
        "Flux Mobile Money": 50 * f["mm_regularite"] + 30 * f["mm_mois_actifs"] / 12
                             + 20 * float(np.clip(f["mm_epargne"] / 0.25, 0, 1)),
        "Discipline de tontine": 80 * f["tontine_ponctualite"] + 20 * (1 - min(f["tontine_retard_moyen"] / 15, 1)),
        "Paiement des intrants": 80 * f["intrants_ponctualite"] + 20 * (1 - min(f["intrants_retard_moyen"] / 20, 1)),
        "Performance des récoltes": 70 * float(np.clip(f["rendement_ratio"] / 1.15, 0, 1)) + 30 * f["rendement_stabilite"],
        "Ancienneté & stabilité": 100 * min(f["anciennete"] / 8, 1),
    }
    return {k: round(float(v * 100 // 1) / 100, 1) for k, v in c.items()}


def run(p: dict, f: dict) -> dict:
    comp = components(f)
    weighted = sum(comp[k] * w for k, w in WEIGHTS.items())
    score = int(round(weighted * 10))
    grade = _grade(score)

    # Capacité de remboursement : 35 % du revenu médian, 12 mois, taux plat 1,5 %/mois
    mensualite_max = 0.35 * f["revenu_median"]
    principal_max = mensualite_max * 12 / (1 + 0.015 * 12)
    montant = min(p["demande"], principal_max * MULT[grade])
    montant = int(round(montant / 10_000) * 10_000)

    forces, alertes = [], []
    if f["tontine_ponctualite"] >= 0.8: forces.append(f"Tontine : {f['tontine_ponctualite']:.0%} de cotisations à temps")
    if f["intrants_ponctualite"] >= 0.8: forces.append(f"Intrants : {f['intrants_ponctualite']:.0%} de paiements à l'échéance")
    if f["rendement_ratio"] >= 1.0: forces.append(f"Rendements {f['rendement_ratio']:.0%} de la référence locale")
    if f["mm_mois_actifs"] >= 11: forces.append("Activité Mobile Money quasi continue sur 12 mois")
    if f["anciennete"] >= 5: forces.append(f"{f['anciennete']} ans d'expérience dans l'activité")
    if f["tontine_ponctualite"] < 0.6: alertes.append("Retards fréquents de cotisation en tontine")
    if f["intrants_ponctualite"] < 0.5: alertes.append("Retards récurrents envers les fournisseurs d'intrants")
    if f["rendement_ratio"] < 0.85: alertes.append("Rendements nettement sous la moyenne locale")
    if f["mm_mois_actifs"] < 9: alertes.append("Activité Mobile Money discontinue")
    if f["mm_epargne"] < 0.05: alertes.append("Capacité d'épargne quasi nulle")
    if f["anciennete"] < 2: alertes.append("Activité récente (moins de 2 ans)")
    if montant < p["demande"]: alertes.append(f"Montant réduit de {p['demande']:,} à {montant:,} FCFA".replace(",", " "))

    ctx = "\n".join(d.page_content for d in retrieve(f"grille décision grade {grade} capacité remboursement", k=2))
    facts = (f"Client: {p['nom']} ({p['activite']}). Score {score}/1000, grade {grade}. "
             f"Composantes (/100): {comp}. Forces: {forces}. Alertes: {alertes}.")
    txt, model = ask(
        "Tu es l'Agent Évaluateur de Risque de MC2, microfinance africaine. Rédige en français une "
        "justification claire et factuelle de 4 phrases maximum pour le comité de crédit. "
        "N'invente aucun chiffre. Utilise la politique fournie.\n\nPOLITIQUE:\n" + ctx,
        facts, max_tokens=300)
    if not txt:
        txt = (f"Le dossier obtient {score}/1000 (grade {grade}). "
               f"{'Points forts : ' + '; '.join(forces[:2]) + '. ' if forces else ''}"
               f"{'Vigilance : ' + '; '.join(alertes[:2]) + '. ' if alertes else ''}"
               f"Décision proposée : {DECISIONS[grade].lower()}.")
    return dict(score=score, grade=grade, decision=DECISIONS[grade], composantes=comp, poids=WEIGHTS,
                montant_recommande=montant, mensualite_max=int(mensualite_max), forces=forces,
                alertes=alertes, justification=txt, modele=model, politique=ctx)
