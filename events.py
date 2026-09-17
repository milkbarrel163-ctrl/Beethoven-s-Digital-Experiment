import pygame
import pygame_gui
from state import GameState
from ui import UI
from config import *
from button import *
from settings import *
from game import handle_game_keydown, handle_game_keyup

def handle_drum_mouse(event,state):
    mx,my = pygame.mouse.get_pos()
    if TRACK_INFO[state.current_track]["type"] != "drum":
        return
    if my < CELL*(TRACK_ROWS[state.current_track]+3):
        return
    if my > CELL*(TRACK_ROWS[state.current_track]+4):
        return
    if mx < 160:
        return
    col=int((mx-160)//state.step_width)
    row=(my-120)//CELL

    if (row,col)in state.tracks[state.current_track]:
        state.tracks[state.current_track].remove((row,col))
    else:
        state.tracks[state.current_track].append((row,col))


def update_piano_cursor(state):
    mx,my=pygame.mouse.get_pos()
    state.hover_mode=None
    if TRACK_INFO[state.current_track]["type"]!="instrument":
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        return
    for note in state.tracks[state.current_track]:
        step,pitch,length=note
        x=160+step*state.step_width
        y=120+pitch*PIANO_CELL-state.piano_scroll
        w=length*state.step_width
        if y <= my <= y+PIANO_CELL:
            if x+w-8 <= mx <= x+w:
                state.hover_mode="resize"
                pygame.mouse.set_cursor(
                    pygame.SYSTEM_CURSOR_SIZEWE
                )
                return
    pygame.mouse.set_cursor(
        pygame.SYSTEM_CURSOR_ARROW
    )


def handle_piano_mouse(event,state):
    if state.drag_mode is not None:
        return
    mx,my=pygame.mouse.get_pos()
    if mx<160:
        return
    if my<120:
        return
    pitch=(my-120+state.piano_scroll)//PIANO_CELL
    step=int((mx-160)//state.step_width)
    if pitch<0 or pitch>=len(PITCHES):
        return
    for note in state.tracks[state.current_track]:
        note_step,note_pitch,length=note
        if note_pitch!=pitch:
            continue
        x=160+note_step*state.step_width
        w=length*state.step_width
        if not (x<=mx<=x+w):
            continue
        if mx>=x+w-8:
            state.selected_note=note
            state.resizing_note=note
            state.drag_mode="resize"
            return
        state.dragging_note=note
        state.drag_mode="move"
        state.selected_note=note
        return
    note=(step,pitch,1)
    for existing_note in state.tracks[state.current_track]:
        if existing_note[0]==step and existing_note[1]==pitch:
            return
    state.tracks[state.current_track].append(note)


def handle_piano_drag(state):
    mx,my=pygame.mouse.get_pos()
    if state.drag_mode=="move":
        old=state.dragging_note
        if old is None:
            return
        new_step=int((mx-160)//state.step_width)
        new_pitch=int((my-120+state.piano_scroll)//PIANO_CELL)
        new_step = max(0,min(state.steps-1,new_step))
        new_pitch = max(0, min(len(PITCHES)-1, new_pitch))
        new_note=(new_step,new_pitch,old[2])
        notes=state.tracks[state.current_track]
        if old not in notes:
            return
        for note in notes:
            if note==old:
                continue
            if note[0]==new_step and note[1]==new_pitch:
                return
        idx=notes.index(old)
        notes[idx]=new_note
        state.dragging_note=new_note
    elif state.drag_mode=="resize":
        old=state.resizing_note
        if old is None:
            return
        step,pitch,length=old
        new_length=int(((mx-160)/state.step_width)-step+1)
        new_length=min(state.steps-step,max(1,new_length))
        notes=state.tracks[state.current_track]
        new_note = (step, pitch, new_length)
        idx=notes.index(old)
        notes[idx]=new_note
        state.resizing_note=new_note
    


def release_piano_drag(state):
    state.dragging_note=None
    state.drag_mode=None
    state.resizing_note=None

def handle_keyboard(event,state):
    if event.key == pygame.K_UP:
        state.bpm += 5
    elif event.key == pygame.K_DOWN:
        state.bpm -= 5

    state.bpm = max(30,min(450,state.bpm))


def handle_selection(event,state,ui):
    if event.ui_element == ui.track_list:
        state.current_track = event.text.lower()

def handle_dropdown(event,state,ui):
    if event.ui_element != ui.pattern_dropdown:
        return
    for i,pattern in enumerate(state.patterns):
        if pattern["name"] == event.text:
            state.current_pattern = i
            state.update_current_pattern()
            break


def handle_text_entry(event,state,ui):
    if event.ui_element!=ui.rename_entry:
        return
    
    new_name=event.text.strip()
    if new_name:
        state.patterns[state.current_pattern]["name"]=new_name
        ui.refresh_pattern_dropdown(state.patterns,state.current_pattern)
    ui.rename_entry.kill()
    ui.rename_entry=None

def handle_mouse(event,state):
    if TRACK_INFO[state.current_track]["type"]=="drum":
        handle_drum_mouse(event,state)
    elif TRACK_INFO[state.current_track]["type"]=="instrument":
        handle_piano_mouse(event,state)

def handle_right_mouse(event,state):
    if TRACK_INFO[state.current_track]["type"]=="drum":
        delete_drum_note(state)
    elif TRACK_INFO[state.current_track]["type"]=="instrument":
        delete_piano_note(state)

def delete_piano_note(state):
    mx,my=pygame.mouse.get_pos()
    if mx<160 or my<120:
        return
    notes=state.tracks[state.current_track]
    for note in notes[:]:
        step,pitch,length=note
        x=160+step*state.step_width
        y=120+pitch*PIANO_CELL-state.piano_scroll
        w=length*state.step_width
        h=PIANO_CELL
        if x<=mx<=x+w and y<=my<=y+h:
            notes.remove(note)
            return

def delete_drum_note(state):
    mx,my=pygame.mouse.get_pos()
    if mx<160:
        return
    row=(my-120)//CELL
    col=int((mx-160)//state.step_width)
    if(row,col) in state.tracks[state.current_track]:
        state.tracks[state.current_track].remove((row,col))

def handle_events(state,ui):
    for event in pygame.event.get():
        ui.manager.process_events(event)
        if event.type == pygame.QUIT:
            state.running=False
        
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            handle_button(event,state,ui)

        elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            handle_text_entry(event,state,ui)

        elif event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            handle_selection(event,state,ui)

        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            handle_dropdown(event,state,ui)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if state.mode == "pattern":
                if event.button == 1:      
                    handle_mouse(event, state)
                elif event.button == 3:    
                    handle_right_mouse(event, state)

        elif event.type == pygame.MOUSEMOTION:
            if state.mode == "pattern":
                if event.buttons[0]:
                    if TRACK_INFO[state.current_track]["type"]=="instrument":
                        handle_piano_drag(state)
                        
        elif event.type == pygame.MOUSEBUTTONUP:
            if state.mode == "pattern":
                if event.button==1:
                    release_piano_drag(state)

        elif event.type == pygame.KEYDOWN:
            state.keys_held.add(event.key)
            if state.mode=="game":
                handle_game_keydown(state)
            elif state.mode in ("pattern","song"):
                if event.key==pygame.K_g:
                    state.start_game()
                else:
                    handle_keyboard(event,state)
        elif event.type==pygame.KEYUP:
            state.keys_held.discard(event.key)
            if state.mode=="game":
                handle_game_keyup(state)

        elif event.type == pygame.MOUSEWHEEL:
            if state.mode == "pattern":
                if TRACK_INFO[state.current_track]["type"]=="instrument":
                    state.piano_scroll-=event.y*PIANO_CELL
                    max_scroll=max(0,min(state.piano_scroll,max(0,len(PITCHES)*PIANO_CELL-GRID_HEIGHT)))
                    state.piano_scroll=max(0,min(state.piano_scroll,max_scroll))
            
