#!/usr/bin/env python3

import numpy as np
import argparse
import os
import math


def load_points(filename):
    points = []
    with open(filename, "r") as file:
        for line in file:
            try:
                x, y = map(int, line.strip().split(","))
                points.append((x, y))
            except ValueError:
                print(f"Skipping invalid line in {filename}: {line.strip()}")
    return points


def interpolate_missing_points(points):
    valid_points = [(i, p) for i, p in enumerate(points) if p is not None]
    if not valid_points:
        return points  # If no valid points, return as is

    x_vals, y_vals = zip(*[p for _, p in valid_points])
    indices, valid_points = zip(*valid_points)

    interp_x = np.interp(range(len(points)), indices, x_vals)
    interp_y = np.interp(range(len(points)), indices, y_vals)

    return [(int(x), int(y)) for x, y in zip(interp_x, interp_y)]


def synchronize_points(manual_points, auto_points):
    max_len = max(len(manual_points), len(auto_points))
    manual_points.extend([None] * (max_len - len(manual_points)))
    auto_points.extend([None] * (max_len - len(auto_points)))

    manual_points = interpolate_missing_points(manual_points)
    auto_points = interpolate_missing_points(auto_points)

    return manual_points, auto_points


def euclidean_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def calculate_metrics(manual_points, auto_points, threshold=10):
    manual_points, auto_points = synchronize_points(manual_points, auto_points)

    distances = [
        euclidean_distance(m, a) for m, a in zip(manual_points, auto_points) if m and a
    ]
    if not distances:
        raise ValueError("No valid points to compare")

    average_deviation = np.mean(distances)
    std_deviation = np.std(distances)
    max_deviation = np.max(distances)
    failure_rate = (np.sum(np.array(distances) > threshold) / len(distances)) * 100

    stability = [
        euclidean_distance(auto_points[i], auto_points[i - 1])
        for i in range(1, len(auto_points))
        if auto_points[i] and auto_points[i - 1]
    ]
    average_stability = np.mean(stability) if stability else float("nan")

    return {
        "average_deviation": average_deviation,
        "std_deviation": std_deviation,
        "max_deviation": max_deviation,
        "failure_rate": failure_rate,
        "average_stability": average_stability,
    }


def display_metrics(metrics):
    print(f"Average Deviation: {metrics['average_deviation']:.2f}")
    print(f"Standard Deviation: {metrics['std_deviation']:.2f}")
    print(f"Maximum Deviation: {metrics['max_deviation']:.2f}")
    print(f"Failure Rate: {metrics['failure_rate']:.2f}%")
    print(f"Average Stability: {metrics['average_stability']:.2f}")


def main(manual_file, auto_file, threshold):
    manual_points = load_points(manual_file)
    auto_points = load_points(auto_file)
    metrics = calculate_metrics(manual_points, auto_points, threshold)
    display_metrics(metrics)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate tracking metrics")
    parser.add_argument("manual_file", help="Path to the manual annotation file")
    parser.add_argument("auto_file", help="Path to the automatic annotation file")
    parser.add_argument(
        "--threshold",
        type=float,
        default=10,
        help="Threshold for failure rate calculation",
    )
    args = parser.parse_args()

    main(args.manual_file, args.auto_file, args.threshold)
