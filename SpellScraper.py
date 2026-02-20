import requests
import os
import json
import time
import re
from bs4 import BeautifulSoup

BASE_URL = "http://dnd2024.wikidot.com"
INDEX_URL = f"{BASE_URL}/spell:all"
OUTPUT_DIR = "Spells"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

RATE_LIMIT = 0.5  # seconds between requests
SKIP_EXISTING = True


# ---------------------------------
# Utility
# ---------------------------------
def ensure_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)


def save_json(slug, data):
    path = os.path.join(OUTPUT_DIR, f"{slug}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def fetch_page(url):
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


# ---------------------------------
# Phase 1: Get all spell slugs
# ---------------------------------
def scrape_spell_index():
    print("[INDEX] Fetching spell index...")
    soup = fetch_page(INDEX_URL)

    slugs = set()

    for link in soup.select("a[href^='/spell:']"):
        href = link.get("href")
        if ":" in href:
            slug = href.split(":")[1]
            if slug and slug != "all":
                slugs.add(slug)

    print(f"[INDEX] Found {len(slugs)} spells.")
    return sorted(slugs)


# ---------------------------------
# Phase 2: Scrape individual spell
# ---------------------------------
def scrape_spell(slug):
    print(f"[SCRAPE] {slug}")

    url = f"{BASE_URL}/spell:{slug}"
    soup = fetch_page(url)

    content = soup.select_one("#page-content")
    if not content:
        print(f"[ERROR] Could not find page-content for {slug}")
        return None

    spell_data = {
        "slug": slug,
        "name": None,
        "source": None,
        "school_line": None,
        "casting_time": None,
        "range": None,
        "components": None,
        "duration": None,
        "description": [],
        "tags": []
    }

    # --------------------------
    # Title
    # --------------------------
    title = soup.select_one(".page-title span")
    if title:
        spell_data["name"] = title.get_text(strip=True)

    paragraphs = content.find_all("p")

    if len(paragraphs) < 3:
        print(f"[WARNING] Unexpected format for {slug}")
        return spell_data

    # --------------------------
    # Source
    # --------------------------
    spell_data["source"] = paragraphs[0].get_text(strip=True)



    spell_data["school_line"] = ""
    spell_data["casting_time"] = ""
    spell_data["range"] = ""
    spell_data["components"] = ""
    spell_data["duration"] = ""

    # --------------------------------------------------
    # 1 Extract School Line from <em>
    # --------------------------------------------------

    em_tag = soup.find("em")
    if em_tag:
        spell_data["school_line"] = em_tag.get_text(strip=True)

    # Fallback: if no <em>, detect via pattern
    if not spell_data["school_line"]:
        for p in paragraphs:
            text = p.get_text(" ", strip=True)

            if re.search(r"(Cantrip|\d+(st|nd|rd|th)-level)", text):
                spell_data["school_line"] = text
                break

    # --------------------------------------------------
    # 2 Extract Stat Block Fields from ALL <strong>
    # --------------------------------------------------

    for strong in soup.find_all("strong"):
        label = strong.get_text(strip=True)

        # Get text after label
        value = strong.next_sibling
        if value:
            value = str(value).strip().replace("\n", " ").strip()

        if "Casting Time" in label:
            spell_data["casting_time"] = value

        elif "Range" in label:
            spell_data["range"] = value

        elif "Components" in label:
            spell_data["components"] = value

        elif "Duration" in label:
            spell_data["duration"] = value

    # --------------------------
    # Description
    # --------------------------
    for p in paragraphs[3:]:
        text = p.get_text(" ", strip=True)
        if text:
            spell_data["description"].append(text)

    # --------------------------
    # Tags
    # --------------------------
    tag_links = soup.select(".page-tags a")
    spell_data["tags"] = [t.get_text(strip=True) for t in tag_links]

    return spell_data


# ---------------------------------
# Main
# ---------------------------------
def main():
    print("===== SPELL SCRAPER START =====")
    ensure_output_dir()

    slugs = scrape_spell_index()

    for slug in slugs:
        path = os.path.join(OUTPUT_DIR, f"{slug}.json")

        # if SKIP_EXISTING and os.path.exists(path):
        #     print(f"[SKIP] {slug} already exists.")
        #     continue

        try:
            spell_data = scrape_spell(slug)

            if spell_data:
                save_json(slug, spell_data)
                print(f"[SAVED] {slug}.json")

            time.sleep(RATE_LIMIT)

        except Exception as e:
            print(f"[ERROR] {slug} -> {e}")

    print("===== SPELL SCRAPER COMPLETE =====")


if __name__ == "__main__":
    main()
