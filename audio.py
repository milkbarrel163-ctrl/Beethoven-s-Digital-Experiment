import pygame
import os
from config import TRACK_INFO
from config import PITCHES
def load_audio():
    channel_number=0
    for track,info in TRACK_INFO.items():
        if info["type"]=="drum":
            info["sound"]=pygame.mixer.Sound(
                info["sound_file"]
            )
            info["channel"]=pygame.mixer.Channel(
                channel_number
            )
        elif info["type"]=="instrument":
            info["sound"]={}
            info["channel"]=pygame.mixer.Channel(
                channel_number
            )
            folder=info["sound_folder"]
            for pitch in PITCHES:
                filename=f"{track} {pitch}.wav"
                path=os.path.join(folder,filename)
                if not os.path.exists(path):
                    print(f"Missing sound: {path}")
                    continue
                info["sound"][pitch]=pygame.mixer.Sound(path)
        channel_number+=1

