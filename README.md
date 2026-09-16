# Beethoven's Digital Experiment
Python-based rhythm game built with Python and pygame-ce, with a built-in music editor, automatic chart generation and full-keyboard control gameplay

## Overview
Unlike traditional rhythm games with fixed charts, Beethoven's Digital Experiment allows players to generate gameplay experiences from their own musical creations.

Beethoven's Digital Experiment is a rhythm game that allows players to create their own music.
The project explores connection between music creation, chart generation and interactive gameplay.

## Features
- **Built-in Music Editor**
    - BDE features the freedom of arranging custom patterns using multiple instruments
- **Automatic Chart Generation**
    - Converts music created into playable rhythm game charts
    - Supports different types of notes:
      - Tap notes
      - Catch notes
      - Hold notes
- **Full-Keyboard Gameplay**
    - Every key can be used for note interaction
    - Designed for flexible gameplay

##Technologies
- Python
- pygame-ce
- pygame_gui

## Project Structure

```text
|————newgame.py # Main entry point, the main file of the project
|
|————chart.py #chart generation
|————game.py # Gameplay Logic
|————state.py # Gameplay state managing
|————events.py # Keyboard, mouse and gameplay events handling
|
|————audio.py # Audio loading, playback and music management
|————export.py # Exports song for gameplay
|————divide.py # Audio sample processing and segmentation utilities
|————ui.py # UI components
|————button.py # Button events managing
|————draw.py # Rendering and visual elements
|
|————config.py # Global constants and configuration settings
|————settings.py # User and game settings management
|————data.py # data loading and storaging
|
└———audio/ # Sound assets and instrument samples
```

## Future Improvements
- Better chart generation algorithms
- Better difficulty balancing
- Allow users to add instruments themselves
- Better visualization for rhythm patterns

## License
MIT License
