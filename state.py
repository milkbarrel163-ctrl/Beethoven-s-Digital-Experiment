from settings import *
import pygame
from export import export_song

class GameState:

    def __init__(self):
        self.dragging=False
        self.drag_note=None
        self.patterns = [
            {
                "name": "Pattern 1",
                "STEPS": 32,
                "tracks": {
                    "kick": [],
                    "snare": [],
                    "hihat": [],
                    "piano": [],
                    "pixels": [],
                    "synth": []
                }
            }
        ]

        self.current_pattern = 0

        self.playing = False
        self.current_step = 0
        self.last_step_time = 0

        self.bpm = 120
        self.project_name = "Untitled Song"
        
        self.song = {"arrangement": []}
        self.current_song_index=0
        
        self.current_track = "kick"

        self.running = True

        self.update_current_pattern()
        self.drag_start_step=0
        self.dragging_note = None
        self.resizing_note = None
        self.drag_mode = None
        self.selected_note = None
        self.hover_mode = None
        self.active_notes=[]
        self.piano_scroll=0

        self.mode="pattern"
        self.song_playing=False
        self.song_position=0

        self.audio_file="audio/song.wav"

        self.keys_held=set()
        
        self.game_chart=[]
        self.game_time=0.0
        self.game_start_time=0

        
        self.combo=0
        self.max_combo=0
        self.score=0
        
        self.perfect=0
        self.great=0
        self.good=0
        self.miss=0

        self.game_countdown=False
        self.countdown_start_time=0
        self.countdown_text=""
        
    def toggle_mode(self):
        if self.mode=="pattern":
            self.mode="song"
        else:
            self.mode="pattern"
    
    def update_current_pattern(self):
        self.pattern=self.patterns[self.current_pattern]
        self.tracks=self.pattern["tracks"]
        self.steps=self.pattern["STEPS"]
    @property
    def step_width(self):
        return GRID_WIDTH/self.steps

    def start_game(self):
        from chart import generate_chart
        self.game_chart=generate_chart(self)

        self.combo=0
        self.max_combo=0
        self.score=0
        
        self.perfect=0
        self.great=0
        self.good=0
        self.miss=0

        self.keys_held.clear()

        export_song(self,self.audio_file)
        
        pygame.mixer.music.load(self.audio_file)

        self.countdown_start_time=pygame.time.get_ticks()
        self.game_countdown=True
        self.countdown_text="READY"
        
        self.game_time=0.0

        self.mode="game"
