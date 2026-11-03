import re

with open(r'c:\projects\tushar sir dodia\dossier\downloads\brochure_extracted_text.txt', 'r', encoding='utf-8') as f:
    text = f.read()

pages = text.split('=== PAGE ')

with open(r'c:\projects\tushar sir dodia\dossier\brochure_summary.txt', 'w', encoding='utf-8') as out:
    for i in range(1, len(pages)):
        lines = [l.strip() for l in pages[i].split('\n') if l.strip()]
        if not lines:
            continue
        page_num = lines[0].replace(' ===', '')
        content = '\n'.join(lines[1:])
        out.write(f"=== PAGE {page_num} ===\n{content}\n\n")

print(f"Wrote {len(pages)-1} pages to brochure_summary.txt")

# Let's search for specific entities like banks, institutes, companies
print("\n--- CORPORATE & CLIENT MENTIONS ---")
for i in range(1, len(pages)):
    p_text = pages[i]
    matches = re.findall(r'(?i)(buldana|buldhana|rajarshi|shahu|ambika|dhanik|bank|persistent|fidelity|cfa|frm|mba|gold medalist|academy|experience)', p_text)
    if matches:
        first_few = [l.strip() for l in p_text.split('\n') if l.strip()][:5]
        # print first few lines of matching page
        print(f"Page {i}: {', '.join(set(matches))} -> {' / '.join(first_few[:3])}")
