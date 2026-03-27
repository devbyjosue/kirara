from utils.identify_domain import identify_domain


if __name__ == "__main__":
    test_urls = [
        'https://twitter.com/AlertaMundoNews/status/2034032012953002006',
        'https://www.instagram.com/reels/DQaYJ16DPna/',
        'https://www.facebook.com/somepage/posts/1234567890',
        'https://www.unknownsite.com/somecontent'
    ]
    for url in test_urls:
        domain = identify_domain(url)
        print(f"URL: {url} -> Dominio identificado: {domain}")
