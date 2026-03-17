from abc import ABC, abstractmethod
import scrapy

class SpiderBase(scrapy.Spider, ABC):
    custom_settings = {
        'USER_AGENT' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:148.0) Gecko/20100101 Firefox/148.0'
    }
    
    # @abstractmethod
    def __init__(self, *args, **kwargs):
        super(SpiderBase, self).__init__(*args, **kwargs)

    @abstractmethod
    def start_requests(self):
        pass