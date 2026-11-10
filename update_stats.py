import os
import urllib.request
import json
import xml.etree.ElementTree as ET

USERNAME = "Nabnish"
TOKEN = os.environ["GITHUB_TOKEN"]

query = """
query($login: String!) {
  user(login: $login) {
    repositories( first: 100, ownerAffiliations: OWNER) {
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
}).encode()

request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=payload,
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "Nabnish-Profile-README"
    }
)

with urllib.request.urlopen(request) as response:
    result = json.loads(response.read())

if "errors" in result:
    raise RuntimeError(result["errors"])

user = result["data"]["user"]
repos = user["repositories"]
stats = {
    "repo_data": repos["totalCount"],
    "star_data": sum(repo["stargazers"]["totalCount"] for repo in repos["nodes"]),
    "contrib_data": user["contributionsCollection"]["contributionCalendar"]["totalContributions"],
    "follower_data": user["followers"]["totalCount"],
}

tree = ET.parse("profile.svg")
root = tree.getroot()
ns = {"svg": "http://www.w3.org/2000/svg"}

for element in root.findall(".//svg:text", ns):
    element_id = element.attrib.get("id")
    if element_id in stats:
        element.text = f"{stats[element_id]:,}"

tree.write("profile.svg", encoding="utf-8", xml_declaration=True)
print("Updated profile.svg:", stats)
