


def identify_domain(url):
    # print(f"URL recibida para identificación: {url}")
    raw_domain = url.split('//')[1].split('/')[0]
    domain = raw_domain.replace('www.', '').split('.')[0].lower()
    print(f"Dominio identificado ------------------------>: {domain}")
    if domain == 'twitter' or domain == 'x' in url:
        return 'x'
    elif domain == 'instagram' in url:
        return 'instagram'
    elif 'facebook' in url:
        return 'facebook'
    elif domain == 'tiktok' in url:
        return 'tiktok'
    elif domain == 'youtube' in url:
        return 'youtube'
    else:
        return 'unknown'
    
