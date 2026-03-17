import scrapy
from .base import SpiderBase

class XSpider(SpiderBase):
    name = 'x_spider'

    def start_requests(self):
        urls = ['https://twitter.com/lu_aux_fraises/status/2032707439154348344']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        """Debe retornar un diccionario con los datos extraídos"""
        # 1. Extraemos datos
        data = {
            'url': response.url,
            'title': response.css('title::text').get(),
            'content': response.css('div[data-testid="tweetText"]::text').getall(),
            'image_url': response.css('img.css-9pa8cd::attr(src)').get() or response.css('img[alt="Imagen"]::attr(src)').get()
        }
        
        self.logger.info(f"Procesando: {data}")
        self.logger.info(f"Procesando: {data}")
        
        yield data