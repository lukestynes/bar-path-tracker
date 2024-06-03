#!/usr/bin/env python3.10
import cv2
import numpy as np
import argparse
import os

# Global variables
current_frame = None
clicked_point = None
frame_counter = 0
total_frames = 0
clicked_points = []
roi = None


# Mouse callback function to capture the click coordinates
def click_event(event, x, y, flags, param):
    global clicked_point
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_point = (x, y)
        print(f"Point clicked: ({x}, {y})")


def draw_crosshair(img, point, size=20, color=(0, 0, 255), thickness=2):
    x, y = point
    cv2.line(img, (x - size, y), (x + size, y), color, thickness)
    cv2.line(img, (x, y - size), (x, y + size), color, thickness)
    cv2.circle(img, point, size // 2, color, thickness)


def save_points(points, filename):
    with open(filename, "a") as file:
        for point in points:
            file.write(f"{point[0]}, {point[1]}\n")


def main(video_path):
    global \
        current_frame, \
        clicked_point, \
        frame_counter, \
        total_frames, \
        clicked_points, \
        roi

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error opening video file")
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Extract video name and create the points file name
    video_name = os.path.basename(video_path).split(".")[0]
    points_file = f"{video_name}_auto_anno.txt"

    cv2.namedWindow("Video")
    cv2.setMouseCallback("Video", click_event)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_counter += 1
        clicked_point = None

        # Display the first frame to select the ROI
        if frame_counter == 1:
            roi = cv2.selectROI(
                "Select ROI", frame, fromCenter=False, showCrosshair=True
            )
            cv2.destroyWindow("Select ROI")

        # Extract ROI from the frame
        roi_frame = frame[
            int(roi[1]) : int(roi[1] + roi[3]), int(roi[0]) : int(roi[0] + roi[2])
        ]

        # Convert ROI to grayscale and apply Gaussian blur
        gray_roi = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)
        gray_roi = cv2.GaussianBlur(gray_roi, (7, 7), 1.5)

        # Detect circles in the ROI
        circles = cv2.HoughCircles(
            gray_roi,
            cv2.HOUGH_GRADIENT,
            dp=1.2,
            minDist=30,
            param1=50,
            param2=30,
            minRadius=10,
            maxRadius=30,
        )

        # Draw detected circle and update clicked_point
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for circle_center_x, circle_center_y, radius in circles:
                cv2.circle(
                    roi_frame,
                    (circle_center_x, circle_center_y),
                    radius,
                    (0, 255, 0),
                    2,
                )
                cv2.rectangle(
                    roi_frame,
                    (circle_center_x - 5, circle_center_y - 5),
                    (circle_center_x + 5, circle_center_y + 5),
                    (0, 128, 255),
                    -1,
                )
                clicked_point = (
                    int(roi[0] + circle_center_x),
                    int(roi[1] + circle_center_y),
                )
                break

        while True:
            display_frame = frame.copy()

            # Draw the crosshair if a point is selected
            if clicked_point:
                draw_crosshair(display_frame, clicked_point)

            # Display frame counter
            cv2.putText(
                display_frame,
                f"{frame_counter}/{total_frames}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            # Display the current frame
            cv2.imshow("Video", display_frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("n"):
                if clicked_point:
                    clicked_points.append(clicked_point)
                break
            elif key == ord("c"):
                # Clear the current point and allow re-click
                clicked_point = None
            elif key == ord("s"):
                # Save all recorded points and quit
                save_points(clicked_points, points_file)
                cap.release()
                cv2.destroyAllWindows()
                return
            elif key == ord("q"):
                cap.release()
                cv2.destroyAllWindows()
                return

    # Save points when the video ends
    save_points(clicked_points, points_file)
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Video frame click marker")
    parser.add_argument("video_path", help="Path to the video file")
    args = parser.parse_args()

    main(args.video_path)

