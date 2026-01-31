import os
import time
import re
import argparse
from typing import List, Dict, Optional
import ollama

# --- CONFIGURATION ---

MODEL_NAME = "qwen2.5:7b"
OUTPUT_DIR = "book"

# Paramètres du modèle pour favoriser la cohérence mais garder de la fluidité
MODEL_OPTIONS = {
    "temperature": 0.3,
    "top_p": 0.9,
    "num_ctx": 8192,
    "repeat_penalty": 1.1,
}

# Glossaire pour assurer la cohérence terminologique
GLOSSARY = {
    # Termes à NE PAS traduire (garder en anglais pour le jargon dev)
    "do_not_translate": [
        "Design Pattern", "Pattern", "patterns", "Singleton", "Flyweight", "Observer", "Prototype",
        "Command", "State", "Double Buffer", "Game Loop", "Bytecode",
        "Component", "Event Queue", "Service Locator", "Object Pool",
        "Dirty Flag", "Spatial Partition", "Subclass Sandbox", "Type Object",
        "Update Method", "Data Locality", "Sequencing Patterns", "Behavioral Patterns",
        "Decoupling Patterns", "Optimization Patterns",
        "Runtime", "Overhead", "Buffer", "Socket", "Framework", "Template", "Inline"
    ],
    "translations": {
        "decoupling": "découplage",
        "architecture": "architecture",
        "abstraction": "abstraction",
        "codebase": "base de code",
        "trade-off": "compromis",
        "flexibility": "flexibilité",
        "maintainability": "maintenabilité",
        "coupling": "couplage",
        # Suppression de "pattern" -> "patron" et autres termes devenus DNT
    }
}

SYSTEM_PROMPT_TEMPLATE = """Tu es un traducteur technique expert spécialisé dans les livres de programmation de jeux vidéo.

## TÂCHE
Traduire le contenu Markdown fourni de l'anglais vers le français.

## RÈGLES DE TRADUCTION STRICTES

### 1. Terminologie & Style "Développeur"
- **NE PAS TRADUIRE** les termes techniques standards (garder en anglais). Ex: *Pattern, Runtime, Overhead, Design Pattern, Thread, Buffer...*
- Utilise le **jargon naturel des développeurs francophones** (le "franglais" technique est accepté et encouragé quand il est plus précis/courant que le français académique).
  - *Bon:* "Ce pattern a un overhead important au runtime."
  - *Mauvais:* "Ce patron a une surcharge importante lors de l'exécution."

- **Termes Spécifiques à NE PAS traduire** :
  {do_not_translate}
  
- **Traductions Imposées** :
  {translations}

### 2. Contenu Technique & Code
- **NE JAMAIS** traduire le contenu des blocs de code (entre ``` ou `).
- **NE JAMAIS** traduire les noms de variables, fonctions, classes ou fichiers.
- **NE JAMAIS** modifier les liens Markdown [texte](url) ou les images ![alt](path).

### 3. Ton
- Le ton doit être professionnel mais conversationnel, reflétant l'humour subtil de l'auteur.
- Utilise le **vouvoiement** ("vous").
- La traduction doit être fluide.

### 4. Contexte Précédent
Voici un résumé des chapitres précédents pour maintenir la cohérence narrative :
{context_summary}

## FORMAT DE SORTIE
Retourne UNIQUEMENT le texte traduit au format Markdown. Ne pas ajouter de commentaires avant ou après.
"""

# --- FONCTIONS UTILITAIRES ---

def setup_model():
    """Vérifie si le modèle est disponible, sinon tente de le télécharger."""
    try:
        print(f"[INIT] Vérification du modèle {MODEL_NAME}...")
        ollama.show(MODEL_NAME)
        print(f"[INIT] Modèle {MODEL_NAME} trouvé.")
    except ollama.ResponseError:
        print(f"[INIT] Modèle {MODEL_NAME} non trouvé. Tentative de téléchargement (cela peut prendre du temps)...")
        try:
            ollama.pull(MODEL_NAME)
            print(f"[INIT] Modèle {MODEL_NAME} téléchargé avec succès.")
        except Exception as e:
            print(f"[ERREUR] Impossible de télécharger le modèle : {e}")
            exit(1)

def build_system_prompt(context_summary: str) -> str:
    """Construit le prompt système dynamique avec le glossaire et le contexte."""
    dnt_list = ", ".join(GLOSSARY["do_not_translate"])
    trans_list = "\n  ".join([f"- {k} -> {v}" for k, v in GLOSSARY["translations"].items()])
    
    return SYSTEM_PROMPT_TEMPLATE.format(
        do_not_translate=dnt_list,
        translations=trans_list,
        context_summary=context_summary if context_summary else "Aucun contexte précédent."
    )

def chunk_markdown(content: str, max_chunk_size: int = 2500) -> List[str]:
    """
    Découpe le markdown en morceaux gérables tout en préservant l'intégrité des blocs de code.
    Evite de couper au milieu d'une phrase.
    """
    chunks = []
    lines = content.split('\n')
    current_chunk = []
    current_size = 0
    in_code_block = False
    
    for line in lines:
        # Détection basique de bloc de code
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
        
        line_len = len(line) + 1 # +1 pour le saut de ligne
        
        # Si on dépasse la taille max et qu'on n'est pas dans un bloc de code
        if current_size + line_len > max_chunk_size and not in_code_block:
            # On essaie de couper à un endroit propice (fin de paragraphe, ou au moins pas en plein milieu d'un truc bizarre)
            # Ici on coupe simplement à la ligne si ce n'est pas du code.
            chunks.append('\n'.join(current_chunk))
            current_chunk = [line]
            current_size = line_len
        else:
            current_chunk.append(line)
            current_size += line_len
            
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
        
    return chunks

def translate_chunk(chunk: str, system_prompt: str, retries: int = 3) -> str:
    """Traduit un morceau de texte avec gestion d'erreurs."""
    if not chunk.strip():
        return chunk
        
    for attempt in range(retries):
        try:
            response = ollama.generate(
                model=MODEL_NAME,
                prompt=chunk,
                system=system_prompt,
                options=MODEL_OPTIONS,
                stream=False
            )
            return response['response']
        except Exception as e:
            print(f"  [ERREUR] Tentative {attempt+1}/{retries} échouée : {e}")
            time.sleep(2 * (attempt + 1))
            
    print("  [ECHEC] Impossible de traduire ce bloc après plusieurs tentatives.")
    return chunk # On retourne l'original en cas d'échec total pour ne pas tout perdre

def extract_summary(translated_content: str) -> str:
    """Crée un bref résumé du contenu traduit pour le contexte suivant."""
    # Pour simplifier, on prend les 500 premiers caractères qui ne sont pas du code
    # Dans une version avancée, on pourrait demander à l'LLM de résumer le chapitre.
    clean_text = re.sub(r'```[\s\S]*?```', '', translated_content)
    return clean_text[:500].replace('\n', ' ') + "..."

def get_markdown_files(root_dir: str) -> List[str]:
    """Récupère récursivement tous les fichiers .md (sauf README et _fr)."""
    md_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".md") and not file.endswith("_fr.md") and file != "README.md":
                md_files.append(os.path.join(root, file))
    # Tri simple pour essayer de suivre l'ordre (basé sur les noms de dossiers numérotés)
    md_files.sort()
    return md_files

def main():
    parser = argparse.ArgumentParser(description="Traducteur GPP via Ollama")
    parser.add_argument("--test", action="store_true", help="Traduit seulement le premier chapitre trouvé pour tester")
    parser.add_argument("--file", type=str, help="Traduit un fichier spécifique")
    args = parser.parse_args()

    setup_model()
    
    files_to_process = []
    if args.file:
        files_to_process = [args.file]
    else:
        files_to_process = get_markdown_files(OUTPUT_DIR)
        
    if not files_to_process:
        print("[INFO] Aucun fichier markdown trouvé à traduire.")
        return

    print(f"[INFO] {len(files_to_process)} fichiers à traduire.")

    global_context = "" 
    
    for i, file_path in enumerate(files_to_process):
        rel_path = os.path.relpath(file_path, OUTPUT_DIR)
        print(f"\n[{i+1}/{len(files_to_process)}] Traduction de : {rel_path}")
        
        # Vérifier si déjà traduit
        output_path = file_path.replace(".md", "_fr.md")
        if os.path.exists(output_path) and not args.file:
            print(f"  [SKIP] Fichier déjà traduit : {output_path}")
            # On charge quand même un bout de contexte pour la suite ? 
            # Pour l'instant on skip juste pour aller vite.
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        chunks = chunk_markdown(content)
        print(f"  -> Découpé en {len(chunks)} blocs.")
        
        translated_chunks = []
        system_prompt = build_system_prompt(global_context)
        
        for j, chunk in enumerate(chunks):
            print(f"  -> Traduction bloc {j+1}/{len(chunks)} ({len(chunk)} chars)...", end="", flush=True)
            t_start = time.time()
            trans = translate_chunk(chunk, system_prompt)
            translated_chunks.append(trans)
            print(f" Fait en {time.time()-t_start:.1f}s")
            
        full_translation = "\n\n".join(translated_chunks)
        
        # Sauvegarde
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_translation)
        print(f"  [OK] Sauvegardé dans : {output_path}")
        
        # Mise à jour du contexte pour le chapitre suivant
        # On ajoute un résumé de ce chapitre au contexte global
        chapter_summary = extract_summary(full_translation)
        global_context = f"Dernier chapitre traduit ({rel_path}): {chapter_summary}"
        
        if args.test:
            print("[TEST] Fin du test après un chapitre.")
            break

if __name__ == "__main__":
    main()
