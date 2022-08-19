# frame-game

Code for https://frame-game.herokuapp.com.

### Overview

- Code is written in Python.
- Keypoint generation relies on OpenCV.
- Website is built using plotly Dash.

### Running

1. Setup a virtual environment and install requirements
```
./create_local_env.sh
```
2. Generate keypoint data (if required)
```
python generate_data.py
```
3. Run the site
```
python app.py
```
