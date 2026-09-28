# Système Agentique de Credit Scoring Alternatif et de Conseil Rural

<<<<<<< HEAD
=======
<<<<<<< HEAD
**MC2 · Groupe SAPA (Société Africaine de Participation)**
Projet conçu et réalisé par **Romuald MBANA MEDJO**

🔗 **Tester l'application en ligne :** **[mc2-agentic-scoring.streamlit.app](https://mc2-agentic-scoring-86fpsvp6vqjmdycwwyxujt.streamlit.app/)**
📦 **Dépôt GitHub :** _à compléter_

> Trois agents d'intelligence artificielle transforment les traces de la vie économique rurale — Mobile
> Money, tontines, paiements d'intrants agricoles, rendements de récolte — en un score de confiance
> explicable, un rapport d'aide à la décision et un ordre de décaissement, sans jamais retirer au comité
> de crédit le dernier mot.

---

## Sommaire
1. [Contexte et problème traité](#1-contexte-et-problème-traité)
2. [Description approfondie du projet](#2-description-approfondie-du-projet)
3. [Avantages pour MC2 et la microfinance](#3-avantages-pour-mc2-et-la-microfinance)
4. [Limites actuelles](#4-limites-actuelles)
5. [Perspectives d'évolution](#5-perspectives-dévolution)
6. [Installation et déploiement](#6-installation-et-déploiement)
7. [Architecture technique](#7-architecture-technique)

---

## 1. Contexte et problème traité

MC2 est une institution de microfinance du groupe SAPA implantée en zone rurale africaine. Sa clientèle
naturelle — petits agriculteurs, transformatrices, commerçants vivriers — porte un risque de crédit réel
mais **invisible aux méthodes classiques d'évaluation** : pas de bilan comptable, pas de fiches de paie,
pas d'historique bancaire formel. Deux conséquences concrètes en découlent :

- **Des dossiers instruits lentement**, faute de données exploitables, ce qui allonge le délai entre la
  demande et le décaissement — souvent incompatible avec un calendrier agricole.
- **Des refus par défaut** plutôt que par analyse, qui écartent des emprunteurs en réalité disciplinés,
  simplement parce que leur discipline s'exprime ailleurs que dans un relevé bancaire : la régularité
  d'une tontine, la ponctualité envers un fournisseur d'intrants, un rendement stable saison après saison.

Le projet part d'un constat simple : **ces signaux existent déjà**, dispersés dans les usages numériques
et communautaires locaux. Le problème n'est pas l'absence de données, mais l'absence d'un système capable
de les collecter, de les interpréter avec la bonne grille de lecture rurale, et d'en tirer une décision
traçable.

## 2. Description approfondie du projet

Le système repose sur une **architecture agentique à trois agents spécialisés**, orchestrés en pipeline
séquentiel, chacun avec une responsabilité unique et un contrat d'entrée/sortie clair — plutôt qu'un
modèle monolithique qui masquerait la logique de décision.

### Agent 1 — Collecteur & Analyse de Données Alternatives
Il ingère quatre familles de données comportementales et les normalise en indicateurs numériques
exploitables par le scoring :
- **Mobile Money (MTN MoMo / Orange Money)** : régularité des flux, nombre de mois actifs, capacité
  d'épargne résiduelle, revenu médian mensuel (la médiane plutôt que la moyenne, pour absorber la
  saisonnalité agricole sans la lisser artificiellement).
- **Tontines associatives** : taux de ponctualité des cotisations, retard moyen — un proxy puissant de
  fiabilité dans un contexte où l'engagement communautaire vaut souvent plus qu'une garantie matérielle.
- **Historique de paiement des intrants agricoles** : ponctualité envers les fournisseurs (semences,
  engrais, matériel), volume d'achats sur la période.
- **Données de récolte locales** : rendement par hectare rapporté à une référence locale par culture
  (cacao, café, tomate, manioc, plantain), et stabilité de ce rendement d'une saison à l'autre.

### Agent 2 — Évaluateur de Risque (Scoring)
À partir des indicateurs produits par l'agent 1, il calcule un **score de confiance sur 1000 points**,
décomposé en cinq composantes pondérées (flux Mobile Money, discipline de tontine, paiement des
intrants, performance des récoltes, ancienneté), converti en grade A à E selon la grille de décision de
la politique de crédit MC2. Il calcule ensuite la **capacité de remboursement réelle** — 35 % du revenu
médian mensuel — pour plafonner le montant recommandé indépendamment du montant demandé, et rédige une
justification en langage naturel ancrée dans les documents de politique interne via une recherche
augmentée (RAG) sur une base vectorielle ChromaDB. Rien n'est laissé à l'improvisation du modèle de
langage : chaque chiffre affiché est calculé par du code déterministe, le LLM ne fait que le mettre en
mots.

### Agent 3 — Clôture & Notification
Il transforme la décision de l'agent 2 en trois livrables opérationnels : un **rapport d'aide à la
décision** au format lisible par le comité de crédit (avec conseils d'accompagnement contextualisés,
puisés dans une base de bonnes pratiques agricoles), un **ordre de décaissement** structuré prêt à être
transmis à la banque mère, et un **SMS de notification** pour le bénéficiaire. Le décaissement n'est
exécuté qu'après validation explicite et cochée du comité de crédit dans l'interface — l'agent prépare
la décision, il ne la prend jamais à la place de l'humain.

### Interface et orchestration
Une interface Streamlit présente le pipeline de bout en bout : sélection d'un dossier réel ou simulation
d'un profil sur mesure, exécution tracée des trois agents avec horodatage de chaque étape, visualisation
de la jauge de score et du radar des composantes, flux Mobile Money sur douze mois, rapport téléchargeable,
et un module de conseil rural conversationnel adossé à la même base ChromaDB. L'ensemble s'exécute avec
ou sans clé d'API : en l'absence de connexion à Llama via Groq, le système reste pleinement fonctionnel en
mode déterministe, ce qui garantit la continuité du service en zone à connectivité limitée.

## 3. Avantages pour MC2 et la microfinance

- **Accélération de l'instruction des dossiers.** Ce qui prenait des jours de collecte manuelle et de
  vérification devient un pipeline de quelques secondes, sans dégrader la rigueur de l'analyse.
- **Inclusion financière élargie sans relâchement du risque.** Des emprunteurs aujourd'hui exclus faute
  de dossier formel deviennent évaluables sur la base de comportements réels et vérifiables — la
  promesse d'inclusion ne se paie pas d'une moindre maîtrise du risque.
- **Décision explicable et auditable.** Chaque score se décompose en composantes pondérées traçables
  jusqu'à la donnée source ; aucun chiffre n'est une boîte noire, ce qui facilite la conformité, la
  formation des agents de crédit et la défense du dossier devant un organe de contrôle.
- **Gouvernance humaine préservée.** L'automatisation s'arrête à la recommandation : le comité de crédit
  valide, et le décaissement ne part qu'après cette validation explicite — une architecture pensée pour
  rassurer un conseil d'administration, pas pour le contourner.
- **Capacité de remboursement calculée sur le réel, pas sur le déclaratif.** Le plafonnement à partir du
  revenu médian évite le surendettement structurel, un risque particulièrement élevé chez des emprunteurs
  à revenus saisonniers.
- **Effet d'apprentissage pour l'emprunteur.** Le module de conseil rural transforme chaque interaction en
  occasion d'orienter le bénéficiaire vers de meilleures pratiques agricoles et financières, ce qui
  améliore son profil de risque pour les cycles de financement suivants — un cercle vertueux plutôt qu'une
  relation purement transactionnelle.
- **Cohérence avec la stratégie du groupe SAPA.** Le projet numérise les *Compétences* pour optimiser les
  *Moyens* : il ne remplace pas l'expertise du comité de crédit, il la rend plus rapide et mieux informée.

## 4. Limites actuelles

Ce projet est un **prototype de démonstration**, construit pour illustrer une architecture et une
méthode, pas pour un déploiement en production en l'état. Les limites suivantes doivent être présentées
sans détour :

- **Données synthétiques.** Les profils et l'historique Mobile Money, tontine, intrants et récoltes sont
  générés artificiellement (`core/data.py`). Aucune donnée réelle de client MC2 n'est utilisée.
- **Pondérations non calibrées statistiquement.** Les poids des cinq composantes du score sont fixés par
  jugement métier, pas par régression sur un historique réel de remboursement. Ils doivent être validés
  ou réajustés avec des données réelles avant toute utilisation en conditions réelles.
- **Absence de connecteurs aux systèmes réels.** Aucune intégration n'existe aujourd'hui avec les API
  MTN Mobile Money ou Orange Money, un registre numérique de tontines, ou le système d'information de la
  banque mère : le décaissement est simulé.
- **Embeddings simplifiés.** La recherche augmentée utilise un embedding local par hachage pour garantir
  un fonctionnement hors-ligne et sans dépendance réseau lourde ; il capture moins bien la proximité
  sémantique qu'un modèle d'embeddings entraîné.
- **Dépendance à un fournisseur LLM externe.** Le raisonnement en langage naturel repose sur l'API Groq ;
  la continuité de service dépend de sa disponibilité et de ses quotas, même si un mode dégradé sans LLM
  existe.
- **Absence de cadre de conformité et de protection des données.** Aucun mécanisme de consentement, de
  chiffrement des données personnelles ou d'audit du biais algorithmique n'est implémenté à ce stade.
- **Non testé à l'échelle.** Le système n'a pas été éprouvé sur un volume réel de dossiers ni sur la
  diversité effective des cultures, zones climatiques et pratiques financières couvertes par MC2.

## 5. Perspectives d'évolution

- **Calibrage du score sur données réelles.** Remplacer les pondérations empiriques par un modèle
  supervisé (régression logistique ou gradient boosting) entraîné sur l'historique effectif de
  remboursement de MC2, avec un contrôle continu de la dérive du modèle dans le temps.
- **Connecteurs de production.** Intégrer les API officielles MTN Mobile Money et Orange Money, un
  registre numérique de tontines lorsqu'il existe, les systèmes des fournisseurs d'intrants partenaires,
  et l'API réelle de décaissement de la banque mère.
- **Renforcement de la donnée agricole.** Croiser les rendements déclarés avec des sources externes
  (données météorologiques, imagerie satellite ou indices de végétation) pour objectiver la performance
  des récoltes indépendamment des déclarations de l'emprunteur.
- **Cadre de conformité et d'équité.** Mettre en place le recueil du consentement, le chiffrement des
  données sensibles, une politique de conservation conforme à la réglementation camerounaise et
  régionale, ainsi qu'un audit régulier du biais algorithmique par genre, région et type de culture.
- **Embeddings sémantiques et base de connaissances élargie.** Passer à des embeddings entraînés (par
  exemple des modèles multilingues incluant le français et les langues locales), et enrichir la base
  ChromaDB avec l'ensemble des politiques internes de MC2 et un référentiel agronomique plus complet.
- **Boucle de rétroaction.** Réinjecter les décisions effectives du comité de crédit et les performances
  réelles de remboursement pour améliorer continuellement le scoring et les recommandations de conseil.
- **Extension multicanal.** Rendre le conseiller rural accessible par SMS ou par une messagerie vocale
  interactive, afin de toucher les bénéficiaires ne disposant pas d'un accès internet régulier.
- **Passage à l'échelle multi-agences.** Généraliser le système à l'ensemble du réseau MC2, avec un
  tableau de bord de pilotage à l'usage de la direction des risques du groupe SAPA.

## 6. Installation et déploiement

### Tester en ligne
L'application est déployée sur Streamlit Community Cloud et accessible sans installation :
**[mc2-agentic-scoring.streamlit.app](https://mc2-agentic-scoring-86fpsvp6vqjmdycwwyxujt.streamlit.app/)**

### Déployer sa propre instance sur Streamlit Community Cloud
1. Poussez ce dépôt sur GitHub (voir `.gitignore` : `.env` n'est jamais commité).
2. Sur [share.streamlit.io](https://share.streamlit.io), **New app** → sélectionnez le dépôt, branche
   `main`, fichier `app.py`.
3. Dans **Advanced settings → Secrets**, renseignez :
   ```toml
   GROQ_API_KEY = "gsk_votre_cle"
   GROQ_MODEL = "llama-3.2-3b-preview"
   GROQ_FALLBACK_MODELS = "llama-3.1-8b-instant,llama-3.3-70b-versatile"
   ```
4. Déployez. Le fichier `requirements.txt` inclut `pysqlite3-binary`, et `app.py` bascule dessus
   automatiquement au démarrage : c'est nécessaire car ChromaDB exige un SQLite plus récent que celui
   de l'environnement Cloud. En local ou dans Docker, ce correctif est ignoré silencieusement si
   `pysqlite3` n'est pas installé.

### Lancer avec Docker
=======
>>>>>>> efb9db474e7a81260356fba083a9579f229834e2
**MC2 · Groupe SAPA** — Projet conçu et réalisé par **Romuald MBANA MEDJO**

Trois agents spécialisés transforment des données alternatives (Mobile Money, tontines, intrants, récoltes)
en score de confiance explicable, rapport de comité et ordre de décaissement validé par un humain.

## Lancer avec Docker
<<<<<<< HEAD
=======
>>>>>>> a06c9023fba643c4cb12587010ba021eb20b7d9e
>>>>>>> efb9db474e7a81260356fba083a9579f229834e2
```bash
cp .env.example .env        # renseigner GROQ_API_KEY (gratuite : console.groq.com)
docker compose up --build   # puis ouvrir http://localhost:8501
```
<<<<<<< HEAD
Sans clé Groq, l'application fonctionne en mode déterministe (scoring + rapports modèles).

## Lancer sans Docker
=======
<<<<<<< HEAD
Sans clé Groq, l'application fonctionne en mode déterministe (scoring et rapports générés sans LLM).

### Lancer sans Docker
=======
Sans clé Groq, l'application fonctionne en mode déterministe (scoring + rapports modèles).

## Lancer sans Docker
>>>>>>> a06c9023fba643c4cb12587010ba021eb20b7d9e
>>>>>>> efb9db474e7a81260356fba083a9579f229834e2
```bash
pip install -r requirements.txt
streamlit run app.py
```

<<<<<<< HEAD
=======
<<<<<<< HEAD
## 7. Architecture technique

| Couche | Fichier | Rôle |
|---|---|---|
| Agent 1 — Collecteur | `agents/collector.py` | Extrait les indicateurs des données alternatives |
| Agent 2 — Évaluateur | `agents/scorer.py` | Score 0-1000, grade A-E, capacité, décision, justification (RAG) |
| Agent 3 — Clôture | `agents/closer.py` | Rapport comité, ordre banque mère, notification SMS |
| Orchestrateur | `agents/pipeline.py` | Enchaîne et trace l'exécution des trois agents |
| RAG | `core/rag.py` | ChromaDB + LangChain sur les documents de `data/knowledge/` |
| LLM | `core/llm.py` | Llama via Groq (`langchain-groq`), avec bascule automatique sur des modèles de secours |
| Données | `core/data.py` | Données synthétiques de démonstration, à remplacer par les connecteurs réels |
| Interface | `app.py` | Application Streamlit : pipeline, visualisations, rapport, conseiller rural |

**Stack :** Streamlit · Llama 3.2 (via Groq) · ChromaDB · LangChain · Docker.

---

*Projet présenté à SAPA pour MC2 par **Romuald MBANA MEDJO** — système d'aide à la décision ; la
décision finale d'octroi de crédit appartient dans tous les cas au comité de crédit de MC2.*
=======
>>>>>>> efb9db474e7a81260356fba083a9579f229834e2
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
<<<<<<< HEAD
=======
>>>>>>> a06c9023fba643c4cb12587010ba021eb20b7d9e
>>>>>>> efb9db474e7a81260356fba083a9579f229834e2
