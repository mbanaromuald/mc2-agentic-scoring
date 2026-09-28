# Système Agentique de Credit Scoring Alternatif et de Conseil Rural

**MC2 · Groupe SAPA** — Projet conçu et réalisé par **Romuald MBANA MEDJO**

🔗 **Démo en ligne :** _à compléter après déploiement sur Streamlit Community Cloud_
📦 **Dépôt GitHub :** _à compléter_

Trois agents spécialisés transforment des données alternatives (Mobile Money, tontines, intrants, récoltes)
en score de confiance explicable, rapport de comité et ordre de décaissement validé par un humain.

## Déployer sur Streamlit Community Cloud

1. Poussez ce dépôt sur GitHub (voir `.gitignore` : `.env` n'est jamais commité).
2. Sur [share.streamlit.io](https://share.streamlit.io), **New app** → sélectionnez le dépôt, branche `main`, fichier `app.py`.
3. Dans **Advanced settings → Secrets**, collez :
   ```toml
   GROQ_API_KEY = "gsk_votre_cle"
   GROQ_MODEL = "llama-3.2-3b-preview"
   GROQ_FALLBACK_MODELS = "llama-3.1-8b-instant,llama-3.3-70b-versatile"
   ```
4. Déployez. Le fichier `requirements.txt` inclut `pysqlite3-binary`, et `app.py` bascule dessus automatiquement
   au démarrage : c'est nécessaire car ChromaDB exige un SQLite plus récent que celui de l'environnement Cloud.
   En local ou dans Docker, ce correctif est ignoré silencieusement si `pysqlite3` n'est pas installé.

## Lancer avec Docker
```bash
cp .env.example .env        # renseigner GROQ_API_KEY (gratuite : console.groq.com)
docker compose up --build   # puis ouvrir http://localhost:8501
```
Sans clé Groq, l'application fonctionne en mode déterministe (scoring + rapports modèles).

## Lancer sans Docker
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Architecture
| Couche | Fichier | Rôle |
|---|---|---|
| Agent 1 Collecteur | `agents/collector.py` | Extrait les indicateurs des données alternatives |
| Agent 2 Évaluateur | `agents/scorer.py` | Score 0-1000, grade A-E, capacité, décision, justification (RAG) |
| Agent 3 Clôture | `agents/closer.py` | Rapport comité, ordre banque mère, SMS |
| Orchestrateur | `agents/pipeline.py` | Enchaîne et trace les agents |
| RAG | `core/rag.py` | ChromaDB + LangChain sur `data/knowledge/` |
| LLM | `core/llm.py` | Llama via Groq (`langchain-groq`), modèles de secours |
| Données | `core/data.py` | Données synthétiques (à remplacer par les vrais connecteurs) |

## Passage en production
- Connecteurs API MTN MoMo / Orange Money, registre des tontines, fournisseurs d'intrants.
- Calibrage du score sur l'historique réel de remboursement de MC2 (régression logistique / gradient boosting).
- API réelle de la banque mère dans `execute_disbursement`.
- Embeddings sémantiques (HuggingFace) à la place des embeddings par hachage.
- Conformité : consentement du client, protection des données (RGPD / lois camerounaises), audit du biais.
