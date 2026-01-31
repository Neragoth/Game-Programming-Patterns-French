import os
import requests
import re
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional, Any

# CONSTANTES
BASE_URL = "https://gameprogrammingpatterns.com/"
CONTENTS_URL = urljoin(BASE_URL, "contents.html")
OUTPUT_DIR = "book"

def setup_directories() -> None:
    """Crée le répertoire racine du livre s'il n'existe pas."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"[INFO] Dossier de sortie initialisé : {os.path.abspath(OUTPUT_DIR)}")

def get_soup(url: str) -> Optional[BeautifulSoup]:
    """Récupère le contenu HTML d'une URL et retourne un objet BeautifulSoup."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"[ERREUR] Impossible de récupérer {url} : {e}")
        return None

def int_to_roman(n: int) -> str:
    """Convertit un entier en chiffres romains (majuscules)."""
    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    syb = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
    roman_num = ''
    i = 0
    while n > 0:
        for _ in range(n // val[i]):
            roman_num += syb[i]
            n -= val[i]
        i += 1
    return roman_num

def slugify_name(name: str) -> str:
    """Transforme une chaîne en slug utilisable comme nom de fichier/dossier."""
    name = name.lower()
    # Supprimer les préfixes de type "I. ", "1. ", "i. "
    name = re.sub(r'^[ivx0-9]+\.\s*', '', name)
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[-\s]+', '-', name)
    return name.strip('-')

def get_toc_structure() -> List[Dict]:
    """
    Analyse la page TOC et extrait une structure hiérarchique.
    Utilise une liste de sections connues car les numéros romains sont en CSS.
    """
    print(f"[INFO] Analyse hiérarchique de la table des matières : {CONTENTS_URL}")
    soup = get_soup(CONTENTS_URL)
    if not soup: return []

    structure = []
    content_div = soup.find('div', class_='content') or soup.find('div', id='content') or soup.body
    if not content_div: return []

    # Acknowledgements (Lien spécial)
    ack_link = content_div.find('a', href=re.compile(r'acknowledgements\.html'))
    if ack_link:
        structure.append({
            "type": "preface",
            "title": "Acknowledgements",
            "url": urljoin(BASE_URL, ack_link['href']),
            "roman": "i"
        })

    # Liste des sections dans l'ordre de l'image
    sections_names = [
        "Introduction",
        "Design Patterns Revisited",
        "Sequencing Patterns",
        "Behavioral Patterns",
        "Decoupling Patterns",
        "Optimization Patterns"
    ]

    current_section = None
    chapter_idx = 0
    section_idx = 0
    seen_urls = set()

    ignore_patterns = ["About The Book", "Contents", "Next Chapter", "Previous Chapter", "Table of Contents", "Acknowledgements"]

    all_links = content_div.find_all('a')
    for a in all_links:
        text = a.get_text(strip=True).replace('\xa0', ' ')
        url = urljoin(BASE_URL, a['href'])
        
        if not text or any(p in text for p in ignore_patterns): continue
        if url in seen_urls: continue
        if "contents.html" in url: continue

        # Détection Section par nom exact
        if text in sections_names:
            section_idx += 1
            current_section = {
                "type": "section",
                "title": text,
                "roman": int_to_roman(section_idx),
                "chapters": []
            }
            structure.append(current_section)
            seen_urls.add(url)
            print(f"  [DÉTECTION] Section : {current_section['roman']}. {text}")
            continue

        # Détection Chapitre
        if current_section:
            chapter_idx += 1
            current_section["chapters"].append({
                "num": chapter_idx,
                "title": text,
                "url": url
            })
            seen_urls.add(url)
            print(f"  [DÉTECTION] Chapitre : {chapter_idx}. {text}")

    return structure

def download_image(img_url: str, save_dir: str) -> Optional[str]:
    """Télécharge une image et retourne son nom local."""
    try:
        full_img_url = urljoin(BASE_URL, img_url)
        filename = os.path.basename(urlparse(full_img_url).path).split('?')[0]
        if not filename: return None

        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, filename)
        
        if not os.path.exists(save_path):
            resp = requests.get(full_img_url, stream=True)
            if resp.status_code == 200:
                with open(save_path, 'wb') as f:
                    for chunk in resp.iter_content(1024): f.write(chunk)
            else: return None
        return filename
    except Exception as e:
        print(f"      [ERREUR IMG] {e}")
        return None

def process_page(url: str, save_dir: str, title: str) -> str:
    """Scrape une page HTML, extrait le contenu, télécharge images, convertit en MD."""
    soup = get_soup(url)
    if not soup: return ""

    content = soup.find('div', class_='content') or soup.body
    # Nettoyage
    for tag in content.find_all(['nav', 'script', 'style', 'footer']): tag.decompose()
    
    # Images
    images_dir = os.path.join(save_dir, "images")
    for img in content.find_all('img'):
        src = img.get('src')
        if src:
            filename = download_image(src, images_dir)
            if filename: img['src'] = f"images/{filename}"

    # Conversion
    markdown_text = md(str(content), heading_style="atx", code_language="cpp")
    markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text).strip()
    
    if not markdown_text.startswith('#'):
        markdown_text = f"# {title}\n\n{markdown_text}"

    slug = slugify_name(title)
    md_path = os.path.join(save_dir, f"{slug}.md")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(markdown_text)
    
    return f"{slug}.md"

def main():
    print("=== DÉBUT RESTRUCTURATION GPP ===")
    setup_directories()
    
    structure = get_toc_structure()
    if not structure:
        print("[ERREUR] Structure non récupérée.")
        return

    readme_content = ["# Game Programming Patterns\n", "> Table des matières hiérarchique.\n"]

    for item in structure:
            if item['type'] == 'preface':
                # i-acknowledgements
                folder_name = f"{item['roman']}-{slugify_name(item['title'])}"
                section_path = os.path.join(OUTPUT_DIR, folder_name)
                os.makedirs(section_path, exist_ok=True)
                
                print(f"[PREFACE] {item['title']} -> {folder_name}")
                filename = process_page(item['url'], section_path, item['title'])
                
                if filename:
                    rel_path = f"{folder_name}/{filename}".replace('\\', '/')
                    readme_content.append(f"- [{item['title']}]({rel_path})")

            elif item['type'] == 'section':
                # I-introduction, II-design-patterns-revisited...
                section_folder = f"{item['roman']}-{slugify_name(item['title'])}"
                section_path = os.path.join(OUTPUT_DIR, section_folder)
                os.makedirs(section_path, exist_ok=True)
                
                print(f"\n[SECTION {item['roman']}] {item['title']}")
                readme_content.append(f"\n## {item['roman']}. {item['title']}\n")
                
                for chap in item['chapters']:
                    # 01-architecture..., 02-command...
                    chap_folder = f"{chap['num']:02d}-{slugify_name(chap['title'])}"
                    chap_path = os.path.join(section_path, chap_folder)
                    os.makedirs(chap_path, exist_ok=True)
                    
                    print(f"  [CHAPITRE {chap['num']}] {chap['title']}")
                    filename = process_page(chap['url'], chap_path, chap['title'])
                    
                    if filename:
                        rel_path = f"{section_folder}/{chap_folder}/{filename}".replace('\\', '/')
                        readme_content.append(f"  {chap['num']}. [{chap['title']}]({rel_path})")

    # README.md final
    with open(os.path.join(OUTPUT_DIR, "README.md"), 'w', encoding='utf-8') as f:
        f.write("\n".join(readme_content) + "\n")

    print("\n=== RESTRUCTURATION TERMINÉE ===")

if __name__ == "__main__":
    main()
