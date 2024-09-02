# Dixit Bot

A Python-based game-playing bot for a simulated version of the board game [Dixit](https://en.wikipedia.org/wiki/Dixit_(board_game)) that leverages [OpenAI API](https://platform.openai.com/docs) and [OpenCLIP](https://github.com/mlfoundations/open_clip). The project attempts to simulate both the storyteller and non-storyteller player roles. 

## Description

This repo contains different implementations reaching for multiple goals. Graphics, advanced logging, different testing methods, etc. It defines the tools to be used in the project and acts as a playground to develop those tools. The primary tools of this project can be found across different branches and involves:
* `game_logic.py` or `dixit.py`
* `players.py` or `bot.py`/`player.py`/`humanAgent.py`
* `abstractor.py` or `clue_generator`
* `similarity.py`
* `generate_image_caption.py`

*Note*: This repo is not necessarily meant to be run but instead holds the branches meant for experimenting and developing. It provides insight on the overall development process.

The following repos utilize the tools here to conduct research:
* https://github.com/manualdriver/dixitguessbot
* https://github.com/migsaenz/botStoryTeller

## Getting Started

### Dependencies

* Python 3.8 or higher
* Libraries:
    * Typing
    * Pillow
    * open_clip_torch
    * logging
    * time
    * threading
    * OpenAI
* Operating System: Compatible with Windows, macOS, and Linux

### Executing program

Can be run either through:

* `main.py` or `terminal_game.py`  
    * *Dependant on what is the current branch*

## Authors

* Sean Estrella
* Miguel Saenz
* Harold Ellis

## Acknowledgments

* [Dixit Player with Open CLIP](https://www.scirp.org/pdf/jdaip_2023112814012413.pdf)
* [An Internet-assisted Dixit-playing AI](https://dl.acm.org/doi/pdf/10.1145/3555858.3555863)
