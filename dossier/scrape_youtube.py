import json
import yt_dlp

def scrape_youtube():
    ydl_opts = {
        'extract_flat': True,
        'quiet': False,
    }
    videos = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for tab in ['videos', 'shorts']:
            url = f'https://www.youtube.com/@TusharDodia/{tab}'
            print(f'Fetching {url}...')
            try:
                res = ydl.extract_info(url, download=False)
                if res and 'entries' in res:
                    for e in res['entries']:
                        e['tab'] = tab
                        videos.append(e)
            except Exception as ex:
                print(f'Error fetching {url}: {ex}')

    # Deduplicate by id
    unique_videos = {}
    for v in videos:
        vid = v.get('id')
        if vid and vid not in unique_videos:
            unique_videos[vid] = v

    video_list = list(unique_videos.values())
    print(f'Total unique videos/shorts collected: {len(video_list)}')

    out_file = r'c:\projects\tushar sir dodia\dossier\youtube_videos.json'
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(video_list, f, indent=2, ensure_ascii=False)
    print(f'Saved metadata to {out_file}')

    for i, e in enumerate(video_list):
        print(f"[{i+1}] {e.get('title')} | URL: {e.get('url')} | Views: {e.get('view_count')} | Duration: {e.get('duration')}s | Tab: {e.get('tab')}")

if __name__ == '__main__':
    scrape_youtube()
