import json

with open(r'c:\projects\tushar sir dodia\dossier\youtube_videos.json', 'r', encoding='utf-8') as f:
    videos = json.load(f)

print(f'Total videos/shorts loaded: {len(videos)}')
total_views = sum(v.get('view_count') or 0 for v in videos)
print(f'Total view count: {total_views:,}')

sorted_by_views = sorted(videos, key=lambda x: x.get('view_count') or 0, reverse=True)

with open(r'c:\projects\tushar sir dodia\dossier\youtube_analysis.txt', 'w', encoding='utf-8') as out:
    out.write(f"Total Videos: {len(videos)}\nTotal Views: {total_views:,}\n\n")
    out.write("=== TOP 30 MOST POPULAR VIDEOS ===\n")
    for i, v in enumerate(sorted_by_views[:30]):
        out.write(f"{i+1}. [{v.get('tab', '').upper()}] {v.get('title')} | Views: {v.get('view_count')} | Duration: {v.get('duration')}s | URL: {v.get('url')}\n")

    out.write("\n=== ALL VIDEOS (CHRONOLOGICAL / PLAYLIST ORDER) ===\n")
    for i, v in enumerate(videos):
        out.write(f"{i+1}. [{v.get('tab', '').upper()}] {v.get('title')} | Views: {v.get('view_count')} | Date: {v.get('upload_date')} | URL: {v.get('url')}\n")

print("Wrote youtube_analysis.txt")
