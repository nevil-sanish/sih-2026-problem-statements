#!/usr/bin/env python3
"""
Scraper and Generator for Smart India Hackathon (SIH) 2026 Problem Statements.
Fetches https://sih.gov.in/sih2026PS, parses all problem statements and modals,
and generates:
  - all_problem_statements.md (single comprehensive markdown document)
  - SIH_2026_Problem_Statements.md (matching README reference)
  - all_problem_statements.json (structured JSON data)
  - problem_statements/{id}.md (individual files for each statement)
"""

import os
import re
import json
import urllib.request
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import ftfy

URL = "https://sih.gov.in/sih2026PS"
HTML_FILE = "sih2026PS.html"
MD_FILE = "all_problem_statements.md"
ALT_MD_FILE = "SIH_2026_Problem_Statements.md"
JSON_FILE = "all_problem_statements.json"
OUTPUT_DIR = "problem_statements"


def fetch_html():
    """Fetch live HTML or fallback to local file."""
    print(f"Fetching from {URL}...")
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    req = urllib.request.Request(URL, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode("utf-8", errors="ignore")
            print(f"Successfully fetched {len(html)} bytes from {URL}")
            with open(HTML_FILE, "w", encoding="utf-8") as f:
                f.write(html)
            return html
    except Exception as e:
        print(f"Warning: Failed to fetch live ({e}). Using local {HTML_FILE}...")
        if os.path.exists(HTML_FILE):
            with open(HTML_FILE, "r", encoding="utf-8") as f:
                return f.read()
        raise RuntimeError("No local HTML file available and network fetch failed.")


def clean_description(td):
    """Convert HTML description to clean GitHub markdown."""
    div = td.find("div", class_="style-2")
    raw = str(div) if div else str(td)
    clean = md(raw, heading_style="ATX", bullets="*")
    clean = ftfy.fix_text(clean)
    # Remove trailing spaces on lines
    clean = re.sub(r"[ \t]+\n", "\n", clean)
    # Normalize multiple newlines
    clean = re.sub(r"\n{3,}", "\n\n", clean)
    return clean.strip()


def normalize_line(text):
    """Collapse internal whitespace/newlines into a single line."""
    if not text:
        return ""
    fixed = ftfy.fix_text(text)
    return " ".join(fixed.split())


def clean_multiline_field(text):
    """Clean multiline text fields such as Dataset Link."""
    if not text:
        return ""
    fixed = ftfy.fix_text(text)
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in fixed.splitlines()]
    # Remove leading/trailing empty lines
    clean = "\n".join(lines).strip()
    return clean


def parse_problem_statements(html_content):
    """Parse problem statements from HTML table and modals."""
    soup = BeautifulSoup(html_content, "html.parser")
    
    tbody = soup.find("tbody")
    if not tbody:
        raise ValueError("Could not find <tbody> in HTML.")
        
    rows = tbody.find_all("tr", recursive=False)
    print(f"Found {len(rows)} table rows.")
    
    problems = []
    
    for row in rows:
        tds = row.find_all("td", recursive=False)
        if len(tds) < 8:
            continue
            
        s_no = tds[0].get_text(strip=True)
        org_row = tds[1].get_text(strip=True)
        ps_number = tds[4].get_text(strip=True)
        submitted_count = tds[5].get_text(strip=True)
        theme_row = tds[6].get_text(strip=True)
        deadline = tds[7].get_text(strip=True)
        
        modal = tds[2].find("div", class_="modal")
        if not modal:
            continue
            
        modal_table = modal.find("table")
        if not modal_table:
            continue
            
        modal_id = modal.get("id", "").replace("ViewProblemStatement", "")
        
        details = {
            "Problem Statement ID": modal_id,
            "Problem Statement Title": "",
            "Description": "",
            "Organization": normalize_line(org_row),
            "Department": "",
            "Category": "",
            "Theme": normalize_line(theme_row),
            "Youtube Link": "",
            "Dataset Link": "",
            "Contact info": "",
            "_s_no": s_no,
            "_ps_number": ps_number,
            "_submitted_count": submitted_count,
            "_deadline": deadline,
        }
        
        for tr in modal_table.find_all("tr"):
            th = tr.find("th")
            td = tr.find("td")
            if not th or not td:
                continue
            key = th.get_text(strip=True)
            
            if key == "Description":
                details["Description"] = clean_description(td)
            elif key == "Problem Statement Title":
                div = td.find("div", class_="style-2")
                text = div.get_text(strip=True) if div else td.get_text(strip=True)
                details[key] = normalize_line(text)
            elif key in ["Youtube Link", "Contact info"]:
                text = td.get_text(strip=True)
                hrefs = [
                    a.get("href", "").strip()
                    for a in td.find_all("a")
                    if a.get("href", "").strip()
                    and a.get("href", "").strip() not in ["#", "javascript:void(0);", "javascript:;"]
                ]
                val = hrefs[0] if (hrefs and not text) else text
                details[key] = normalize_line(val)
            elif key == "Dataset Link":
                div = td.find("div", class_="style-2")
                text = div.get_text() if div else td.get_text()
                hrefs = [
                    a.get("href", "").strip()
                    for a in td.find_all("a")
                    if a.get("href", "").strip()
                    and a.get("href", "").strip() not in ["#", "javascript:void(0);", "javascript:;"]
                ]
                val = hrefs[0] if (hrefs and not text.strip()) else text
                details[key] = clean_multiline_field(val)
            elif key in ["Problem Statement ID", "Organization", "Department", "Category", "Theme"]:
                div = td.find("div", class_="style-2")
                text = div.get_text(strip=True) if div else td.get_text(strip=True)
                details[key] = normalize_line(text)
            else:
                div = td.find("div", class_="style-2")
                text = div.get_text(strip=True) if div else td.get_text(strip=True)
                details[key] = normalize_line(text)
                
        problems.append(details)
        
    # Sort by Problem Statement ID numerically
    problems.sort(key=lambda p: int(p["Problem Statement ID"]) if p["Problem Statement ID"].isdigit() else 999999)
    return problems


def generate_single_markdown(problems):
    """Generate a single markdown document containing all problem statements."""
    lines = [
        "# Smart India Hackathon 2026 Problem Statements\n",
        "## Table of Contents\n",
    ]
    
    for p in problems:
        ps_id = p["Problem Statement ID"]
        title = p["Problem Statement Title"]
        lines.append(f"- [{ps_id} - {title}](#{ps_id})")
        
    lines.append("\n---\n")
    
    for p in problems:
        ps_id = p["Problem Statement ID"]
        title = p["Problem Statement Title"]
        desc = p["Description"]
        org = p["Organization"]
        dept = p["Department"]
        cat = p["Category"]
        theme = p["Theme"]
        yt = p["Youtube Link"]
        dataset = p["Dataset Link"]
        contact = p["Contact info"]
        
        block = [
            f"## <a id=\"{ps_id}\"></a>{ps_id}\n",
            "**Problem Statement ID**:",
            f"{ps_id}\n",
            "**Problem Statement Title**:",
            f"{title}\n",
            "**Description**:",
            f"{desc}\n",
            "**Organization**:",
            f"{org}\n",
            "**Department**:",
            f"{dept}\n",
            "**Category**:",
            f"{cat}\n",
            "**Theme**:",
            f"{theme}\n",
            "**Youtube Link**:",
            f"{yt}\n",
            "**Dataset Link**:",
            f"{dataset}\n",
            "**Contact info**:",
            f"{contact}\n",
        ]
        
        # Include Mentor 1 if present
        if p.get("Mentor 1"):
            block.extend(["**Mentor 1**:", f"{p['Mentor 1']}\n"])
            
        block.append("---\n")
        lines.append("\n".join(block))
        
    return "\n".join(lines)


def generate_individual_markdown(p):
    """Generate individual markdown content for a single problem statement."""
    ps_id = p["Problem Statement ID"]
    title = p["Problem Statement Title"]
    desc = p["Description"]
    org = p["Organization"]
    dept = p["Department"]
    cat = p["Category"]
    theme = p["Theme"]
    yt = p["Youtube Link"]
    dataset = p["Dataset Link"]
    contact = p["Contact info"]
    
    lines = [
        f"# Problem Statement ID: {ps_id}\n",
        "## Problem Statement Title\n",
        f"{title}\n",
        "## Description\n",
        f"{desc}\n",
        "## Organization\n",
        f"{org}\n",
        "## Department\n",
        f"{dept}\n",
        "## Category\n",
        f"{cat}\n",
        "## Theme\n",
        f"{theme}\n",
        "## Youtube Link\n",
        f"{yt}\n",
        "## Dataset Link\n",
        f"{dataset}\n",
        "## Contact info\n",
        f"{contact}\n",
    ]
    
    if p.get("Mentor 1"):
        lines.extend(["## Mentor 1\n", f"{p['Mentor 1']}\n"])
        
    return "\n".join(lines)


def main():
    html_content = fetch_html()
    problems = parse_problem_statements(html_content)
    print(f"Extracted {len(problems)} problem statements.")
    
    # 1. Write single markdown file (all_problem_statements.md)
    print(f"Generating {MD_FILE}...")
    single_md = generate_single_markdown(problems)
    with open(MD_FILE, "w", encoding="utf-8") as f:
        f.write(single_md)
    print(f"Saved {MD_FILE} ({len(single_md)} characters).")
    
    # 2. Write SIH_2026_Problem_Statements.md
    print(f"Generating {ALT_MD_FILE}...")
    with open(ALT_MD_FILE, "w", encoding="utf-8") as f:
        f.write(single_md)
    print(f"Saved {ALT_MD_FILE}.")
    
    # 3. Write all_problem_statements.json
    print(f"Generating {JSON_FILE}...")
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(problems, f, indent=2, ensure_ascii=False)
    print(f"Saved {JSON_FILE}.")
    
    # 4. Write individual markdown files in problem_statements/
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Generating individual markdown files in {OUTPUT_DIR}/...")
    for p in problems:
        filename = os.path.join(OUTPUT_DIR, f"{p['Problem Statement ID']}.md")
        content = generate_individual_markdown(p)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
    print(f"Saved {len(problems)} files to {OUTPUT_DIR}/.")
    
    # Validation check for 26243
    matching = [p for p in problems if p["Problem Statement ID"] == "26243"]
    if matching:
        print("Validation SUCCESS: Problem statement 26243 found and verified!")
        print(f"Title: {matching[0]['Problem Statement Title']}")
        print(f"Theme: {matching[0]['Theme']}")
        print(f"Category: {matching[0]['Category']}")
    else:
        print("Validation WARNING: Problem statement 26243 not found!")


if __name__ == "__main__":
    main()
