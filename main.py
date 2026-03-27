from modules.spider import run_spider


sample = [
    # {
    #     'url': 'https://twitter.com/AlertaMundoNews/status/2034032012953002006',
    #     'file_type': 'video',
    #     'file_format': 'mp4'
    # },
    # {
    #     'url': 'https://twitter.com/GeddyJaibo/status/2034337288633606515',
    #     'file_type': 'image',
    #     'file_format': 'jpg'
    # },
    # {
    #     'url': 'https://www.instagram.com/reels/DQaYJ16DPna/',
    #     'file_type': 'video',
    #     'file_format': 'mp4'
    # },
    # {
    #     'url':'https://www.instagram.com/shitposthero/p/DWMP3dWDk13/',
    #     'file_type': 'image',
    #     'file_format': 'jpg'
    # }
    # {
    #     'url': 'https://www.facebook.com/100064441644698/videos/pcb.10159944371444699/10159944371389699/',
    #     'file_type': 'video',
    #     'file_format': 'mp4'
    # }
    {
        'url': 'https://youtube.com/shorts/FRI_283DKjQ?si=hSaQN_gjglG5JErz',
        'file_type': 'video',
        'file_format': 'mp4'
    }
    # {
    #     'url': 'https://www.facebook.com/facebook/videos/671204259264003/',
    #     'file_type': 'video',
    #     'file_format': 'mp4'
    # }
]
def main():
    run_spider(sample)



if __name__ == "__main__":
    main()
