from modules.x_spider import XSpider
from scrapy.crawler import CrawlerProcess


SAMPLE_URL = "https://twitter.com/lu_aux_fraises/status/2032707439154348344"

def main():
    process = CrawlerProcess(settings={
        "FEEDS": {
            "items.json": {"format": "json"}, 
        },
        "LOG_LEVEL": "INFO", 
    })
    process.crawl(XSpider)
    process.start()



if __name__ == "__main__":
    main()
