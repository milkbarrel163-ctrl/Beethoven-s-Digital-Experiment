import pygame
from settings import *
from config import *


NOTE_PENDING="pending"
NOTE_HOLDING="holding"
NOTE_COMPLETED="completed"
NOTE_MISSED="missed"

PERFECT_WINDOW=0.02
GREAT_WINDOW=0.04
GOOD_WINDOW=0.06

HOLD_START_WINDOW=0.15
CATCH_START_WINDOW=0.08
HOLD_END_WINDOW=0.15


def update_game(state):
    if state.game_countdown:
        elapsed=(pygame.time.get_ticks()-state.countdown_start_time)/1000.0

        if elapsed<1.0:
            state.countdown_text="READY"
        elif elapsed<2.0:
            state.countdown_text="3"
        elif elapsed<3.0:
            state.countdown_text="2"
        elif elapsed<4.0:
            state.countdown_text="1"
        elif elapsed<4.5:
            state.countdown_text="GO!"
        else:
            state.game_countdown=False
            state.countdown_text=""
            state.game_start_time=pygame.time.get_ticks()
            pygame.mixer.music.play()
        return
    if state.mode !="game":
        return
    
    state.game_time=pygame.mixer.music.get_pos()/1000.0

    current_time=state.game_time
    
    for note in state.game_chart:

        note_type=note["type"]
        note_state=note["state"]

        if note_state in (NOTE_COMPLETED,NOTE_MISSED):
            continue
        
        if note_type=="tap":
            if note_state==NOTE_PENDING:
                if current_time-note["time"]>GOOD_WINDOW:
                    note["state"]=NOTE_MISSED
                    state.combo=0
                    state.miss+=1
                    print("MISS")

        elif note["type"]=="hold":
            if note_state==NOTE_PENDING:
                if current_time-note["time"]>HOLD_START_WINDOW:
                    note["state"]=NOTE_MISSED
                    state.combo=0
                    state.miss+=1
                    print("MISS HOLD")

            elif note_state==NOTE_HOLDING:
                if current_time>=note["end_time"]:
                    note["state"]=NOTE_COMPLETED
                    state.combo+=1
                    state.perfect+=1
                    state.score+=1000

                    if state.combo>state.max_combo:
                        state.max_combo=state.combo

                    print("HOLD COMPLETE")
        elif note_type=="catch":
            if note_state==NOTE_PENDING:
                while note["hit_index"]<len(note["hit_times"]):
                    hit_time=note["hit_times"][note["hit_index"]]

                    if current_time<hit_time:
                        break
                    if state.keys_held:
                        state.combo+=1
                        state.perfect+=1
                        state.score+=1000

                        if state.combo>state.max_combo:
                            state.max_combo=state.combo

                        print("PERFECT CATCH")

                    else:
                        state.combo=0
                        state.miss+=1

                        print("MISS CATCH")

                    note["hit_index"]+=1

                if note["hit_index"]>=len(note["hit_times"]):
                    note["state"]=NOTE_COMPLETED
            

def handle_game_keydown(state):

    current_time=state.game_time

    best_note=None
    best_difference=float("inf")

    for note in state.game_chart:
        if note["type"]!="tap":
            continue
        if note["state"]!=NOTE_PENDING:
            continue

        difference=abs(note["time"]-current_time)

        if difference<best_difference:
            
            best_difference=difference
            best_note=note

    if best_note is not None:
        if best_difference<=PERFECT_WINDOW:
            judge_tap(state,best_note,"perfect")
            return
        elif best_difference<=GREAT_WINDOW:
            judge_tap(state,best_note,"great")
            return
        elif best_difference<=GOOD_WINDOW:
            judge_tap(state,best_note,"good")
            return

    for note in state.game_chart:
        if note["type"]!="hold":
            continue

        if note["state"]!=NOTE_PENDING:
            continue

        difference=abs(note["time"]-current_time)

        if difference<=HOLD_START_WINDOW:
            note["state"]=NOTE_HOLDING
            print("HOLD START")
            return

def judge_tap(state,note,result):

    note["state"]=NOTE_COMPLETED

    if result=="perfect":

        state.perfect+=1
        state.combo+=1
        state.score+=1000

        print("PERFECT")

    elif result=="great":

        state.great+=1
        state.combo+=1
        state.score+=500

        print("GREAT")

    elif result=="good":

        state.good+=1
        state.combo+=1
        state.score+=250

        print("GOOD")

    if state.combo>state.max_combo:
        state.max_combo=state.combo

def handle_game_keyup(state):
    current_time=state.game_time

    for note in state.game_chart:
        if note["state"]!=NOTE_HOLDING:
            continue
        
        if note["type"]!="hold":
            continue
        
        if current_time>=note["end_time"]-HOLD_END_WINDOW:
            continue

        note["state"]=NOTE_MISSED
        state.combo=0
        state.miss+=1

        print(f"{note['type'].upper()} RELEASED")



def draw_game(screen,state):
    screen.fill((20,20,20))

    current_time=state.game_time

    HIT_Y=500

    pygame.draw.line(
        screen,
        (255,255,255),
        (100,HIT_Y),
        (700,HIT_Y),
        3
    )

    SPEED=300

    if state.game_countdown:
        font=pygame.font.Font(None,100)

        text=font.render(state.countdown_text,True,WHITE)

        rect=text.get_rect(center=(WIDTH//2,HEIGHT//2))

        screen.blit(text,rect)
    
    for note in state.game_chart:

        if note["state"] in ("completed","missed"):
            continue

        note_type=note["type"]

        if note_type=="tap":
            time_until_hit=note["time"]-current_time
            y=HIT_Y-time_until_hit*SPEED

            if -50<=y<=HEIGHT+50:
                TAP_WIDTH=50
                TAP_HEIGHT=6
                x=note["x"]
                rect=pygame.Rect(
                    x-TAP_WIDTH//2,
                    int(y-TAP_HEIGHT//2),
                    TAP_WIDTH,
                    TAP_HEIGHT
                )

                pygame.draw.rect(
                    screen,
                    (255,255,255),
                    rect,
                    border_radius=3
                )
        elif note_type=="hold":
            start_y=(
                HIT_Y-(note["time"]-current_time)*SPEED
            )
            end_y=(
                HIT_Y-(note["end_time"]-current_time)*SPEED
            )
            top=min(start_y,end_y)
            bottom=max(start_y,end_y)

            if bottom<-50 or top>HEIGHT+50:
                continue

            HOLD_WIDTH=30

            x=note["x"]

            
            body_rect=pygame.Rect(
                x-HOLD_WIDTH//2,
                int(top),
                HOLD_WIDTH,
                max(5,int(bottom-top))
            )

            pygame.draw.rect(
                screen,
                (150,150,150),
                body_rect,
                border_radius=5
            )

            if -50<=start_y<=HEIGHT+50:
                HEAD_WIDTH=50
                HEAD_HEIGHT=8

                head_rect=pygame.Rect(
                    x-HEAD_WIDTH//2,
                    int(start_y-HEAD_HEIGHT//2),
                    HEAD_WIDTH,
                    HEAD_HEIGHT
                )

                pygame.draw.rect(
                    screen,
                    (255,255,255),
                    head_rect,
                    border_radius=4
                )
            if -50<=end_y<=HEIGHT+50:
                TAIL_WIDTH=30
                TAIL_HEIGHT=6

                tail_rect=pygame.Rect(
                    x-TAIL_WIDTH//2,
                    int(end_y-TAIL_HEIGHT//2),
                    TAIL_WIDTH,
                    TAIL_HEIGHT
                )

                pygame.draw.rect(
                    screen,
                    (200,200,200),
                    tail_rect,
                    border_radius=3
                )

        elif note_type=="catch":

            for index,hit_time in enumerate(note["hit_times"]):
                if index<note["hit_index"]:
                    continue
                time_until_hit=hit_time-current_time
                y=HIT_Y-time_until_hit*SPEED

                if -50<=y<=HEIGHT+50:
                    CATCH_WIDTH=50
                    CATCH_HEIGHT=6
                    
                    x=note["x"]
                    
                    rect=pygame.Rect(
                        x-CATCH_WIDTH//2,
                        int(y-CATCH_HEIGHT//2),
                        CATCH_WIDTH,
                        CATCH_HEIGHT
                    )

                    pygame.draw.rect(
                        screen,
                        (80,160,255),
                        rect,
                        border_radius=3
                    )

    font=pygame.font.Font(None,36)

    combo_text=font.render(
        f"Combo: {state.combo}",
        True,
        (255,255,255)
    )

    score_text=font.render(
        f"Score: {state.score}",
        True,
        (255,255,255)
    )

    perfect_text=font.render(
        f"Perfect: {state.perfect}",
        True,
        (255,255,255)
    )

    great_text=font.render(
        f"Great: {state.great}",
        True,
        (255,255,255)
    )

    good_text=font.render(
        f"Good: {state.good}",
        True,
        (255,255,255)
    )

    miss_text=font.render(
        f"Miss: {state.miss}",
        True,
        (255,255,255)
    )

    screen.blit(combo_text, (20, 20))
    screen.blit(score_text, (20, 60))
    screen.blit(perfect_text, (20, 100))
    screen.blit(great_text, (20, 140))
    screen.blit(good_text, (20, 180))
    screen.blit(miss_text, (20, 220))
    
    
