# Système Agentique de Credit Scoring Alternatif et de Conseil Rural

**MC2 · Groupe SAPA** — Projet conçu et réalisé par **Romuald MBANA MEDJO**

Trois agents spécialisés transforment des données alternatives (Mobile Money, tontines, intrants, récoltes)
en score de confiance explicable, rapport de comité et ordre de décaissement validé par un humain.

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
