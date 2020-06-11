import scrapy
from bs4 import BeautifulSoup
from pathlib import Path


class ConcordiaSpider(scrapy.Spider):
    name = "concordia"
    start_urls = ['https://www.concordia.ca/research.html']

    allowed_domains = ["www.concordia.ca"]

    files_path = Path("files")

    if not files_path.exists():
        files_path.mkdir()

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        divs = soup.find(class_="content-main")
        if not divs:
            divs = soup.find(id="content-main")

        if divs is not None:
            filename = response.url
            filename = '_'.join(filename.split("/")[3:])
            filename = filename.replace('https://www.concordia.ca', '', 1)
            filename = filename.replace('/', '', 1)
            filename = filename.replace('/', '_')
            filename = filename.replace('.html', 'DotHtml')
            filename = filename.replace('?', '$')

            with open(f"files\\{filename}.txt", 'wb') as f:
                f.write(response.body)

            links_to_traverse = []

            anchors = divs.find_all("a")

            for anchor in anchors:
                if anchor.get("href") is not None:
                    links_to_traverse.append(anchor.get("href"))

            for link in links_to_traverse:
                yield response.follow(link, callback=self.parse)
