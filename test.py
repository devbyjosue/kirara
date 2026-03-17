import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy_playwright.page import PageMethod

class XSpider(scrapy.Spider):
    name = 'x_spider'

    def start_requests(self):
        urls = [
            'https://twitter.com/lu_aux_fraises/status/2032707439154348344'
        ]
        
        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", 'img[alt="Image"]', timeout=10000),
                    ],
                }
            )

    def parse(self, response):
        self.logger.info(f"✅ Renderizado completo para: {response.url}")

        image_url = (
            response.css('img[alt="Image"]::attr(src)').get() or 
            response.css('img.css-9pa8cd::attr(src)').get()
        )

        data = {
            'url': response.url,
            'title': response.css('title::text').get(),
            'content': response.css('div[data-testid="tweetText"] ::text').getall(),
            'image_url': image_url,
        }

        print("\n" + "="*30)
        print(f"RESULTADO ENCONTRADO:")
        print(f"IMAGEN: {data['image_url']}")
        print(f"TEXTO: {''.join(data['content'][:50])}...")
        print("="*30 + "\n")

        yield data

if __name__ == "__main__":
    settings = {
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "DOWNLOAD_HANDLERS": {
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {
            "headless": True, 
        },
        "LOG_LEVEL": "INFO",
        "FEEDS": {
            "results.json": {"format": "json", "overwrite": True},
        },
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:148.0) Gecko/20100101 Firefox/148.0"
    }

    process = CrawlerProcess(settings=settings)
    process.crawl(XSpider)
    process.start()