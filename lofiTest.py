import pafy
import vlc
import time
import sys

def main():
    
    url = "https://www.youtube.com/watch?v=3SeOVVJXOUo"
    video = pafy.new(url) 
    videolink =video.getbestaudio()  
    media = vlc.MediaPlayer(videolink.url)  
    media.play()
    time.sleep(30)
    media.stop()

    return

try:
    main()
    
except KeyboardInterrupt:
    print('Interrupted with Ctrl-C')
    sys.exit(0)