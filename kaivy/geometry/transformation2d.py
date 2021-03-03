########################################################################################################################
#                                                                                                                      #
#                                             This file is part of kAIvy                                               #
#                                                                                                                      #
#                                      Copyright (c) 2019-2021 by the kAIvy team and contributors                                      #
#                                                                                                                      #
########################################################################################################################

import numpy as np


class Transformation2D:
    """
    Defines a two dimensional point transformation
    """

    def __init__(self, offset=(0.0, 0.0), scaling=1.0, rotation=0.0):
        """
        Initializer
        :param offset: The offset
        :param scaling: The scaling
        :param rotation: The rotation in degree
        """
        self.offset = offset      # The offset (X,Y)
        self.scaling = np.array(scaling if isinstance(scaling, tuple) else (scaling, scaling))    # The size scaling for each axis (X,Y)
        self.rotation = rotation  # The rotation, not yet used

    def transform(self, nodes):
        """
        Transforms given set of nodes
        :param nodes: The nodes
        :return: The transformed nodes
        """
        return nodes*self.scaling + self.offset

    def get_line_width_scaling(self):
        """
        Returns the required scaling of lines
        :return: The scaling value
        """
        return np.mean(self.scaling)
