# Barbell Path Visualiser - A Computer Vision Approach
_This was produced for COSC428: Computer Vision_

![CleanShot 2024-06-03 at 22 56 48@2x](https://github.com/lukestynes/bar-path-tracker/assets/11674345/2720af91-b174-4f98-8ef7-e8e67a50fd65)


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

## Manual Annotation
If you wish to annotate the barbell centres manually on a video you can do so by running, replacing `path_to_video` with the relevant path:
`python3.10 barbell_path_tracker.py path_to_video`

## Viewing Metrics
Once you have a manual and automated tracked video data set you can compare the two by using the following, replacing `path_to_manual` with the manual marked data file, and `path_to_auto` with the automatically generated data file:
`python3.10 metrics.py path_to_manual path_to_auto`
