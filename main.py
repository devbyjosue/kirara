from modules.spider import run_spider


sample = [
    {
        'url': 'https://twitter.com/AlertaMundoNews/status/2034032012953002006',
        'file_type': 'video',
        'file_format': 'mp4'
    },
    {
        'url': 'https://twitter.com/GeddyJaibo/status/2034337288633606515',
        'file_type': 'image',
        'file_format': 'jpg'
    }
]
def main():
    run_spider(sample)



if __name__ == "__main__":
    main()
