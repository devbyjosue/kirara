import requests
import os


def download_image(url,filename):
    try:
        with requests.get(url, stream=True, timeout=10) as response:
            response.raise_for_status()


            ##if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(8192):
                    f.write(chunk)
    except Exception as e:
        print(f"Error downloading image: {e}")