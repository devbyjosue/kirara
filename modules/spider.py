import multiprocessing

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy_playwright.page import PageMethod
from utils.identify_domain import identify_domain
import requests
import os
import yt_dlp
import uuid



class XSpider(scrapy.Spider):
    name = 'x_spider'
    file_type = 'video' #| 'image'
    domain = '' #| 'instagram' | 'facebook'

    videos_dir = 'temp/videos'
    imgs_dir = 'temp/imgs'

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(videos_dir, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'download': True,
        'verbose':True,
    }

    def __init__(self, requests=None, *args, **kwargs):
        super(XSpider, self).__init__(*args, **kwargs)
        self.requests_list = requests 

    def start_requests(self, requests=None):
        if self.requests_list is None:
            self.logger.warning("No se proporcionaron URLs")
            return

        for request in self.requests_list:
            self.logger.info(f"Enviando solicitud para: {request.get('url')}")
            self.logger.info(f"Tipo de archivo: {request.get('file_type', 'image')}")
            # self.file_type = 
            try:
                format_t = request.get('file_type', 'image')
                url = request.get('url')

                self.domain = identify_domain(url)
                self.logger.info(f"Dominio identificado: {self.domain}")

                match self.domain:
                    case 'x':
                        yield scrapy.Request(
                            url=url,
                            callback=self.parse,
                            meta={
                                "playwright": True,
                                "playwright_page_methods": [
                                    PageMethod("wait_for_selector", 'video[tabindex="-1"]' if format_t == 'video' else 'img[alt="Image"]' , timeout=20000),
                                ],
                                "format_type": format_t,
                                "save_path": request.get('save_path')
                            }
                        )
                    case 'instagram':
                        yield scrapy.Request(
                            url=url,
                            callback=self.parse,
                            meta={
                                "playwright": True,
                                "playwright_page_methods": [
                                    PageMethod("wait_for_selector", 'video' if format_t == 'video' else 'img' , timeout=20000),
                                ],
                                "format_type": format_t,
                                "save_path": request.get('save_path')
                            }
                        )
                    case 'youtube':
                        yield scrapy.Request(
                            url=url,
                            callback=self.parse,
                            meta={
                                "format_type": format_t,
                                "save_path": request.get('save_path')
                            }
                        )
                    case 'facebook':
                        yield scrapy.Request(
                            url=url,
                            callback=self.parse,
                            meta={
                                "playwright": True,
                                "playwright_page_methods": [
                                    PageMethod("wait_for_selector", 'video' if format_t == 'video' else 'img' , timeout=20000),
                                ],
                                "format_type": format_t,
                                "save_path": request.get('save_path')

                            }
                        )
            except Exception as e:
                self.logger.error(f"Error al enviar solicitud para {request.get('url')}: {e}")

    # def scrap_initialize(self, request):
    #     format_t = request.get('file_type', 'image')
    #     url = request.get('url')

    #     self.domain = identify_domain(url)

    #     match self.domain:
    #         case 'x':
    #             yield scrapy.Request(
    #                 url=url,
    #                 callback=self.parse,
    #                 meta={
    #                     "playwright": True,
    #                     "playwright_page_methods": [
    #                         PageMethod("wait_for_selector", 'video[tabindex="-1"]' if format_t == 'video' else 'img[alt="Image"]' , timeout=20000),
    #                     ],
    #                     "format_type": format_t
    #                 }
    #             )
    #         case 'instagram':
    #             yield scrapy.Request(
    #                 url=url,
    #                 callback=self.parse,
    #                 meta={
    #                     "playwright": True,
    #                     "playwright_page_methods": [
    #                         PageMethod("wait_for_selector", 'video' if format_t == 'video' else '//div[role="button"]//img[alt="Image"]' , timeout=20000),
    #                     ],
    #                     "format_type": format_t
    #                 }
    #             )

    def parse(self, response):
        self.logger.info(f"✅ Renderizado completo para: {response.url}")
        self.domain = identify_domain(response.url)

        format_type = response.meta.get("format_type", "image")

        data = None

        match self.domain:
            case 'x':
                self.logger.info("Procesando contenido de X...")
                data = self.handle_x_file(response, format_type)
            case 'instagram':
                self.logger.info("Procesando contenido de Instagram...")
                data = self.handle_ig_file(response, format_type)
            case 'facebook':
                self.logger.info("Procesando contenido de Facebook...")
                data = self.handle_fb_file(response, format_type)
            case 'youtube':
                self.logger.info("Procesando contenido de YouTube...")
                data = self.handle_yt_file(response, format_type)

        yield data

    def handle_yt_file(self, response, format_type):
        """Tal vez agregar descargar el tumbmail"""
        data = {}
        save_path = response.meta.get("save_path", "")
        if format_type == 'video':
            custom_ydtl_options = self.ydl_opts.copy()
            custom_ydtl_options['outtmpl'] = save_path
            with yt_dlp.YoutubeDL(custom_ydtl_options) as ydl:
                try:
                    info_dict = ydl.extract_info(response.url, download=True)
                    video_url = info_dict.get("url", None)
                    data = {
                        'url': response.url,
                        'title': info_dict.get('title', None) or response.css('title::text').get(),
                        'content': info_dict.get('description', '') or response.css('meta[name="description"]::attr(content)').get() or '',
                        'video_url': video_url,
                    }

                    print("\n" + "="*30)
                    print(f"RESULTADO ENCONTRADO:")
                    print(f"VIDEO: {data['video_url']}")
                    print(f"TEXTO: {data['content'][:50]}...")
                    print("="*30 + "\n")
                    
                except Exception as e:
                    print(f"Error al extraer video de YouTube con yt-dlp: {e}")

        return data
    

    def handle_fb_file(self, response, format_type):
        data = {}
        if format_type == 'video':
            save_path = response.meta.get("save_path", "")
            custom_ydl_opts = self.ydl_opts.copy()
            custom_ydl_opts['outtmpl'] = save_path
            with yt_dlp.YoutubeDL(custom_ydl_opts) as ydl:
                try:
                    info_dict = ydl.extract_info(response.url, download=True)
                    video_url = info_dict.get("url", None)
                    data = {
                        'url': response.url,
                        'title': info_dict.get('title', None) or response.css('title::text').get(),
                        'content': info_dict.get('description', '') or response.css('meta[name="description"]::attr(content)').get() or '',
                        'video_url': video_url,
                    }

                    print("\n" + "="*30)
                    print(f"RESULTADO ENCONTRADO:")
                    print(f"VIDEO: {data['video_url']}")
                    print(f"TEXTO: {data['content'][:50]}...")
                    print("="*30 + "\n")
                    
                except Exception as e:
                    print(f"Error al extraer video de Facebook con yt-dlp: {e}")

        return data

    def handle_ig_file(self, response, format_type):
        data = {}
        if format_type == 'image':
            
            image_url = (
                response.css('article img::attr(src)').get() or 
                response.xpath('//img[contains(@style, "object-fit: cover")]/@src').get() or
                response.css('meta[property="og:image"]::attr(content)').get()
            )
            data = {
                'url': response.url,
                'title': response.css('title::text').get(),
                'content': response.css('div[data-testid="post_message"] ::text').getall(),
                'image_url': image_url,
            }
            print("\n" + "="*30) 
            print(f"RESULTADO ENCONTRADO:")
            print(f"IMAGEN: {data['image_url']}")
            print(f"TEXTO: {''.join(data['content'][:50])}...")
            print("="*30 + "\n")

            if data['image_url']:
                # folder_dir = self.imgs_dir
                # if not os.path.exists(folder_dir):
                #     os.makedirs(folder_dir, exist_ok=True)
                # filename = os.path.basename(data['image_url'].split('/')[-1].split('?')[0])
                # if '.' not in filename:
                #     filename += '.png'

                # complete_path = os.path.join(folder_dir, filename)
                # if os.path.exists(complete_path):
                #     filename = os.path.basename(uuid.uuid4().hex + '_' + filename)

                complete_path = response.meta.get("save_path")
                print(f"Descargando imagen en: {complete_path} ")
                
                self.download_image(data['image_url'], complete_path)

        elif format_type == 'video':
            save_path = response.meta.get("save_path", "")
            custom_ydl_opts = self.ydl_opts.copy()
            custom_ydl_opts['outtmpl'] = save_path
            with yt_dlp.YoutubeDL(custom_ydl_opts) as ydl:
                try:
                    info_dict = ydl.extract_info(response.url, download=True)
                    video_url = info_dict.get("url", None)
                    data = {
                        'url': response.url,
                        'title': info_dict.get('title', None) or response.css('title::text').get(),
                        'content': response.css('div[data-testid="post_message"] ::text').getall(),
                        'video_url': video_url,
                    }

                    print("\n" + "="*30)
                    print(f"RESULTADO ENCONTRADO:")
                    print(f"VIDEO: {data['video_url']}")
                    print(f"TEXTO: {''.join(data['content'][:50])}...")
                    print("="*30 + "\n")
                    
                except Exception as e:
                    print(f"Error al extraer video de Instagram con yt-dlp: {e}")

        return data

    def handle_x_file(self, response, format_type):
        data = {}
        if format_type == 'image':        
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

            if data['image_url']:
                # folder_dir = self.imgs_dir
                # if not os.path.exists(folder_dir):
                #     os.makedirs(folder_dir, exist_ok=True)
                # filename = os.path.basename(data['image_url'].split('/')[-1].split('?')[0])
                # if '.' not in filename:
                #     filename += '.png'

                # complete_path = os.path.join(folder_dir, filename)
                # if os.path.exists(complete_path):
                #     filename = os.path.basename(uuid.uuid4().hex + '_' + filename)
                print(f"Descargando imagen en: {complete_path} ")
                complete_path = response.meta.get("save_path")
                self.download_image(data['image_url'], complete_path)

        elif format_type == 'video':
            save_path = response.meta.get("save_path", "")
            custom_ydl_opts = self.ydl_opts.copy()
            custom_ydl_opts['outtmpl'] = save_path
            with yt_dlp.YoutubeDL(custom_ydl_opts) as ydl:
                try:
                    info_dict = ydl.extract_info(response.url, download=True)
                    video_url = info_dict.get("url", None)
                    data = {
                        'url': response.url,
                        'title': info_dict.get('title', None),
                        'content': response.css('div[data-testid="tweetText"] ::text').getall(),
                        'video_url': video_url,
                    }

                    print("\n" + "="*30)
                    print(f"RESULTADO ENCONTRADO:")
                    print(f"VIDEO: {data['video_url']}")
                    print(f"TEXTO: {''.join(data['content'][:50])}...")
                    print("="*30 + "\n")
                    
                except Exception as e:
                    print(f"Error al extraer video con yt-dlp: {e}")


        return data


    def download_image(self, url,filename):
        try:
            with requests.get(url, stream=True, timeout=10) as response:

                response.raise_for_status()

                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(8192):
                        f.write(chunk)
        except Exception as e:
            print(f"Error downloading image: {e}")


    def download_video(self, url,filename):
        """No audio xdd"""
        try:
            with requests.get(url, stream=True, timeout=10) as response:

                response.raise_for_status()

                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(8192):
                        f.write(chunk)
        except Exception as e:
            print(f"Error downloading image: {e}")


def _run_spider_process(requests):
    if requests is None:
        print("No se proporcionaron solicitudes para el spider.")
        return

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
    try:
        process = CrawlerProcess(settings=settings)
        process.crawl(XSpider, requests=requests)
        process.start()
    except Exception as e:
        print(e)

def run_spider(requests=None):
    print("Iniciando proceso del spider...")
    p = multiprocessing.Process(target=_run_spider_process, args=(requests,))
    p.start()
    p.join()