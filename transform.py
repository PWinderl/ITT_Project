#!/usr/bin/env python3
# coding: utf-8

"""
By Thomas Oswald
"""

from numpy import matrix
from numpy.linalg import solve, inv


class Transform():

    def sort(self, points):
        sorted_x = sorted(points, key=lambda item: item[0])
        if sorted_x[0][1] < sorted_x[1][1]:
            top_left = sorted_x[0]
            bottom_left = sorted_x[1]
        else:
            top_left = sorted_x[1]
            bottom_left = sorted_x[0]

        if sorted_x[2][1] < sorted_x[3][1]:
            top_right = sorted_x[2]
            bottom_right = sorted_x[3]
        else:
            top_right = sorted_x[3]
            bottom_right = sorted_x[2]
        return (top_left, bottom_left, bottom_right, top_right)

    def transform(self, points, output_res, wiimote_point):
        points = self.sort(points)
        A = points[0]
        B = points[1]
        C = points[2]
        D = points[3]

        # Step 1
        source_points_123 = matrix([[A[0], B[0], C[0]],
                                    [A[1], B[1], C[1]],
                                    [1,   1,   1]])

        source_point_4 = [[D[0]],
                          [D[1]],
                          [1]]

        # solve the system of linear equations
        scale_to_source = solve(source_points_123, source_point_4)

        l, m, t = [float(x) for x in scale_to_source]

        # Step 2
        unit_to_source = matrix([[l * A[0], m * B[0], t * C[0]],
                                 [l * A[1], m * B[1], t * C[1]],
                                 [l,      m,    t]])
        A2 = 0, output_res[1]
        B2 = 0, 0
        C2 = output_res[0], 0
        D2 = output_res[0], output_res[1]

        """
        A2 = 0, 0
        B2 = 0, output_res[1]
        C2 = output_res[0], output_res[1]
        D2 = output_res[0], 0
        """

        dest_points_123 = matrix([[A2[0], B2[0], C2[0]],
                                  [A2[1], B2[1], C2[1]],
                                  [1,   1,   1]])

        dest_point_4 = matrix([[D2[0]],
                               [D2[1]],
                               [1]])

        scale_to_dest = solve(dest_points_123, dest_point_4)
        l, m, t = [float(x) for x in scale_to_dest]

        unit_to_dest = matrix([[l * A2[0], m * B2[0], t * C2[0]],
                               [l * A2[1], m * B2[1], t * C2[1]],
                               [l,       m,      t]])

        source_to_unit = inv(unit_to_source)

        source_to_dest = unit_to_dest @ source_to_unit

        x, y, z = [float(w) for w in (source_to_dest @ matrix([[wiimote_point[0]],
                                                               [wiimote_point[1]],
                                                               [1]]))]
        x = x / z
        y = y / z
        return (x, y)
