########################################################################################################################
#                                                                                                                      #
#                                             This file is part of kAIvy                                               #
#                                                                                                                      #
#                                      Copyright (c) 2019-2021 by the kAIvy team and contributors                                      #
#                                                                                                                      #
########################################################################################################################

import numpy as np


class Polygon2D:
    """
    Defines a two dimensional polygon

    In progress.
    """

    @staticmethod
    def get_bounding_coords(points):
        """
        Returns the bounding of a given set of points
        :param points: A numpy point array
        :return: The bounding in form of minX, minY, maxX, maxY
        """
        if points is None or len(points) == 0:
            return None
        return np.min(points[:, 0]), np.min(points[:, 1]), np.max(points[:, 0]), np.max(points[:, 1])
