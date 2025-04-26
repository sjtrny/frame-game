# frame-game

Code for https://frame-game.sjtrny.com/

### Overview

- Code is written in Python.
- Keypoint generation relies on OpenCV.
- Website is built using plotly Dash.

# Instructions

## Build

`docker build -t frame-game .`

## Run

`docker run --name frame-game -d -p 8080:80 frame-game`

## tar

`tar --exclude-vcs -czf file.tar --exclude file.tar .`
