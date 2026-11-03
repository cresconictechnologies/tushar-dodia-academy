import json

with open('dossier/youtube_videos.json', 'r', encoding='utf-8') as f:
    videos = json.load(f)

output_lines = [f"Total Videos Analyzed: {len(videos)}\n"]

titles = [v.get('title', '') for v in videos]
output_lines.append("=== SAMPLE 25 VIDEO TITLES ===")
for i, t in enumerate(titles[:25]):
    output_lines.append(f"{i+1:02d}. {t}")

keywords = {}
for t in titles:
    for word in ['Anger', 'Karna', 'Arjun', 'Student', 'Parenting', 'Math', 'Finance', 'Credit', 'Shahu', 'Krishna', 'Ram', 'Mind', 'Trekking', 'Life', 'Thought', 'Brain', 'Class']:
        if word.lower() in t.lower():
            keywords[word] = keywords.get(word, 0) + 1

output_lines.append("\n=== THEMATIC CONTENT BREAKDOWN ===")
for k, count in sorted(keywords.items(), key=lambda x: x[1], reverse=True):
    output_lines.append(f"- {k}: {count} videos")

with open('dossier/youtube_content_summary.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))

print("Wrote dossier/youtube_content_summary.txt")
