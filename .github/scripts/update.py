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

def fetch_github_stats():
    """Fetches commits and stars using GitHub GraphQL API."""
    headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
    query = """
    {
      user(login: "%s") {
        contributionsCollection {
          totalCommitContributions
        }
        repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
          nodes {
            stargazerCount
          }
        }
      }
    }
    """ % USERNAME

    try:
        response = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
        response.raise_for_status()
        data = response.json()['data']['user']
        
        total_commits = data['contributionsCollection']['totalCommitContributions']
        total_stars = sum(repo['stargazerCount'] for repo in data['repositories']['nodes'])
        return total_commits, total_stars
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return "{{ COMMITS }}", "{{ STARS }}"

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