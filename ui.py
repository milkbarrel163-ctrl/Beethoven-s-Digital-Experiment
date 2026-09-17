import pygame
import pygame_gui
from settings import *
class UI:
    def __init__(self,patterns):
        self.manager=pygame_gui.UIManager((WIDTH,HEIGHT))
        self.play_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((25,50),(120,40)),
            text="Play",
            manager=self.manager
        )

        self.save_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((570,50),(100,40)),
            text="Save",
            manager=self.manager
        )

        self.load_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((680,50),(100,40)),
            text="Load",
            manager=self.manager
        )

        self.new_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((25,170),(110,40)),
            text="New",
            manager=self.manager
        )

        self.delete_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((25,220),(110,40)),
            text="Delete",
            manager=self.manager
        )

        self.rename_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((25,270),(110,40)),
            text="Rename",
            manager=self.manager
        )

        self.rename_entry = None
        self.pattern_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=[p["name"] for p in patterns],
            starting_option=patterns[0]["name"],
            relative_rect=pygame.Rect((20,120),(110,40)),
            manager=self.manager
        )
        self.track_list = pygame_gui.elements.UISelectionList(
            relative_rect=pygame.Rect((0,360),(160,160)),
            item_list=[
                "Kick",
                "Snare",
                "HiHat",
                "Piano",
                "Pixels",
                "Synth"
            ],
            manager=self.manager
        )
        
        self.song_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((180, 145), (220, 40)),
            text="Song Arrangement",
            manager=self.manager
        )

        self.song_list = pygame_gui.elements.UISelectionList(
            relative_rect=pygame.Rect((180, 190), (350, 300)),
            item_list=[],
            manager=self.manager
        )

        self.add_song_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((550, 190), (100, 40)),
            text="Add",
            manager=self.manager
        )

        self.remove_song_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((550, 240), (100, 40)),
            text="Remove",
            manager=self.manager
        )

        self.clear_song_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((550, 290), (100, 40)),
            text="Clear",
            manager=self.manager
        )

        self.mode_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((300, 50), (160, 40)),
            text="Song Mode",
            manager=self.manager
        )
        self.show_pattern_mode()
        
    def refresh_pattern_dropdown(self, patterns, current_pattern):

        current_name = patterns[current_pattern]["name"]
        if self.pattern_dropdown is not None:
            self.pattern_dropdown.kill()

        self.pattern_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=[p["name"] for p in patterns],
            starting_option=current_name,
            relative_rect=pygame.Rect((20,120),(110,40)),
            manager=self.manager
        )

    def show_pattern_mode(self):
        self.pattern_dropdown.show()
        self.new_button.show()
        self.delete_button.show()
        self.rename_button.show()
        self.track_list.show()

        self.song_label.hide()
        self.song_list.hide()
        self.add_song_button.hide()
        self.remove_song_button.hide()
        self.clear_song_button.hide()


    def show_song_mode(self):
        self.pattern_dropdown.hide()
        self.new_button.hide()
        self.delete_button.hide()
        self.rename_button.hide()
        self.track_list.hide()
        
        self.song_label.show()
        self.song_list.show()
        self.add_song_button.show()
        self.remove_song_button.show()
        self.clear_song_button.show()
    
    def refresh_song_list(self,state):
        items=[]
        for i,pattern_index in enumerate(state.song["arrangement"]):
                name=state.patterns[pattern_index]['name']
                items.append(f'{i+1}.{name}')
        self.song_list.set_item_list(items)
    def update_play_button(self, playing):
        if playing:
            self.play_button.set_text("Stop")
        else:
            self.play_button.set_text("Play")
