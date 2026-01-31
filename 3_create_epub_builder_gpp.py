import os

# Configuration
BOOK_DIR = "book"
OUTPUT_SCRIPT = "build-epub.ps1"
EPUB_NAME = "game-programming-patterns-fr.epub"
METADATA_FILE = "metadata.yaml"

def find_french_files(root_dir):
    """
    Parcourt récursivement root_dir et trouve tous les fichiers finissant par -fr.md
    Retourne une liste de chemins relatifs.
    """
    french_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith("-fr.md"):
                # Construit le chemin relatif depuis le dossier racine du projet
                full_path = os.path.join(root, file)
                # Normalisation des séparateurs pour éviter les soucis sous Windows/PS
                relative_path = os.path.relpath(full_path, start=".")
                french_files.append(relative_path)
    return french_files

def sort_files(files):
    """
    Trie les fichiers de manière naturelle (I avant II, 01 avant 02, etc.)
    Ici, le tri alphabétique standard fonctionne bien grâce à la numérotation des dossiers
    (01-, 02-, etc.) et des sections (I-, II-, etc. => Attention I, II, III, IV, V est ok alphbétiquement ? 
    Non: I, II, III, IV, V, VI. 
    I-introduction
    II-design
    III-sequencing
    IV-behavioral
    V-decoupling
    VI-optimization
    
    Ordre alpha:
    I-introduction
    II-design...
    III-sequencing...
    IV-behavioral...
    V-decoupling...
    VI-optimization...
    
    C'est presque bon, sauf que V vient après IV en romain mais avant en alpha (V vs I).
    Wait: 'V' (86) vs 'I' (73). 'V' est après 'I'.
    Comparons 'I-' vs 'V-'. 'I' vient avant 'V'.
    Comparons 'IV-behavioral' vs 'V-decoupling'. 'I' (73) vs 'V' (86). I est avant V.
    Comparons 'VI-optimization' (VI) vs 'V-decoupling' (V-). 
    'V-' vs 'VI'. 'V' == 'V', '-' (45) vs 'I' (73). '-' est avant 'I'.
    Donc 'V-decoupling' viendra AVANT 'VI-optimization'.
    
    Il semble que la structure de nommage permette un tri alphabétique simple correct.
    Vérifions 'i-acknowledgements': minuscule, souvent à la fin ou au début selon le système (ASCII 'i' > 'Z'). 
    Mais le dossier s'appelle 'i-acknowledgements'.
    
    On va faire un tri simple pour commencer.
    """
    return sorted(files)

def generate_powershell_script(files):
    """
    Génère le contenu du script PowerShell
    """
    # Échappement des chemins pour PowerShell (guillemets)
    quoted_files = [f'"{f}"' for f in files]
    file_list_str = " `\n  ".join(quoted_files)
    
    script_content = f"""# Script généré automatiquement par 3_create_epub_builder_gpp.py
Write-Host "Démarrage de la conversion Pandoc..."

# Vérification de l'existence de Pandoc
if (-not (Get-Command pandoc -ErrorAction SilentlyContinue)) {{
    Write-Error "Pandoc n'est pas trouvé dans le PATH. Veuillez l'installer et redémarrer."
    exit 1
}}

$outputFile = "{EPUB_NAME}"

# Commande Pandoc
pandoc `
  --metadata-file="{METADATA_FILE}" `
  --toc `
  --toc-depth=2 `
  --resource-path=".:{BOOK_DIR}" `
  -o $outputFile `
  {file_list_str}

if (Test-Path $outputFile) {{
    $size = (Get-Item $outputFile).Length
    Write-Host "Succès ! EPUB généré : $outputFile ($size bytes)"
}} else {{
    Write-Error "Erreur : Le fichier EPUB n'a pas été généré."
}}
"""
    return script_content

def main():
    print(f"Recherche des fichiers dans '{BOOK_DIR}'...")
    if not os.path.exists(BOOK_DIR):
        print(f"Erreur: Le dossier '{BOOK_DIR}' n'existe pas.")
        return

    files = find_french_files(BOOK_DIR)
    
    if not files:
        print("Aucun fichier '-fr.md' trouvé !")
        return

    print(f"Trouvé {len(files)} fichiers traduits.")
    
    sorted_files = sort_files(files)
    
    # Affichage pour debug
    for f in sorted_files:
        print(f" - {f}")

    script_content = generate_powershell_script(sorted_files)
    
    with open(OUTPUT_SCRIPT, "w", encoding="utf-8") as f:
        f.write(script_content)
    
    print(f"\nScript de build généré : {OUTPUT_SCRIPT}")
    print("Exécutez-le avec PowerShell pour créer l'epub.")

if __name__ == "__main__":
    main()
