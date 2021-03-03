########################################################################################################################
#                                                                                                                      #
#                                             This file is part of kAIvy                                               #
#                                                                                                                      #
#                                      Copyright (c) 2019-2021 by the kAIvy team and contributors                                      #
#                                                                                                                      #
########################################################################################################################

import numpy as np
from kaivy.geometry.geometry2d import Geometry2D
from kaivy.geometry.transformation2d import Transformation2D
from kivy.graphics import Line, SmoothLine, Color


class Line2D(Geometry2D):
    """
    Defines a simple line defined by two points
    """

    def __init__(self, points, width=1.0, color=(1.0, 1.0, 1.0, 1.0)):
        """
        Initializer
        :param points: The line's points
        """
        super().__init__()
        self.geometry_class_name = 'Line2D'
        self.set_nodes(np.array(points))
        self.smooth = True
        self.color = color
        self.width = width

    def render_to_kivy(self, target, transformation: Transformation2D, parameters={}, geometry_out=None):
        color = parameters.get('color', self.color)
        target.add(Color(*color))
        nodes = transformation.transform(self.nodes)

        if geometry_out is not None:
            if self.GO_TAG_LINE_LIST not in geometry_out:  # add line array if still missing
                geometry_out[self.GO_TAG_LINE_LIST] = []
            geometry_out[self.GO_TAG_LINE_LIST].append({self.GO_TAG_OWNER: self, self.GO_TAG_LINE_LIST_LINES: nodes})

        nodes = nodes.flatten().tolist()

        if self.smooth:
            target.add(SmoothLine(points=nodes, width=self.width))
        else:
            target.add(Line(points=nodes, width=self.width))

    def distance_to_point(self, point, ray=False):
        """
        Returns the distance between this line and given point
        :param point: A 2D coordinate
        :param ray: Defines if the line defines an unbound ray
        """
        return self.line_distance_to_point(self.nodes, point, ray=ray)

    @staticmethod
    def line_distance_to_point(point_list, point, ray=False):
        """
        Returns the distance from line p1 p2 and a given point point
        :param point_list: The line's points as numpy array
        :param point: A 2D coordinate
        :param ray: Defines if the line defines an unbound ray
        :return: The distance to the point and the nearest point. None, None if line is invalid
        """
        # two points define the line
        n = (point_list[1] - point_list[0])
        if np.sum(n) == 0:
            return None, None
        line_length = np.linalg.norm(n)
        n = n / line_length

        ap = point - point_list[0]
        t = ap.dot(n)
        if not ray:
            t = min(max(t, 0), line_length)
        x = point_list[0] + t * n
        # d = (np.cross(ap, n) ** 2).sum()**0.5
        return ((point - x) ** 2).sum() ** 0.5, x

    def to_dict(self,  options):  # Overrides Geometry2D to_dict
        result = super().to_dict(options)
        if options.get(self.OPTION_VISUAL_DETAILS, True):
            result['width'] = self.width
            result['smooth'] = self.smooth
        return result
