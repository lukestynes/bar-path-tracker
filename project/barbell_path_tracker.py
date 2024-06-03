#!/usr/bin/env python3.10

import cv2
import numpy as np
import argparse
import os

midfoot_line_color = (108, 181, 94)
path_line_color = (0, 173, 222)
path_line_dots_color = (0, 106, 197)


def save_points(points, filename):
    """Saves the data of the drawn barbell path as a series of (x, y) coordinate pairs."""
    with open(filename, "w") as file:
        for point in points:
            file.write(f"{point[0]}, {point[1]}\n")


def draw_barbell_path(video_path):
    """Draws the barbell path and does all the other stuff too"""
    # Load the video and check it worked
    cap = cv2.VideoCapture(video_path)
    successful_load, frame = cap.read()

    if not successful_load:
        print("Failed to read video")
        return

    # Display a bounding box selector using the First Frame of the video.
    roi = cv2.selectROI(
        "Select the Region Around the Barbell End",
        frame,
        fromCenter=False,
        showCrosshair=True,
    )
    cv2.destroyWindow("Select the Region Around the Barbell End")

    roi_x_coord, roi_y_coord, roi_width, roi_height = map(int, roi)
    roi_frame = frame[
        roi_y_coord : roi_y_coord + roi_height, roi_x_coord : roi_x_coord + roi_width
    ]

    # Convert ROI to grayscale and apply Gaussian blur
    gray_roi = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)
    gray_roi = cv2.GaussianBlur(gray_roi, (7, 7), 1.5)

    # Detect circles in the ROI
    circles = cv2.HoughCircles(
        gray_roi,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=100,  # distance between circles, high number as only one circle wanted
        param1=50,
        param2=50,  # how stringent the detection is
        minRadius=10,
        maxRadius=30,
    )

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for circle_center_x, circle_center_y, radius in circles:
            # Draw the circle in the ROI
            cv2.circle(
                roi_frame, (circle_center_x, circle_center_y), radius, (0, 255, 0), 2
            )
            cv2.rectangle(
                roi_frame,
                (circle_center_x - 5, circle_center_y - 5),
                (circle_center_x + 5, circle_center_y + 5),
                (0, 128, 255),
                -1,
            )
            initial_point = (
                roi_x_coord + circle_center_x,
                roi_y_coord + circle_center_y,
            )
            break
    else:
        print("No circle was detected in the selected ROI, cannot track barbell.")
        return

    # Store the initial center point for the vertical line
    # Draws the vertical line from this point, so assume user starts with barbell over midfoot in video
    initial_center_x = initial_point[0]

    # Initialize the list to store the barbell path
    barbell_path = [initial_point]

    # Parameters for Lucas-Kanade Algorithm
    lk_params = dict(
        winSize=(21, 21),
        maxLevel=3,
        criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 20, 0.01),
    )

    # Convert the first frame to grayscale
    old_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Create initial points for tracking
    p0 = np.array([[initial_point]], dtype=np.float32)

    # Create a mask image for drawing purposes
    barbell_path_mask = np.zeros_like(frame)

    while True:
        successful_load, frame = cap.read()
        if not successful_load:
            print("Issue loading in the video")
            break

        # Convert the frame to grayscale
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Track the point
        p1, st, err = cv2.calcOpticalFlowPyrLK(
            old_gray, frame_gray, p0, None, **lk_params
        )

        # Select good points
        if st[0][0] == 1:
            new_point = (int(p1[0][0][0]), int(p1[0][0][1]))
            barbell_path.append(new_point)

            # Draw the new points
            barbell_path_mask = cv2.line(
                barbell_path_mask, initial_point, new_point, path_line_color, 5
            )
            initial_point = new_point

        # Tint the frame to make the path easier to see overlayed on video
        tinted_frame = cv2.addWeighted(frame, 0.7, np.zeros_like(frame), 0.3, 0)

        # Display the drawn barbell path
        img = cv2.add(tinted_frame, barbell_path_mask)

        # Draw the vertical line from the initial center point
        # Supposed to be the midfoot line
        img = cv2.line(
            img,
            (initial_center_x, 0),
            (initial_center_x, frame.shape[0]),
            midfoot_line_color,
            2,
        )

        # Display the frame with the dark tint and path
        cv2.imshow("Barbell Path Analyser", img)

        # Update the previous frame and previous points
        old_gray = frame_gray.copy()
        p0 = p1

        if cv2.waitKey(30) & 0xFF == ord("q"):
            break

    # Save the barbell path to a file for analysis
    video_name = os.path.basename(video_path).split(".")[0]
    auto_track_file = f"{video_name}_auto_track.txt"
    save_points(barbell_path, auto_track_file)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Video barbell path tracker")
    parser.add_argument("video_path", help="Path to the video file")
    args = parser.parse_args()

    draw_barbell_path(args.video_path)
