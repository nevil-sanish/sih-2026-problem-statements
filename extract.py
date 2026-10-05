import re
from bs4 import BeautifulSoup
import json

def parse_html():
    with open('sih2026PS.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all table rows
    # The table might have a specific id, but we can just look for modals starting with ViewProblemStatement
    modals = soup.find_all('div', id=re.compile(r'^ViewProblemStatement'))
    
    problems = []
    
    for modal in modals:
        # Find the parent tr
        tr = modal.find_parent('tr')
        if not tr:
            continue
            
        tds = tr.find_all('td', recursive=False)
        # 6th td (index 5) typically has the submissions, but because the modal is in the 3rd td, let's just find the td that matches '\d+/\d+' or just get all tds and find it.
        # Actually, tds could be nested. `recursive=False` on tr should give the top level tds.
        # The structure is:
        # td 1: SNo
        # td 2: Organization
        # td 3: Title + Modal
        # td 4: Category
        # td 5: PS Number
        # td 6: Submissions
        # td 7: Theme
        # td 8: Date
        
        # Let's extract submissions safely
        submissions_str = ""
        for td in tds:
            text = td.get_text(strip=True)
            if re.match(r'^\d+/\d+$', text) or re.match(r'^\d+$', text):
                submissions_str = text
                break
                
        if not submissions_str:
            # Maybe the submissions are in one of the tds, let's check text pattern
            try:
                submissions_str = tds[5].get_text(strip=True)
            except Exception:
                submissions_str = '0'
                
        # Parse submissions number
        try:
            if '/' in submissions_str:
                sub_count = int(submissions_str.split('/')[0])
            else:
                sub_count = int(submissions_str)
        except ValueError:
            sub_count = 0
            
        # Now parse the modal table
        details = {}
        modal_table = modal.find('table')
        if modal_table:
            trs = modal_table.find_all('tr')
            for m_tr in trs:
                th = m_tr.find('th')
                td = m_tr.find('td')
                if th and td:
                    key = th.get_text(strip=True)
                    # For description, preserve paragraphs by adding newlines, or just use get_text with separator
                    value = td.get_text(separator='\n', strip=True)
                    details[key] = value
                    
        details['_submissions'] = sub_count
        details['_submissions_str'] = submissions_str
        problems.append(details)
        
    return problems

def main():
    problems = parse_html()
    print(f"Found {len(problems)} problem statements.")
    
    # Sort by submissions
    problems.sort(key=lambda x: x.get('_submissions', 0))
    
    # Get least 20
    least_20 = problems[:20]
    
    # Format output
    output_text = ""
    for i, p in enumerate(least_20, 1):
        output_text += f"=== Problem {i} (Submissions: {p.get('_submissions_str')}) ===\n"
        for k, v in p.items():
            if k.startswith('_'): continue
            output_text += f"{k}:\n{v}\n\n"
        output_text += "-" * 80 + "\n\n"
        
    with open('least_20_problem_statements.txt', 'w', encoding='utf-8') as f:
        f.write(output_text)
        
    print("Saved to least_20_problem_statements.txt")

if __name__ == '__main__':
    main()
