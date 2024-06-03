# Barbell Path Visualiser - A Computer Vision Approach

![CleanShot 2024-06-03 at 22 50 04@2x](https://github.com/lukestynes/bar-path-tracker/assets/11674345/5f398b70-4cdc-44cd-994d-f3070387e6d1)


Using OpenCV2 and Python, this project creates an automated barbell tracker and path visualiser.
Using side on footage of weighlifting movements, the end of the barbell

This application was created with [OpenCV2](https://opencv.org/) and [Python3.10](https://www.python.org/downloads/release/python-3100/)

## Author

[Luke Stynes](https://github.com/lukestynes)

## Features

- [x] Barbell end detection
- [x] Automated barbell end tracking and path visualisation

## Run the application

To run the application first install Python3.10, installation using homebrew is shown:
`brew install python@3.10`

Then install the dependencies using:
`python3.10 -m pip install -r dependencies.txt`

From here the application can be run using the following command, with the video to be analysed passed as a command line argument:
`python3.10 barbell_path_tracker.py ../resources/stabilised/squat.mp4`

This will highlight the barbell path in the video, and also save an output file of the extracted bar path coordinate points.
