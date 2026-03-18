import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy_playwright.page import PageMethod
from utils.identify_domain import identify_domain
import requests
import os
import yt_dlp


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
        'ffmpeg_location': r"C:\\Users\\v81137\\AppData\\Local\\Microsoft\WinGet\\Packages\\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\\ffmpeg-8.1-full_build\\bin"
    }

    def start_requests(self):
        urls = [
            'https://twitter.com/AlertaMundoNews/status/2034032012953002006'
        ]
        
        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", 'img[alt="Image"]' if self.file_type == 'image' else 'video[tabindex="-1"]', timeout=10000),
                    ],
                }
            )


    def parse(self, response):
        self.logger.info(f"✅ Renderizado completo para: {response.url}")
        self.domain = identify_domain(response.url)

        data = None

        match self.domain:
            case 'x':
                self.logger.info("Procesando contenido de X...")
                data = self.handle_x_file(response)
            case 'instagram':
                pass
            case 'facebook':
                pass
            case 'youtube':
                pass

        yield data


    def handle_x_file(self, response):
        data = {}
        if self.file_type == 'image':        
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
                folder_dir = self.imgs_dir
                if not os.path.exists(folder_dir):
                    os.makedirs(folder_dir, exist_ok=True)
                filename = os.path.basename(data['image_url'].split('/')[-1].split('?')[0])
                if '.' not in filename:
                    filename += '.png'

                complete_path = os.path.join(folder_dir, filename)
                print(f"Descargando imagen en: {complete_path} ")
                
                self.download_image(data['image_url'], complete_path)

        elif self.file_type == 'video':
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
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

                    if data['video_url']:
                        folder_dir = self.videos_dir
                        if not os.path.exists(folder_dir):
                            os.makedirs(folder_dir, exist_ok=True)
                        filename = os.path.basename(data['video_url'].split('/')[-1].split('?')[0])
                        if '.' not in filename:
                            filename += '.mp4'

                        complete_path = os.path.join(folder_dir, filename)
                        print(f"Descargando video en: {complete_path} ")
                        
                        # self.download_video(data['video_url'], complete_path)

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


def run_spider():
    settings = {
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "DOWNLOAD_HANDLERS": {
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {
            "headless": False, 
        },
        "LOG_LEVEL": "INFO",
        "FEEDS": {
            "results.json": {"format": "json", "overwrite": True},
        },
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:148.0) Gecko/20100101 Firefox/148.0"
    }
    try:
        
        process = CrawlerProcess(settings=settings)
        process.crawl(XSpider)
        process.start()
    except Exception as e:
        print(e)