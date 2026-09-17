from config import *

import random

NOTE_MIN_X=100
NOTE_MAX_X=700
MAX_X_MOVE=180
MIN_X_MOVE=40

CATCH_MAX_GAP=2

CATCH_MIN_NOTES=4

HOLD_MIN_LENGTH=2

def generate_x(last_x=None):
    if last_x is None:
        return random.randint(NOTE_MIN_X,NOTE_MAX_X)
    min_x=max(NOTE_MIN_X,last_x-MAX_X_MOVE)
    max_x=min(NOTE_MAX_X,last_x+MAX_X_MOVE)

    candidates=[x for x in range(min_x,max_x+1,10) if abs(x-last_x)>=MIN_X_MOVE]

    if not candidates:
        return random.randint(min_x,max_x)

    return random.choice(candidates)

def make_tap(time,source,x):
    return{
        "type":"tap",
        "time":time,
        "end_time":time,
        "duration":0,
        "source":source,
        "x":x,
        "state":"pending"
    }

def make_catch(times,source,x):
    return{
        "type":"catch",
        "time":times[0],
        "end_time":times[-1],
        "duration":times[-1]-times[0],
        "source":source,
        "x":x,
        "hit_times":times,
        "hit_index":0,
        "state":"pending"
    }

def make_hold(start_time,end_time,source,pitches,x):
    return{
        "type":"hold",
        "time":start_time,
        "end_time":end_time,
        "duration":end_time-start_time,
        "source":source,
        "x":x,
        "state":"pending"
    }

def find_catch_sections(notes):

    if len(notes)<CATCH_MIN_NOTES:
        return[]

    notes=sorted(notes,key=lambda note:note[0])

    sections=[]

    current=[notes[0]]

    for note in notes[1:]:
        previous=current[-1]

        previous_step=previous[0]
        current_step=note[0]

        gap=current_step-previous_step

        if gap<=CATCH_MAX_GAP:
            
            current.append(note)

        else:

            if len(current)>= CATCH_MIN_NOTES:

                sections.append({
                    "start_step":current[0][0],
                    "end_step":current[-1][0],
                    "notes":current
                })

            current=[note]

    if len(current)>=CATCH_MIN_NOTES:

        sections.append({
            "start_step":current[0][0],
            "end_step":current[-1][0],
            "notes":current
        })

    return sections

def process_pattern(pattern,current_time,step_time,chart):
    tracks=pattern["tracks"]

    tap_events={}
    piano_catch_steps=set()

    for track,notes in tracks.items():
        info=TRACK_INFO[track]
        if info["type"]=="drum":
            if track=="hihat":
                hihat_steps=sorted(step for row,step in notes)
                sections=[]

                if len(hihat_steps)>=CATCH_MIN_NOTES:
                    current_section=[hihat_steps[0]]

                    for step in hihat_steps[1:]:
                        previous_step=current_section[-1]

                        if step-previous_step<=CATCH_MAX_GAP:
                            current_section.append(step)
                        else:
                            if len(current_section)>=CATCH_MIN_NOTES:
                                sections.append(current_section)

                            current_section=[step]
                    if len(current_section)>=CATCH_MIN_NOTES:
                        sections.append(current_section)
                catch_steps=set()

                for section in sections:
                    hit_times=[current_time+step*step_time for step in section]
                    chart.append(
                        make_catch(hit_times,"hihat",None)
                    )

                    catch_steps.update(section)

                for row,step in notes:
                    if step in catch_steps:
                        continue
                    time=current_time+step*step_time

                    if time not in tap_events:
                        tap_events[time]=[]

                    tap_events[time].append(track)
            else:
                for row,step in notes:
                    time =current_time+step*step_time

                    if time not in tap_events:
                        tap_events[time]=[]
                    tap_events[time].append(track)
                    

        elif info["type"]=="instrument":
            if track in ("piano","pixels"):
                active_steps=sorted(set(note[0] for note in notes))
                sections=[]

                if len(active_steps)>=CATCH_MIN_NOTES:
                    current_section=[active_steps[0]]

                    for step in active_steps[1:]:

                        previous_step=current_section[-1]
                        if step-previous_step<=CATCH_MAX_GAP:
                            current_section.append(step)

                        else:
                            if len(current_section)>=CATCH_MIN_NOTES:
                                sections.append(current_section)

                            current_section=[step]
                    if len(current_section)>=CATCH_MIN_NOTES:
                        sections.append(current_section)
                catch_steps=set()
                
                for section in sections:
                    
                    hit_times=[current_time+step*step_time for step in section]
                    chart.append(make_catch(hit_times,track,None))

                    for step in section:
                        catch_steps.add(step)

                        if track=="piano":
                            piano_catch_steps.add(step)
                for note in notes:
                    step,pitch,length=note

                    if step in catch_steps:
                        continue

                    time=(current_time+step*step_time)

                    if length>=HOLD_MIN_LENGTH:
                        end_time=(
                            time+length*step_time
                        )

                        chart.append(
                            make_hold(time,end_time,track,[pitch],None)
                        )
                    else:
                        if time not in tap_events:
                            tap_events[time]=[]
                        tap_events[time].append(track)
    piano_notes=tracks.get("piano",[])
    piano_groups={}
    for note in piano_notes:
        step,pitch,length=note
        if step not in piano_groups:
            piano_groups[step]=[]

        piano_groups[step].append(note)
    for step,chord in piano_groups.items():
        if len(chord)<2:
            continue

        if step in piano_catch_steps:
            continue
        
        pitches=[]
        longest_length=1

        for note in chord:
            step_,pitch,length=note
            pitches.append(pitch)
            longest_length=max(longest_length,length)

        time=(current_time+step*step_time)
        end_time=(time+longest_length*step_time)

        if time in tap_events:
            tap_events[time]=[source for source in tap_events[time] if source!="piano"]
            if not tap_events[time]:
                del tap_events[time]

        chart.append(make_hold(time,end_time,"piano",pitches,None))

    for time,sources in tap_events.items():
        sources=list(set(sources))

        chart.append(make_tap(time,"+".join(sources),None))


def generate_chart(state):
    chart=[]
    current_time=0.0
    
    for pattern_index in state.song["arrangement"]:
        
        pattern=state.patterns[pattern_index]
        
        steps=pattern["STEPS"]
        step_time=60/state.bpm*4/steps
        process_pattern(pattern,current_time,step_time,chart)
        
        current_time+=(steps*step_time)

    chart.sort(key=lambda note:note["time"])

    assign_x_positions(chart)
    
    return chart


def assign_x_positions(chart):
    last_x=None
    placed=[]
    
    for note in chart:

        candidates=list(range(
            NOTE_MIN_X,
            NOTE_MAX_X+1,
            10
        ))

        random.shuffle(candidates)

        placed_flag=False
        
        for x in candidates:
            conflict=False

            for other in placed:
                time_gap=abs(note["time"]-other["time"])
                x_gap=abs(x-other["x"])

                if time_gap<0.2:
                    if x_gap<120:
                        conflict=True
                        break

                if note["type"]=="catch" or other["type"]=="catch":
                    if time_gap<0.3:
                        if x_gap<180:
                            conflict=True
                            break
            if not conflict:
                note["x"]=x
                placed_flag=True
                break

        if not placed_flag:
            note["x"]=generate_x()

        placed.append(note)
