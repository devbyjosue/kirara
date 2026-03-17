# import scrapy_playwright
# import scrapy


# class SpiderTest(scrapy_playwright.PlaywrightSpider):
#     name = "spider_test"

#     def start_requests(self):
#         yield scrapy.Request(
#             url="https://twitter.com/lu_aux_fraises/status/2032707439154348344",
#             meta={"playwright": True}
#         )

#     def parse(self, response):
#         self.logger.info(f"Page title: {response.css('title::text').get()}")