# Game Programming Patterns - Édition Française

Bienvenue sur le dépôt de la traduction française non-officielle du livre de référence **Game Programming Patterns** écrit par Robert Nystrom.

Ce projet vise à rendre accessible aux développeurs francophones les concepts fondamentaux de l'architecture logicielle appliquée au développement de jeux vidéo.

## Le Livre Original

Ce travail est basé sur le contenu disponible gratuitement sur [gameprogrammingpatterns.com](https://gameprogrammingpatterns.com/).

> **Note importante :** Tout le crédit revient à **Robert Nystrom** pour la création de cet ouvrage exceptionnel. Si vous appréciez ce contenu, nous vous encourageons vivement à soutenir l'auteur original en achetant la version physique ou eBook officielle (en anglais).

## Guide d'Installation et d'Utilisation

Suivez ces étapes pour configurer votre environnement et générer le livre.

### 1. Prérequis

Assurez-vous d'avoir installé les logiciels suivants sur votre machine :

*   **Python 3.8+** : [Télécharger Python](https://www.python.org/downloads/)
*   **Git** : [Télécharger Git](https://git-scm.com/downloads)
*   **Ollama** : Nécessaire pour la traduction via IA locale. [Télécharger Ollama](https://ollama.com/)
*   **Pandoc** : Indispensable pour la conversion finale en EPUB. [Télécharger Pandoc](https://pandoc.org/installing.html)

> **Note :** Pour Pandoc, assurez-vous qu'il est bien ajouté à votre `PATH` système lors de l'installation.

### 2. Installation des Dépendances

Ouvrez votre terminal dans le dossier du projet et exécutez les commandes suivantes :

```bash
# (Optionnel) Créer un environnement virtuel pour isoler les paquets
python -m venv venv
# Activer l'environnement virtuel (Windows)
.\venv\Scripts\activate

# Installer les librairies Python requises
pip install -r requirements.txt
```

### 3. Configuration du Modèle IA

Le script de traduction utilise le modèle `qwen2.5:7b` via Ollama. 
Assurez-vous qu'Ollama est lancé, puis téléchargez le modèle (le script peut le faire automatiquement, mais il est préférable de le faire en amont) :

```bash
ollama pull qwen2.5:7b
```

### 4. Génération du Livre (Pas à Pas)

Le processus est divisé en 3 étapes automatisées.

#### Étape 1 : Récupération du contenu (Scraping)
Télécharge le contenu brut depuis le site officiel.
```bash
python 1_scrape_gpp.py
```

#### Étape 2 : Traduction
Traduit les fichiers Markdown récupérés. Cette étape peut prendre du temps selon la puissance de votre machine.
```bash
python 2_translate_gpp.py
```
*Options :* `python 2_translate_gpp.py --test` pour traduire uniquement le premier chapitre.

#### Étape 3 : Construction de l'EPUB
Assemble les fichiers traduits et génère le fichier final `.epub`.
```powershell
# D'abord, préparer la structure du livre
python 3_create_epub_builder_gpp.py

# Ensuite, lancer le script de génération (PowerShell)
.\build-epub.ps1
```

Une fois terminé, le fichier `game-programming-patterns-fr.epub` sera disponible à la racine du projet.

## Fonctionnalités du Projet

Ce repository met à disposition une suite d'outils Python conçus pour automatiser la création de cette édition française :

1.  **Extraction (Scraping)** : Récupération structurée du contenu depuis la source originale.
2.  **Traduction** : Processus de traduction ajusté pour conserver la précision technique et le style conversationnel de l'auteur.
3.  **Génération EPUB** : Compilation automatique des chapitres et des ressources pour produire un livre électronique de qualité professionnelle.

### Les Scripts

- `1_scrape_gpp.py` : Scrape le contenu du site original.
- `2_translate_gpp.py` : Gère la traduction des fichiers Markdown.
- `3_create_epub_builder_gpp.py` : Prépare la structure pour la génération du livre.
- `build-epub.ps1` : Script PowerShell pour l'assemblage final via Pandoc.

## ⚠️ Avertissement (Disclaimer)

**L'utilisation de ce logiciel est soumise aux conditions suivantes :**

Les scripts fournis dans ce dépôt sont destinés à un usage personnel et éducatif. 

**Je ne suis pas responsable de l'utilisation qui est faite de ces scripts.** 

Il incombe à l'utilisateur final de s'assurer qu'il respecte :
- Les droits de propriété intellectuelle.
- Les conditions d'utilisation (Term of Service) du site source.
- La charge serveur imposée lors de l'extraction des données (scraping).

## Contribuer

Les corrections, améliorations de traduction et optimisations de scripts sont les bienvenues. N'hésitez pas à ouvrir une *Issue* ou à proposer une *Pull Request*.

---
*Ce projet est une initiative communautaire et n'est pas affilié officiellement à l'auteur du livre.*
