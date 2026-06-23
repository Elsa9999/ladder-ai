import requests
import json
import time

headers = {
    'Accept': 'application/vnd.github+json',
    'User-Agent': 'TIA-Portal-Seeker'
}

extensions = ['zap18', 'zap17', 'zap16', 'ap18', 'ap17']
found_repos = {}

print("Searching GitHub for TIA Portal project files...")
for ext in extensions:
    url = f"https://api.github.com/search/code?q=extension:{ext}"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            print(f"Extension .{ext}: found {len(items)} files.")
            for item in items:
                repo_name = item['repository']['full_name']
                repo_url = item['repository']['html_url']
                file_path = item['path']
                if repo_name not in found_repos:
                    found_repos[repo_name] = {
                        'url': repo_url,
                        'files': []
                    }
                found_repos[repo_name]['files'].append(file_path)
        elif response.status_code == 403:
            print(f"Rate limited or forbidden for .{ext}. Skipping...")
        else:
            print(f"Error {response.status_code} for .{ext}")
        time.sleep(2)  # Avoid rate limiting
    except Exception as e:
        print(f"Request failed for .{ext}: {e}")

print("\n--- RESULTS ---")
for repo, info in list(found_repos.items())[:15]:
    print(f"\nRepository: {repo}")
    print(f"URL: {info['url']}")
    print("Files:")
    for f in info['files'][:3]:
        print(f"  - {f}")
