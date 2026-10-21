import os
import random
import requests
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

# --- CONFIGURATION ---
USERNAME = 'oyelurker'
TOKEN = os.getenv('GITHUB_TOKEN')
WAIFU_DIR = 'Waifu'
IMG_DIR = 'img'
TEMPLATE_FILE = 'TEMPLATE.md'
OUTPUT_FILE = 'README.md'
CROPPED_IMG = 'cropped.jpg'
# ---------------------

def fetch_cached_stats():
    """Reads fallback stats from README.md if API calls fail."""
    import re
    commits, stars = None, None
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
            c_match = re.search(r'Total commits:\s*(\d+)', content)
            s_match = re.search(r'Total stars gained:\s*(\d+)', content)
            if c_match:
                commits = int(c_match.group(1))
            if s_match:
                stars = int(s_match.group(1))
        except Exception:
            pass
    return commits or 656, stars or 15

def fetch_github_stats():
    """Fetches total lifetime commits and stars using GitHub Search, GraphQL, and REST APIs."""
    headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
    fallback_commits, fallback_stars = fetch_cached_stats()
    
    # 1. Total Lifetime Commits
    total_commits = None
    
    # Method A: GitHub Commit Search API (author:oyelurker across all repositories and years)
    try:
        search_headers = dict(headers)
        search_headers["Accept"] = "application/vnd.github.cloak-preview"
        search_url = f"https://api.github.com/search/commits?q=author:{USERNAME}"
        res = requests.get(search_url, headers=search_headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if "total_count" in data:
                total_commits = data["total_count"]
    except Exception as e:
        print(f"Commit Search API error: {e}")

    # Method B: GraphQL multi-year contributions (fallback)
    if total_commits is None:
        try:
            query_years = """
            query($login: String!) {
              user(login: $login) {
                contributionsCollection {
                  contributionYears
                }
              }
            }
            """
            res = requests.post(
                'https://api.github.com/graphql',
                json={'query': query_years, 'variables': {'login': USERNAME}},
                headers=headers,
                timeout=10
            )
            if res.status_code == 200:
                years = res.json().get('data', {}).get('user', {}).get('contributionsCollection', {}).get('contributionYears', [])
                if years:
                    year_queries = [
                        f"""
                        y{y}: contributionsCollection(from: "{y}-01-01T00:00:00Z", to: "{y}-12-31T23:59:59Z") {{
                          totalCommitContributions
                          restrictedContributionsCount
                        }}
                        """
                        for y in years
                    ]
                    full_query = "query { user(login: \"%s\") { %s } }" % (USERNAME, " ".join(year_queries))
                    res_years = requests.post('https://api.github.com/graphql', json={'query': full_query}, headers=headers, timeout=10)
                    if res_years.status_code == 200:
                        user_data = res_years.json().get('data', {}).get('user', {})
                        commits_sum = sum(
                            user_data.get(f'y{y}', {}).get('totalCommitContributions', 0) +
                            user_data.get(f'y{y}', {}).get('restrictedContributionsCount', 0)
                            for y in years
                        )
                        if commits_sum > 0:
                            total_commits = commits_sum
        except Exception as e:
            print(f"GraphQL commits error: {e}")

    if total_commits is None:
        total_commits = fallback_commits

    # 2. Total Stars
    total_stars = None
    
    # Method A: GraphQL
    try:
        stars_query = """
        query($login: String!) {
          user(login: $login) {
            repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
              nodes {
                stargazerCount
              }
            }
          }
        }
        """
        res = requests.post(
            'https://api.github.com/graphql',
            json={'query': stars_query, 'variables': {'login': USERNAME}},
            headers=headers,
            timeout=10
        )
        if res.status_code == 200:
            repos = res.json().get('data', {}).get('user', {}).get('repositories', {}).get('nodes', [])
            total_stars = sum(repo['stargazerCount'] for repo in repos)
    except Exception as e:
        print(f"GraphQL stars error: {e}")

    # Method B: REST API (fallback for stars)
    if total_stars is None:
        try:
            stars_sum = 0
            page = 1
            while True:
                url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}&type=owner"
                res = requests.get(url, headers=headers, timeout=10)
                if res.status_code != 200:
                    break
                repos = res.json()
                if not repos or not isinstance(repos, list):
                    break
                for repo in repos:
                    if not repo.get('fork', False):
                        stars_sum += repo.get('stargazers_count', 0)
                if len(repos) < 100:
                    break
                page += 1
            total_stars = stars_sum
        except Exception as e:
            print(f"REST stars error: {e}")

    if total_stars is None:
        total_stars = fallback_stars

    return total_commits, total_stars

def get_random_image():
    """Selects a random image from the Waifu folder."""
    if not os.path.exists(WAIFU_DIR):
        raise FileNotFoundError(f"Folder '{WAIFU_DIR}' not found. Please create it and add images.")
    
    valid_exts = ('.jpg', '.jpeg', '.png', '.webp')
    images = [f for f in os.listdir(WAIFU_DIR) if f.lower().endswith(valid_exts)]
    
    if not images:
        raise ValueError(f"No valid images found in '{WAIFU_DIR}'.")
        
    return os.path.join(WAIFU_DIR, random.choice(images))

def process_image(image_path, num_colors=5):
    """Resizes image to cropped.jpg and extracts dominant colors."""
    print(f"Processing image: {image_path}")
    
    with Image.open(image_path) as img:
        rgb_img = img.convert('RGB')
        
        # Save cropped/resized version for the profile
        rgb_img.thumbnail((600, 600), Image.Resampling.LANCZOS)
        rgb_img.save(CROPPED_IMG, "JPEG", quality=85)
        
        # Extract colors using KMeans
        small_img = rgb_img.resize((150, 150))
        data = np.array(small_img).reshape((-1, 3))
        
        kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
        kmeans.fit(data)
        colors = kmeans.cluster_centers_.astype(int)
        
        # Convert RGB array to hex strings
        hex_colors = ['#' + ''.join([f'{c:02x}' for c in color]) for color in colors]
        return hex_colors

def create_color_blocks(hex_colors):
    """Creates the small colored squares and returns the HTML tags."""
    os.makedirs(IMG_DIR, exist_ok=True)
    html_tags = []
    
    for hex_color in hex_colors:
        clean_hex = hex_color.lstrip('#')
        rgb = tuple(int(clean_hex[i:i+2], 16) for i in (0, 2, 4))
        
        # Create a 25x20 color block
        img = Image.new('RGB', (25, 20), rgb)
        img_path = f'{IMG_DIR}/{clean_hex}.png'
        img.save(img_path)
        
        # Build the HTML image tag pointing to YOUR repo
        img_url = f"https://raw.githubusercontent.com/{USERNAME}/{USERNAME}/main/{img_path}"
        html_tags.append(f'<img alt="{hex_color}" src="{img_url}" width="25" height="20" />')
        
    return "".join(html_tags)

def update_readme(commits, stars, color_html):
    """Injects stats and colors into TEMPLATE.md and saves as README.md."""
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template = f.read()

    # 1. Update Stats
    readme = template.replace('{{ COMMITS }}', str(commits))
    readme = readme.replace('{{ STARS }}', str(stars))
    
    # 2. Update Color Palette block safely using unique ID
    lines = readme.split('\n')
    new_lines = []
    skip = False
    
    for line in lines:
        if '<p align="center" id="color-palette">' in line:
            new_lines.append(line)
            new_lines.append(f"  {color_html}")
            skip = True
        elif skip and '</p>' in line:
            skip = False
            new_lines.append(line)
        elif not skip:
            new_lines.append(line)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))

def main():
    print(f"Starting profile update for {USERNAME}...")
    
    commits, stars = fetch_github_stats()
    print(f"Fetched Stats: {commits} Commits, {stars} Stars")
    
    img_path = get_random_image()
    colors = process_image(img_path)
    print(f"Extracted Colors: {colors}")
    
    color_html = create_color_blocks(colors)
    update_readme(commits, stars, color_html)
    
    print("Successfully generated new README.md!")

if __name__ == "__main__":
    main()