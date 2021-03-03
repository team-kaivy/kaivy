########################################################################################################################
#                                                                                                                      #
#                                             This file is part of kAIvy                                               #
#                                                                                                                      #
#                                      Copyright (c) 2019-2021 by the kAIvy team and contributors                                      #
#                                                                                                                      #
########################################################################################################################

import numpy as np
import math
from kivy.graphics import Line, SmoothLine, Color
from kivy.graphics.tesselator import Tesselator
from kivy.graphics import Mesh
from kaivy.geometry.geometry2d import Geometry2D, Transformation2D


class Arc2D(Geometry2D):
    """
    Defines a two dimensional arc, so a partial ellipse with a defined inner radius, outer radius, start and end angle.
    """

    def __init__(self, center, inner_radius, outer_radius, start_angle, end_angle):
        """
        Initializer
        :param center: The center coordinate
        :param inner_radius: The inner radius (single value or xy tuple)
        :param outer_radius: The inner radius (single value or xy tuple)
        :param start_angle: The start angle in degree
        :param end_angle: The end angle in degree
        """
        super().__init__()
        self.geometry_class_name = 'Arc2D'
        self.center = np.array(center, dtype=np.float)  # The center coordinate
        self.inner_radius = inner_radius  # The inner radius (single value or tuple for X/Y)
        self.outer_radius = outer_radius  # The outer radius (single value or tuple for X/Y)
        self.start_angle = start_angle  # The start angle in degree
        self.end_angle = end_angle  # The end angle in degree
        self.border_color = (1.0, 0.0, 0.0, 1.0)  # The border color as float RGBA
        self.border_size = 1.0  # The border size in pixels
        self.max_segments = 128  # The maximum number of segments
        self.perimeter_segment_relation = 0.125  # The relation between circle perimeter and segments

    @staticmethod
    def get_arc_points(rad, start_degree, end_degree, center, segments=None, backwards=True):
        """
        Returns the points for a partial circle
        :param rad: The radius (single value or xy tuple)
        :param start_degree: The start angle in degree
        :param end_degree: The end angle in degree
        :param center: The center coordinate
        :param segments: The count of segments
        :param backwards: Defines if the points shall be added back to front (starting at end_degree)
        :return: A 1-dimensional list of points
        """

        def add_point(step: int):
            """
            Helper function, adds a point for given iteration step along the arc's curve
            :param step: The step (from 0 to segmentation count)
            :return:
            """
            rad_v = deg_per_seg_rad * step + start_degree
            cv = math.cos(rad_v)
            sv = math.sin(rad_v)
            point_list.append(center[0] + cv * rad[0])
            point_list.append(center[1] + sv * rad[1])

        if not isinstance(rad, tuple) and not isinstance(rad, np.ndarray):
            rad = (rad, rad)
        overall_degree = end_degree - start_degree
        start_degree = math.radians(start_degree - 90.0)
        deg_per_seg_rad = math.radians(overall_degree / segments)
        point_list = []
        if not backwards:
            for index in range(segments + 1):
                add_point(index)
        else:
            for index in range(segments, -1, -1):
                add_point(index)
        return point_list

    def get_optimal_segments(self):
        """
        Returns the optimal count of segments for given arc size
        :return: The count of segments for a given circle perimeter
        """
        segments = int(
            self.outer_radius * math.pi * 2.0 * (
                        self.end_angle - self.start_angle) / 360.0 * self.perimeter_segment_relation + 0.5)
        if segments < 8:
            segments = 8
        if segments > self.max_segments:
            segments = self.max_segments
        return segments

    def render_to_kivy(self, target, transformation: Transformation2D, parameters={}, geometry_out=None):
        if self.start_angle == self.end_angle:
            return

        segments = self.get_optimal_segments()

        point_list = self.get_arc_points(rad=(self.outer_radius, self.outer_radius), start_degree=self.start_angle,
                                         end_degree=self.end_angle,
                                         center=self.center,
                                         segments=segments,
                                         backwards=False)

        if self.inner_radius != 0.0:
            point_list += self.get_arc_points(rad=(self.inner_radius, self.inner_radius),
                                              start_degree=self.start_angle,
                                              end_degree=self.end_angle,
                                              center=self.center,
                                              segments=segments,
                                              backwards=True)
            point_list = point_list + point_list[:2]
        else:
            point_list += [self.center[0], self.center[1]]
            point_list = point_list + point_list[:2]

        transformed = transformation.transform(np.array(point_list).reshape(-1, 2))
        point_list = transformed.flatten().tolist()

        width_scaling = transformation.get_line_width_scaling()

        if self.color[3] != 0.0:  # Inner filling?
            # Tessalate polygon to triangles
            tess = Tesselator()
            tess.add_contour(point_list)

            target_list = None

            if geometry_out is not None:
                if not self.GO_TAG_TRIANGLE_FAN in geometry_out:
                    target_list = geometry_out[self.GO_TAG_TRIANGLE_FAN] = []
                else:
                    target_list = geometry_out[self.GO_TAG_TRIANGLE_FAN]

            if tess.tesselate():
                target.add(Color(*self.color))
                for vertices, indices in tess.meshes:  # Iterate tesselated triangles
                    if target_list is not None:
                        restacked = np.array(vertices).reshape(-1, 2)
                        target_list.append({self.GO_TAG_OWNER: self, self.GO_TAG_TF_INDICES: list(indices),
                                            self.GO_TAG_TF_VERTICES: restacked})
                    target.add(Mesh(
                        vertices=vertices,
                        indices=indices,
                        mode="triangle_fan"
                    ))

        if self.border_color[3] != 0.0 and self.border_size != 0:  # Border visible?
            line_list = None
            if geometry_out is not None:
                self.add_lines_to_geometry_list(geometry_out, transformed)

            target.add(Color(*self.border_color))
            smooth = parameters.get("smooth", True)
            if smooth:
                target.add(SmoothLine(points=point_list[0:-2], width=int(self.border_size * width_scaling + 0.5)))
                target.add(SmoothLine(points=point_list[-4:], width=int(self.border_size * width_scaling + 0.5)))
            else:
                target.add(Line(points=point_list[0:-2], width=int(self.border_size * width_scaling + 0.5)))
                target.add(Line(points=point_list[-4:], width=int(self.border_size * width_scaling + 0.5)))

    def to_dict(self,  options):  # Overrides Geometry2D to_dict
        result = super().to_dict(options)
        result['innerRadius'] = self.inner_radius
        result['outerRadius'] = self.outer_radius
        result['startAngle'] = self.start_angle
        result['endAngle'] = self.end_angle
        result['borderColor'] = list(self.border_color)
        result['borderSize'] = self.border_size
        if options.get(self.OPTION_VISUAL_DETAILS, True):
            result['maxSegments'] = self.max_segments
            result['perimeterSegmentRelation'] = self.perimeter_segment_relation
        return result
