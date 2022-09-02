import pafy
import vlc
import time
import sys

def main():
    url = "https://www.youtube.com/watch?v=3SeOVVJXOUo"
    video = pafy.new(url)
    best = video.getbestaudio()
    
    player = vlc.MediaPlayer()
    media = vlc.Media(best.url_https)
    player.set_media(media)
    player.play()

    while True:
        time.sleep(1)

    return

try:
    main()
except KeyboardInterrupt:
    print('Interrupted with Ctrl-C')
    sys.exit(0)