import tkinter as tk
from tkinter import filedialog
import json
import pygame
import pygame_gui
from settings import *
pygame.init()
pygame.mixer.init()
screen=pygame.display.set_mode((WIDTH,HEIGHT))
from data import *
from audio import load_audio
from draw import *
from events import *
from ui import UI
from state import GameState
state=GameState()
ui=UI(state.patterns)
from audio import load_audio
from chart import generate_chart

from game import update_game, draw_game

load_audio()

root=tk.Tk()
root.withdraw()

pygame.display.set_caption("My Rhythm Game")
clock=pygame.time.Clock()


def play_step(step,tracks,step_time_ms,state):

    for track,notes in tracks.items():
        if TRACK_INFO[track]["type"]=="drum":
            for row,col in notes:
                if col!=step:
                    continue
                TRACK_INFO[track]["channel"].play(TRACK_INFO[track]["sound"])
        elif TRACK_INFO[track]["type"]=="instrument":
            for note_step,pitch,length in notes:
                if note_step!=step:
                    continue
                note_name=PITCHES[pitch]
                channel=TRACK_INFO[track]["sound"][note_name].play()
                state.active_notes.append({"channel":channel,"end_time":pygame.time.get_ticks()+length*step_time_ms})

def update_playback(state):
    if state.mode=="pattern":
        update_pattern_playback(state)
    elif state.mode=="song":
        update_song_playback(state)

def update_pattern_playback(state):
    if not state.playing:
        return
    step_time=60/state.bpm*4/state.steps
    now=pygame.time.get_ticks()/1000
    now_ms=pygame.time.get_ticks()
    step_time_ms = (60 / state.bpm * 4 / state.steps) * 1000
    if now-state.last_step_time<step_time:
        return
    for note in state.active_notes[:]:
        if now_ms>=note["end_time"]:
            note["channel"].stop()
            state.active_notes.remove(note)
    play_step(state.current_step,state.tracks,step_time_ms,state)

    state.last_step_time=now
    state.current_step=(state.current_step+1)%state.steps

def update_song_playback(state):
    if not state.playing:
        return
    if not state.song["arrangement"]:
        state.playing=False
        ui.update_play_button(False)
        return
    pattern_index=state.song["arrangement"][state.song_position]
    pattern=state.patterns[pattern_index]
    tracks=pattern["tracks"]
    steps=pattern["STEPS"]
    
    step_time=60/state.bpm*4/steps
    step_time_ms=step_time*1000
    
    now=pygame.time.get_ticks()
    now_seconds=now/1000

    for note in state.active_notes[:]:
        if now>=note["end_time"]:
            note["channel"].stop()
            state.active_notes.remove(note)
    
    if now_seconds -state.last_step_time < step_time:
        return
    play_step(
        state.current_step,
        tracks,
        step_time_ms,
        state
    )

    state.last_step_time=now_seconds
    
    state.current_step+=1
    
    if state.current_step>=steps:
        state.current_step=0
        state.song_position+=1
        if state.song_position>=len(state.song["arrangement"]):
            state.song_position=0
            state.playing=False

            for note in state.active_notes:
                note["channel"].stop()

            state.active_notes.clear()
            
    ui.update_play_button(state.playing)

while state.running:
    time_delta=clock.tick(FPS)/1000.0
    if state.mode=="pattern":
        screen.fill(BLACK)
        ui.manager.update(time_delta)
        handle_events(state,ui)
        draw(screen,state)
        update_piano_cursor(state)
        update_playback(state)
        ui.manager.draw_ui(screen)
    elif state.mode=="song":
        screen.fill(BLACK)
        ui.manager.update(time_delta)
        handle_events(state,ui)
        ui.manager.draw_ui(screen)
        update_playback(state)
        
    elif state.mode=="game":
            screen.fill(BLACK)
            handle_events(state, ui)
            update_game(state)
            draw_game(screen, state)
    
    pygame.display.flip()
    
pygame.quit()
