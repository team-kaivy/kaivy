########################################################################################################################
#                                                                                                                      #
#                                             This file is part of kAIvy                                               #
#                                                                                                                      #
#                                      Copyright (c) 2019-2021 by the kAIvy team and contributors                                      #
#                                                                                                                      #
########################################################################################################################

from kaivy.geometry.geometry2d import Geometry2D
from typing import List


class GeometryProvider:
    """
    The geometry provider is an interface which enables geometry viewers and editors to access geometry data of an
    arbitrary source.
    """

    def __init__(self):
        """
        Initializer
        """
        self.geometry_list: List[Geometry2D] = []  # The geometry data

    def get_geometry(self, region=None) -> List[Geometry2D]:
        """
        Returns the list of all geometries in given region
        :param region: The region to receive. If None is passed all elements will be returned
        :return:
        """
        return self.geometry_list

    def to_dict(self, options={}):
        """
        Stores all elements in a dictionary and returns it
        :param options: The storage options, see Geometry2D.OPTION_
        :return: The dictionary
        """
        element_list = [cur_element.to_dict(options) for cur_element in self.geometry_list]
        result = {'elements': element_list}
        return result
