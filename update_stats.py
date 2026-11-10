import json
import os
import urllib.request
import xml.etree.ElementTree as ET

USERNAME = "Nabnish"
TOKEN = os.environ["GITHUB_TOKEN"]

query = """
query($login: String!) {
  user(login: $login) {
    repositories(first: 100, ownerAffiliations: OWNER) {
      totalCount
      nodes { stargazers { totalCount } }
    }
    followers { totalCount }
    contributionsCollection {
      contributionCalendar { totalContributions }
    }
  }
}
"""

payload = json.dumps({
    "query": query,
    "variables": {"login": USERNAME}
}).encode("utf-8")

request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=payload,
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "Nabnish-Profile-README",
    },
)

with urllib.request.urlopen(request, timeout=30) as response:
    result = json.loads(response.read())

if result.get("errors"):
    raise RuntimeError(json.dumps(result["errors"], indent=2))

user = result["data"]["user"]
repositories = user["repositories"]

stats = {
    "repo_data": repositories["totalCount"],
    "star_data": sum(
        repo["stargazers"]["totalCount"] for repo in repositories["nodes"]
    ),
    "contrib_data": user["contributionsCollection"]["contributionCalendar"]["totalContributions"],
    "follower_data": user["followers"]["totalCount"],
}

tree = ET.parse("profile.svg")
root = tree.getroot()

for element in root.iter():
    element_id = element.attrib.get("id")
    if element_id in stats:
        element.text = f"{stats[element_id]:,}"

tree.write("profile.svg", encoding="utf-8", xml_declaration=True)
print("Updated profile stats:", stats)
