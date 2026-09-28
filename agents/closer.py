"""Agent 3 — Clôture & Notification : rapport comité, ordre de décaissement, SMS bénéficiaire."""
import uuid
from datetime import date
from core.llm import ask
from core.rag import retrieve

fcfa = lambda x: f"{int(x):,}".replace(",", " ") + " FCFA"


def run(cid: str, p: dict, f: dict, s: dict) -> dict:
    conseils = "\n".join(d.page_content for d in retrieve(f"conseils {p['culture']} {p['activite']} épargne", k=3))
    facts = (f"Client {p['nom']}, {p['activite']}, {p['localite']}, {p['surface_ha']} ha. Objet: {p['objet']}. "
             f"Score {s['score']}/1000 grade {s['grade']}. Décision: {s['decision']}. Forces: {s['forces']}. "
             f"Alertes: {s['alertes']}. Montant recommandé: {fcfa(s['montant_recommande'])}.")
    narratif, model = ask(
        "Tu es l'Agent de Clôture de MC2. Rédige en français, en Markdown, deux sections courtes : "
        "'### Recommandation au comité' (3 phrases, conditions de suivi incluses) et "
        "'### Conseils d'accompagnement' (3 puces basées UNIQUEMENT sur les conseils fournis). "
        "N'invente aucun chiffre.\n\nCONSEILS:\n" + conseils, facts, temperature=0.3, max_tokens=500)
    if not narratif:
        cond = {"A": "Suivi standard à 30 jours.", "B": "Suivi standard à 30 jours.",
                "C": "Caution solidaire et suivi mensuel obligatoires.",
                "D": "Visite terrain et garantie renforcée avant toute décision.",
                "E": "Orienter vers un parcours d'épargne et d'accompagnement."}[s["grade"]]
        narratif = (f"### Recommandation au comité\n{s['justification']} {cond}\n\n"
                    f"### Conseils d'accompagnement\n" + "\n".join("- " + l.strip() for l in conseils.split("\n")
                                                                  if l.strip() and not l.startswith("#"))[:600])

    ref = f"MC2-{date.today():%Y%m%d}-{cid}"
    tableau = "\n".join([
        "| Indicateur | Valeur |", "|---|---|",
        f"| Score de confiance | **{s['score']} / 1000 (grade {s['grade']})** |",
        f"| Décision proposée | {s['decision']} |",
        f"| Montant demandé | {fcfa(p['demande'])} |",
        f"| Montant recommandé | **{fcfa(s['montant_recommande'])}** |",
        f"| Mensualité maximale supportable | {fcfa(s['mensualite_max'])} |",
        f"| Revenu mensuel médian (Mobile Money) | {fcfa(f['revenu_median'])} |",
        f"| Ponctualité tontine / intrants | {f['tontine_ponctualite']:.0%} / {f['intrants_ponctualite']:.0%} |",
        f"| Rendement vs référence locale | {f['rendement_ratio']:.0%} |"])
    rapport = (f"# Dossier {ref} — {p['nom']}\n\n**Activité :** {p['activite']} · {p['localite']}  \n"
               f"**Objet du crédit :** {p['objet']}\n\n{tableau}\n\n"
               f"### Analyse du risque\n{s['justification']}\n\n{narratif}\n\n"
               f"---\n*Rapport généré par le système agentique MC2 — aide à la décision, "
               f"la décision finale appartient au comité de crédit.*")

    ordre = dict(reference=ref, beneficiaire=p["nom"], montant_fcfa=s["montant_recommande"],
                 canal=p["operateur"], source="Banque mère — compte de refinancement MC2",
                 fournisseur_direct="Paiement direct aux fournisseurs d'intrants recommandé",
                 statut="EN ATTENTE DE VALIDATION DU COMITÉ",
                 autorise=s["grade"] != "E" and s["montant_recommande"] > 0)
    sms = (f"MC2 : Bonjour {p['nom'].split()[0]}, votre demande de {fcfa(p['demande'])} a été étudiée. "
           + (f"Accord de principe pour {fcfa(s['montant_recommande'])}. Passez à l'agence pour finaliser."
              if ordre["autorise"] else "Nous vous proposons un accompagnement avant un nouvel examen. Passez à l'agence."))
    return dict(rapport=rapport, ordre=ordre, sms=sms, modele=model, conseils=conseils)


def execute_disbursement(ordre: dict) -> dict:
    """SIMULATION de l'appel API vers la banque mère (à remplacer par l'API réelle)."""
    return {**ordre, "statut": "DÉCAISSÉ (simulation)", "transaction_id": "TX" + uuid.uuid4().hex[:10].upper(),
            "horodatage": date.today().isoformat()}
