########################################################################################################################
#                                                                                                                      #
#                                             This file is part of kAIvy                                               #
#                                                                                                                      #
#                                      Copyright (c) 2019-2021 by the kAIvy team and contributors                                      #
#                                                                                                                      #
########################################################################################################################


import numpy as np


class Vector2D:
    """
    Two vector functions
    """

    def __init__(self, value):
        """
        Initializer
        :param value: The vector's direction value
        """
        self.value = np.array(value)

    @staticmethod
    def get_vector(start, end):
        """
        Returns a vector from given start coordinate to given end coordinate
        :param start: The vector's start
        :param end: The vector's end
        :return: The vector
        """
        diff = end - start
        return Vector2D(diff)

    def get_length(self):
        """
        Returns the length of this vector
        :return: The length
        """
        return self.get_vector_length(self)

    def normalized(self):
        """
        Returns the normalized version of this vector
        :return: The length
        """
        length = self.get_length()
        return Vector2D(self.value / length if length != 0 else self.value)

    @staticmethod
    def get_vector_length(vector):
        """
        Returns a vector's length
        :param vector: The vector
        :return: The length
        """
        return (vector.value[0] ** 2 + vector.value[1] ** 2) ** 0.5
