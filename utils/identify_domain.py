


def identify_domain(url):
    if 'twitter.com' or 'x.com' in url:
        return 'x'
    elif 'instagram.com' in url:
        return 'instagram'
    elif 'facebook.com' in url:
        return 'facebook'
    else:
        return 'unknown'