import scrapy
import json
import re

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
X_ACCESS_TOKEN = ""
X_SOURCE = "local"

def clean_html_with_regex(html_content):
    # Use regular expression to remove HTML tags
    clean_text = re.sub(r"<.*?>", "", html_content)

    # Remove newline characters
    clean_text = clean_text.replace('\n', ' ').strip()
    
    # Replace multiple spaces with a single space
    clean_text = re.sub(r'\s+', ' ', clean_text)

    return clean_text


class TikiSpider(scrapy.Spider):
    name = "tiki_spider"

    start_urls = [
        "https://api.tiki.vn/seller-store/v2/collections/118456/products?limit=20&cursor=0"
    ]

    def start_requests(self):
        headers = {
            "User-Agent": USER_AGENT,
            "X-Access-Token": X_ACCESS_TOKEN,
            "X-Source": X_SOURCE,
        }

        for url in self.start_urls:
            yield scrapy.Request(url=url, headers=headers, callback=self.parse)

    def parse(self, response):
        data = json.loads(response.body)

        for product in data["data"]:
            product_item = {
                "product_id": product["id"],
                "product_name": product["name"],
                "quantity_sold": product["quantity_sold"]["value"],
            }

            product_url = f"https://tiki.vn/api/v2/products/{product['id']}"

            yield scrapy.Request(
                url=product_url,
                callback=self.parse_product_details,
                meta=product_item,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
                },
            )

    def parse_product_details(self, response):
        data = json.loads(response.body)

        yield {
            "product_url": data["short_url"],
            "description": clean_html_with_regex(data["description"]),
        }
