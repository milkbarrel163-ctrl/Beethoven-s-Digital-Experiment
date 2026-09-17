import pygame
from state import GameState
from ui import UI
import tkinter as tk
from tkinter import filedialog
import json
from config import *
import pygame_gui

def handle_add_to_song(state,ui):
    state.song["arrangement"].append(state.current_pattern)
    ui.refresh_song_list(state)

def handle_remove_from_song(state,ui):
    selection=ui.song_list.get_single_selection()
    
    if selection is None:
        return
    
    index = int(selection.split(".")[0])-1
    
    if 0<=index<len(state.song["arrangement"]):
        state.song["arrangement"].pop(index)

    ui.refresh_song_list(state)

def handle_clear_song(state,ui):
    state.song["arrangement"].clear()
    state.song_position=0
    ui.refresh_song_list(state)

def handle_mode_button(state,ui):
    if state.mode=="pattern":
        state.mode="song"
        ui.show_song_mode()
        ui.mode_button.set_text("Pattern Mode")
    else:
        state.mode="pattern"
        ui.show_pattern_mode()
        ui.mode_button.set_text("Song Mode")
        

def handle_button(event,state,ui):
    if event.ui_element == ui.play_button:
        handle_play_button(state,ui)
        
    elif event.ui_element == ui.new_button:
        handle_new_pattern_button(state,ui)
            
    elif event.ui_element == ui.save_button:
        handle_save_button(state)
    elif event.ui_element == ui.load_button:
        handle_load_button(state,ui)
    elif event.ui_element == ui.delete_button:
        handle_delete_button(state,ui)         
    elif event.ui_element == ui.rename_button:
        create_rename_entry(ui)
    elif event.ui_element == ui.add_song_button:
        handle_add_to_song(state,ui)
    elif event.ui_element == ui.remove_song_button:
        handle_remove_from_song(state,ui)
    elif event.ui_element == ui.clear_song_button:
        handle_clear_song(state,ui)
    elif event.ui_element == ui.mode_button:
        handle_mode_button(state,ui)

def handle_play_button(state,ui):
    if not state.playing:
        state.playing=not state.playing
        state.current_step=0
        state.last_step_time=0
        if state.mode=="song":
            state.song_position=0
    else:
        state.playing=False
    ui.update_play_button(state.playing)

def handle_new_pattern_button(state,ui):
    tracks={
        track:[]
        for track in TRACK_INFO
    }
    state.patterns.append({
        "name":f"Pattern {len(state.patterns)+1}",
        "STEPS":32,
        "tracks":tracks
    })
    state.current_pattern=len(state.patterns)-1
    state.update_current_pattern()
    ui.refresh_pattern_dropdown(state.patterns,state.current_pattern)
    

def handle_save_button(state):
    data={"bpm":state.bpm,"patterns":state.patterns,"song":state.song}
    filename=filedialog.asksaveasfilename(title="保存工程",defaultextension=".json",filetypes=[("JSON files","*.json")])
    if filename:
        with open(filename,"w",encoding="utf-8") as f:
            json.dump(data,f,indent=4,ensure_ascii=False)

def handle_load_button(state,ui):
    filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if not filename:
        return
    with open(filename,encoding="utf-8") as f:
        data=json.load(f)
    state.patterns=data["patterns"]
    state.bpm=data["bpm"]
    state.song=data.get("song",[])
    state.current_pattern=0
    state.song_position=0
    state.update_current_pattern()
    ui.refresh_pattern_dropdown(state.patterns,state.current_pattern)

def handle_delete_button(state,ui):
    if len(state.patterns)<=1:
        return
    state.patterns.pop(state.current_pattern)
    state.current_pattern=max(0,state.current_pattern-1)
    state.update_current_pattern()
    ui.refresh_pattern_dropdown(state.patterns,state.current_pattern)

def create_rename_entry(ui):
    if ui.rename_entry is not None:
        return
    ui.rename_entry = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect((20, 270), (150, 30)),
        manager=ui.manager
    )
    ui.rename_entry.focus()
