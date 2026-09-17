from pydub import AudioSegment
from config import *
audio=AudioSegment.from_wav("synth.wav")
for i in range(36):
    note=audio[i*1000:(i+1)*1000]
    note.export(f"synth {PITCHES[36-i-1]}.wav",format="wav")
