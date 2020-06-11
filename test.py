import requests
from bs4 import BeautifulSoup

# url = 'https://www.concordia.ca/news/stories/2019/11/29/concordia-researchers-want-to-revolutionize-motion-picture-film-processing-using-coffee.html?c=/research'
# url = 'https://www.concordia.ca/research.html'
url = "https://www.concordia.ca/research/spotlights.html"
# url = "https://www.concordia.ca/next-gen/artificial-intelligence.html"
# url = "https://www.concordia.ca/cunews/encs/2019/11/29/phd-water-quality-research-award.html?c=/research"

response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser')
soup.prettify()
divs = soup.find(class_="content-main")
if not divs:
    divs = soup.find(id="content-main")

social_divs = divs.find_all(class_="social-media")

social_media = []
for div in social_divs:
    social_media += div.find_all("a")

links_to_traverse = []
anchors = divs.find_all("a")

for anchor in anchors:
    if anchor in social_media:
        continue

    links_to_traverse.append(anchor.get("href"))

print(links_to_traverse)
tags = ['p', 'li', 'h1', 'h2', 'h3']
content = ""
for tag in tags:
    content += '\n' + '\n'.join([el.text for el in divs.find_all(tag)])
# print(content.replace('\n', ' '))

