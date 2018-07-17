#!/usr/bin/env python3
# coding: utf-8

"""
By Thomas Oswald
"""

import math
import os


class Recognizer():
    """
    Implementation of the $1 recognition algorithm.
    Wobbrock, J.O., Wilson, A.D. and Li, Y. (2007).
    Gestures without libraries, toolkits or training:
    A $1 recognizer for user interface prototypes.
    Proceedings of the ACM Symposium on User Interface Software
    and Technology (UIST ’07).
    Newport, Rhode Island (October 7-10, 2007). New York: ACM
    Press, pp. 159-168.,
    see also https://depts.washington.edu/aimgroup/proj/dollar/
    """

    def __init__(self, stepsize=64):
        self.stepsize = stepsize
        self.recognize_flag = True
        self.callback = None

    def set_flag(self, needs_recognizing):
        self.recognize_flag = needs_recognizing

    def set_callback(self, callback):
        self.callback = callback

    def recognize(self, points, p_name="None"):
        if len(points) > 1:
            points = self.resample(points)
            points = self.rotate_to_zero(points)
            points = self.scale_to_square(points, 100)
            points = self.translate_to_origin(points)
            # read in templates
            templates = []
            if not os.access("strokes.map", os.F_OK):
                with open("strokes.map", "w"):
                    pass
            with open("strokes.map", "r") as f:
                for line in f.readlines():
                    parts = line.split(":")
                    name = parts[0]
                    print(len(eval(parts[1])))
                    templates.append(
                        {"name": name, "points": eval(parts[1])})
            if templates is not None and len(templates) > 0:
                result = self.compare(points, templates, 100)
                print(p_name)
                if result[0] is not None and self.callback is not None:
                    self.callback(result[0]["name"], result[1], p_name)
                else:
                    self.callback("None", 0, p_name)

    # Takes the points of the unistroke as input.
    # Calculates the distance distance between two points.
    # Returns the calculated points.
    # TODO: 67 und 72 Errors
    def resample(self, points):
        # length of each increment
        inc_length = self.get_path_length(points) / (self.stepsize - 1)
        new_points = []
        new_points.append(points[0])
        whole_distance = 0

        try:
            for idx, point in enumerate(points):
                if idx == 0:
                    continue
                last_pos = points[idx - 1]
                d = self.distance(last_pos, point)
                if whole_distance + d >= inc_length:
                    qx = last_pos[0] + ((inc_length - whole_distance) / d) * \
                        (point[0] - last_pos[0])
                    qy = last_pos[1] + ((inc_length - whole_distance) / d) * \
                        (point[1] - last_pos[1])
                    new_points.append((qx, qy))
                    points.insert(idx, (qx, qy))
                    whole_distance = 0
                else:
                    whole_distance += d
            if len(new_points) == 63:
                new_points.append(points[-1])
            if len(new_points) > 64:
                return new_points[63:]
        except Exception as e:
            print(e)
            print("new points")
            print(len(new_points))
            print(new_points)
        return new_points

    # Gets two points and calculates and returns the distance between them.
    def distance(self, pos1, pos2):
        return math.sqrt((pos1[0] - pos2[0])**2 +
                         (pos1[1] - pos2[1])**2)

    # Gets the unistroke as input.
    # Returns the length of the whole path.
    def get_path_length(self, points):
        length = 0
        for idx in range(1, len(points)):
            length += self.distance(points[idx - 1], points[idx])
        return length

    # Rotate points so their indicative angle is at 0°.
    def rotate_to_zero(self, points):
        c = self.centroid(points)
        radian = math.atan2(c[1] - points[0][1], c[0] - points[0][0])
        new_points = self.rotate_by(points, -radian)
        return new_points

    # Calculates the centroid of points.
    def centroid(self, points):
        xs, ys = zip(*points)
        return sum(xs) / len(xs), sum(ys) / len(ys)

    def rotate_by(self, points, radian):
        c = self.centroid(points)
        new_points = []
        for point in points:
            x = (point[0] - c[0]) * math.cos(radian) - \
                (point[1] - c[1]) * math.sin(radian) + c[0]
            y = (point[0] - c[0]) * math.sin(radian) + \
                (point[1] - c[1]) * math.cos(radian) + c[1]
            new_points.append((x, y))
        return new_points

    # Scales the points to a specified size and returns the new points
    # TODO: y = point[1] * (size / box[1])
    # ZeroDivisionError: float division by zero
    def scale_to_square(self, points, size):
        box = self.bounding_box(points)
        new_points = []
        for point in points:
            x = point[0] * (size / box[0])
            y = point[1] * (size / box[1])
            new_points.append((x, y))
        return new_points

    # https://depts.washington.edu/madlab/proj/dollar/dollar.js
    def bounding_box(self, points):
        min_x = math.inf
        max_x = -math.inf
        min_y = math.inf
        max_y = -math.inf
        for point in points:
            min_x = min(min_x, point[0])
            min_y = min(min_y, point[1])
            max_x = max(max_x, point[0])
            max_y = max(max_y, point[1])
        return (max_x - min_x, max_y - min_y)

    # Translates the points to origin (0, 0)
    # Centroid is now at (0, 0)
    def translate_to_origin(self, points):
        c = self.centroid(points)
        new_points = []
        for p in points:
            x = p[0] + (0 - c[0])
            y = p[1] + (0 - c[1])
            new_points.append((x, y))
        return new_points

    # Compares minimum distances between sample and templates
    # Returns the best matching template
    def compare(self, sample, templates, size):
        b = None
        s_template = None
        theta = math.radians(45)
        theta_delta = math.radians(2)
        for t in templates:
            d = self.distance_at_best_angle(
                sample, t["points"], -theta, theta, theta_delta)
            if b is None:
                b = d
            if d < b:
                b = d
                s_template = t
        score = 1 - b / 0.5 * math.sqrt(size * size + size * size)
        return (s_template, score)

    # Calculates the distances
    def distance_at_best_angle(self, points, template,
                               theta_a, theta_b, theta_c):

        phi = 0.5 * (-1 + math.sqrt(5))
        x1 = phi * theta_a + (1 - phi) * theta_b
        f1 = self.distance_at_angle(points, template, x1)
        x2 = (1 - phi) * theta_a + phi * theta_b
        f2 = self.distance_at_angle(points, template, x2)
        while abs(theta_b - theta_a) > theta_c:
            if f1 < f2:
                theta_b = x2
                x2 = x1
                f2 = f1
                x1 = phi * theta_a + (1 - phi) * theta_b
                f1 = self.distance_at_angle(points, template, x1)
            else:
                theta_a = x1
                x1 = x2
                f1 = f2
                x2 = (1 - phi) * theta_a + phi * theta_b
                f2 = self.distance_at_angle(points, template, x2)
        return min(f1, f2)

    def distance_at_angle(self, points, template, theta):
        points = self.rotate_by(points, theta)
        return self.path_distance(points, template)

    def path_distance(self, a, b):
        d = 0
        length = len(a)
        print(len(a))
        print(len(b))
        for idx in range(length - 1):
            d += self.distance(a[idx], b[idx])
        return d / length
