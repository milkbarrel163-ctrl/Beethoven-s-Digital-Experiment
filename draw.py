import pygame
from settings import *
from config import *

def draw_grid(screen,state):
    if TRACK_INFO[state.current_track]["type"]!="drum":
        return
    for x in range(state.steps):
        for y in range(10):
            pygame.draw.rect(
                screen,
                (100,100,100),
                (
                160+x*state.step_width,
                120+y*CELL,
                state.step_width,
                CELL
                ),
                1
            )


def draw_notes(screen,state):
    for track,notes in state.tracks.items():
        if TRACK_INFO[track]["type"]!="drum":
            continue
        for row,col in notes:
            pygame.draw.rect(
                screen,
                TRACK_INFO[track]["color"],
                (
                160+col*state.step_width,
                120+row*CELL,
                state.step_width,
                CELL
                )
            )
            
def draw_playhead(screen,state):
    height=GRID_HEIGHT
    if TRACK_INFO[state.current_track]["type"]=="instrument":
        height = len(PITCHES)*PIANO_CELL
    if not state.playing:
        return
    pygame.draw.rect(screen,WHITE,(160+state.current_step*state.step_width,120,state.step_width,GRID_HEIGHT),4)

def draw_current_track(screen,state):
    colors = {"kick": (200,200,0),"snare": (0,200,200),"hihat": (255,100,100)}
    if state.current_track in colors:
        pygame.draw.rect(screen,colors[state.current_track],(160,CELL*(TRACK_ROWS[state.current_track]+3),GRID_WIDTH,CELL),3)

def draw_text(screen,state):
    font=pygame.font.Font(None,30)
    text=font.render(f"BPM:{state.bpm}",True,WHITE)
    screen.blit(text,(600,20))

def draw_drum_editor(screen,state):
    draw_grid(screen,state)
    draw_notes(screen,state)
    draw_current_track(screen,state)

def draw_piano_editor(screen,state):
    draw_piano_grid(screen,state)
    old_clip=screen.get_clip()
    screen.set_clip(pygame.Rect(160,120,GRID_WIDTH,GRID_HEIGHT))
    draw_piano_notes(screen,state)
    screen.set_clip(old_clip)

def draw_piano_grid(screen,state):
    for track,notes in state.tracks.items():
        if TRACK_INFO[track]["type"] != "instrument":
            continue
        for x in range(state.steps):
            for y in range(len(PITCHES)):
                pygame.draw.rect(screen,(80,80,80),(160+x*state.step_width,120+y*PIANO_CELL-state.piano_scroll,state.step_width,PIANO_CELL),1)
    font=pygame.font.Font(None,18)

    for i,pitch in enumerate(PITCHES):
        text=font.render(pitch,True,WHITE)
        screen.blit(text,(20,120+i*PIANO_CELL-state.piano_scroll))
            
def draw_piano_notes(screen,state):
    track=state.current_track
    for note in state.tracks[track]:
        step,pitch,length=note
        x=160 + step*state.step_width
        y=120 + pitch*PIANO_CELL-state.piano_scroll
        w=state.step_width*length
        h=PIANO_CELL
        pygame.draw.rect(
            screen,
            TRACK_INFO[track]["color"],
            (x,y,w,h)
        )
        if note==state.selected_note:
            pygame.draw.rect(
                screen,
                WHITE,
                (x,y,w,h),
                3
            )
    
def draw(screen,state):
    if TRACK_INFO[state.current_track]["type"]=="drum":
        draw_drum_editor(screen,state)
    elif TRACK_INFO[state.current_track]["type"]=="instrument":
        draw_piano_editor(screen,state)
    draw_playhead(screen,state)
    draw_text(screen,state)
