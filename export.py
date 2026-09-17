from pydub import AudioSegment
from config import TRACK_INFO
from config import PITCHES
import os

def export_song(state,filename="audio/song.wav"):
    song=AudioSegment.silent(duration=0)
    current_time=0.0
    for pattern_index in state.song["arrangement"]:
        pattern=state.patterns[pattern_index]
        steps=pattern["STEPS"]
        tracks=pattern["tracks"]

        step_time=60/state.bpm*4/steps

        pattern_length=steps*step_time

        for track,notes in tracks.items():

            info=TRACK_INFO[track]

            if info["type"]=="drum":
                sound=AudioSegment.from_wav(info["sound_file"])

                for row,step in notes:
                    start_time=(current_time+step*step_time)
                    song=mix_sound(song,sound,start_time*1000)
            elif info["type"]=="instrument":
                for step,pitch,length in notes:
                    pitch_name=PITCHES[pitch]
                    sound_path=os.path.join(
                        info["sound_folder"],
                        f"{track} {pitch_name}.wav"
                    )
                    if not os.path.exists(sound_path):
                        print(
                            "Missing sound:",
                            sound_path
                        )
                        continue
                    sound=AudioSegment.from_wav(sound_path)

                    start_time=(current_time+step*step_time)

                    duration=length*step_time

                    duration_ms=int(duration*1000)

                    if duration_ms<len(sound):
                        sound=sound[:duration_ms]

                    song=mix_sound(
                        song,
                        sound,
                        start_time*1000
                    )
            
        current_time+=pattern_length
    os.makedirs(
        os.path.dirname(filename),
        exist_ok=True
    )
    song.export(
        filename,
        format="wav"
    )

    print("Exported:",filename)

def mix_sound(song,sound,position):
    position=int(position)
    required_length=position+len(sound)

    if len(song)<required_length:
        song+=AudioSegment.silent(
            duration=required_length-len(song)
        )
    return song.overlay(
        sound,
        position=position
    )
