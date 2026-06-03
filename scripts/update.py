import os
import requests

TOKEN = os.getenv('GITHUB_TOKEN')
USERNAME = 'oyelurker'

headers = {"Authorization": f"Bearer {TOKEN}"}

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

# Fetch data
response = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
data = response.json()['data']['user']
# Calculate totals
total_commits = data['contributionsCollection']['totalCommitContributions']
total_stars = sum(repo['stargazerCount'] for repo in data['repositories']['nodes'])
# Read the template
with open('README_template.md', 'r', encoding='utf-8') as f:
    template = f.read()
# Replace the placeholders with actual live data
new_readme = template.replace('{{ COMMITS }}', str(total_commits)).replace('{{ STARS }}', str(total_stars))
# Overwrite the actual README.md
with open('README.md', 'w', encoding='utf-8') as f:
    f.write(new_readme)

print(f"Successfully updated README with {total_commits} commits and {total_stars} stars.")
