import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

BASE_URL = "http://dnd2024.wikidot.com"
# CLASS_SLUGS = [
#     "artificer", "barbarian", "bard", "cleric", "druid", "fighter", 
#     "monk", "ranger", "rogue", "sorcerer", "warlock", "wizard"
# ]

# -----------------------------
# Utility
# -----------------------------

def fetch_page(url):
    print(f"[FETCH] {url}")
    r = requests.get(url)
    r.raise_for_status()
    return r.text

def clean_filename(name):
    return (
        name.lower()
        .replace(" ", "_")
        .replace(":", "")
        .replace("/", "")
    )

# -----------------------------
# Core Extraction
# -----------------------------

def extract_page_content(html):
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()
    return soup.find("div", id="page-content")

def extract_title(soup):
    title = soup.find("div", class_="page-title")
    if title:
        return title.get_text(strip=True)
    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)
    return "Unknown Class"

def extract_tables(content):
    tables = []
    first_table = content.find("table", class_="wiki-content-table")
    if first_table:
        rows = []
        for row in first_table.find_all("tr"):
            cols = [col.get_text(" ", strip=True) for col in row.find_all(["td", "th"])]
            if cols:
                rows.append(cols)
        tables.append(rows)
    return tables

def extract_sections(content):
    sections = []
    for header in content.find_all(["h2", "h3"]):
        title = header.get_text(" ", strip=True)
        # Only keep "Level X" features
        if "level" not in title.lower():
            continue

        section_text = []
        sibling = header.find_next_sibling()
        while sibling and sibling.name not in ["h2", "h3"]:
            if sibling.name:
                section_text.append(sibling.get_text(" ", strip=True))
            sibling = sibling.find_next_sibling()

        sections.append({
            "title": title,
            "content": "\n\n".join(section_text)
        })
    return sections

def extract_subclass_links(content, class_slug):
    subclass_links = []
    for a in content.find_all("a", href=True):
        href = a["href"]
        # Match pattern /wizard:abjurer
        if href.startswith(f"/{class_slug}:"):
            subclass_links.append(urljoin(BASE_URL, href))
    return list(set(subclass_links))

# -----------------------------
# JSON Builder
# -----------------------------

def build_page_json(url, first_table_only=True, level_only=True):
    html = fetch_page(url)
    content = extract_page_content(html)
    soup = BeautifulSoup(html, "lxml")
    title = extract_title(soup)
    tables = extract_tables(content) if first_table_only else []
    sections = extract_sections(content) if level_only else []

    print(f"[EXTRACT] {title} -> {len(tables)} table(s), {len(sections)} section(s)")

    return {
        "title": title,
        "url": url,
        "tables": tables,
        "sections": sections
    }

# -----------------------------
# Main Class Builder
# -----------------------------

def build_class(class_slug):
    class_url = f"{BASE_URL}/{class_slug}:main"

    # Base directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    classes_root = os.path.join(script_dir, "Classes")
    os.makedirs(classes_root, exist_ok=True)

    html = fetch_page(class_url)
    content = extract_page_content(html)
    soup = BeautifulSoup(html, "lxml")
    class_name = extract_title(soup)
    safe_class_name = clean_filename(class_name)

    # Create folder for class
    class_dir = os.path.join(classes_root, safe_class_name)
    os.makedirs(class_dir, exist_ok=True)

    # Build class JSON
    class_data = build_page_json(class_url)
    class_json_path = os.path.join(class_dir, f"{safe_class_name}.json")

    print(f"[SCRAPER WRITE] Writing class JSON to: {class_json_path}")
    with open(class_json_path, "w", encoding="utf-8") as f:
        json.dump(class_data, f, indent=2)
    print(f"[SUCCESS] Saved {safe_class_name}.json")

    # Detect subclasses
    subclass_links = extract_subclass_links(content, class_slug)
    if subclass_links:
        subclass_dir = os.path.join(class_dir, "subclasses")
        os.makedirs(subclass_dir, exist_ok=True)
        for link in subclass_links:
            subclass_slug = link.split("/")[-1]
            subclass_safe = clean_filename(subclass_slug.split(":")[-1])

            subclass_data = build_page_json(link)

            subclass_json_path = os.path.join(subclass_dir, f"{subclass_safe}.json")
            print(f"[SCRAPER WRITE] Writing subclass JSON to: {subclass_json_path}")
            with open(subclass_json_path, "w", encoding="utf-8") as f:
                json.dump(subclass_data, f, indent=2)
            print(f"[SUCCESS] Saved subclass: {subclass_safe}.json")

    print("[DONE] Class scraping complete.\n")

# -----------------------------
# Run
# -----------------------------

if __name__ == "__main__":
    # Currently just Wizard for testing
    build_class("wizard")
    print("\nAll classes processed.")
