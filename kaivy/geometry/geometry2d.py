########################################################################################################################
#                                                                                                                      #
#                                             This file is part of kAIvy                                               #
#                                                                                                                      #
#                                      Copyright (c) 2019-2021 by the kAIvy team and contributors                                      #
#                                                                                                                      #
########################################################################################################################

import numpy as np
from typing import Tuple
from kaivy.geometry.transformation2d import Transformation2D


class Geometry2D:
    """
    Defines the base class for geometrical data
    """

    # Tags for a geometry out dictionary
    GO_TAG_LINE_LIST = "lineLists"  # Line list geometry out entry
    GO_TAG_TRIANGLE_FAN = "triangleFans"  # Triangle fans defining a polygon
    GO_TAG_OWNER = "owner"  # Owner of an geometry out object
    GO_TAG_LINE_LIST_LINES = "lines"  # Lines of a line list object
    GO_TAG_TF_VERTICES = "vertices"  # Vertices defining a triangle fan
    GO_TAG_TF_INDICES = "indices"  # Indices defining a triangle fan

    OPTION_VISUAL_DETAILS = 'visualDetails'  # Defines if visual details shall be stored

    def __init__(self):
        """
        Initializer
        """
        self.tag = ''  # The geometry's unique tag
        self.geometry_class_name = 'Geometry2D'  # The geometry's unique class name
        self.nodes: np.ndarray = None  # Defines the geometry's points (list of 2D coordinates)
        self.color: Tuple = (1.0, 1.0, 1.0, 1.0)  # Defines the geometry's color

    def get_nodes(self, parameters={}):
        """
        Returns all object nodes
        :param parameters: Optional parameters such as resolution
        :return: The list of nodes
        """
        return self.nodes

    def set_nodes(self, nodes):
        """
        Sets new nodes
        :param nodes: A new set of nodes
        """
        self.nodes = nodes

    def update_node(self, index, value):
        """
        Called to update a single node
        :param index: The node's index
        :param value: The new value
        """
        self.nodes[index] = value

    def move_by(self, distance):
        """
        Moves all nodes in this geometry by given distance
        :param distance: The movement distance
        """
        self.nodes[:] += distance

    def get_editable_nodes(self):
        """
        Shall return all nodes of this object which can be edited by a user
        :return: A list of tuples of the form (self, node_index, node_coordinate, node_color)
        """
        result_list = []
        for index, element in enumerate(self.nodes):
            result_list.append((self, index, element, self.color))
        return result_list

    def add_lines_to_geometry_list(self, geometry_out, points):
        """
        Adds lines to a geometry out list
        :param geometry_out: The geometry dictionary
        :param points: The points of the line strip
        """
        if geometry_out is not None:
            return
        line_list = geometry_out.get(self.GO_TAG_LINE_LIST, None)
        if line_list is None:
            line_list = geometry_out[self.GO_TAG_LINE_LIST] = []
        line_list.append({self.GO_TAG_OWNER: self, self.GO_TAG_LINE_LIST_LINES: points})

    def render_to_kivy(self, target, transformation: Transformation2D, parameters={}, geometry_out=None):
        """
        Called when the geometry shall be rendered to kivy.

        :param target: The target canvas or instruction group.
        :param transformation: The transformation (offset, scaling, rotation)
        :param parameters: Advanced parameters
        :param geometry_out: Optional. A target dictionary which receives lines, polygons and triangles rendered
        object's silhouette.
        Format:
            "lineLists": [
            {
                "owner": The owning geometry object,
                "lines": [List of 2D coordinates]
            }
            ],
            "polygons":
            [
            {
                "owner": The owning geometry object,
                "points": [List of 2D coordinates]
            }
            ],
            "triangleFans":
            [
            {
                "owner": The owning geometry object,
                "vertices": [List of 2D coordinates],
                "indices": [list of indices pointing to coordinates]
            }
            ]
        """
        pass

    def to_dict(self, options):
        """
        Returns the geometry to a dictionary
        :param options: Storage options, see OPTION_
        :return: The geometry stored in a dictionary
        """
        result = {'nodes': self.nodes.tolist(), 'tag': self.tag, 'type': self.geometry_class_name}
        if options.get(self.OPTION_VISUAL_DETAILS, True):
            result['color'] = self.color
        return result
