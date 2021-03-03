########################################################################################################################
#                                                                                                                      #
#                                             This file is part of kAIvy                                               #
#                                                                                                                      #
#                                      Copyright (c) 2019-2021 by the kAIvy team and contributors                                      #
#                                                                                                                      #
########################################################################################################################

import numpy as np
from unittest import TestCase
from kaivy.geometry.vector2d import Vector2D


class Ray2D:
    """
    Defines a two dimensional ray with a given start point and direction
    """

    def __init__(self, start, direction: Vector2D = None, end=None) -> None:
        """
        Creates a ray with given start and direction or end
        :param start: Starting point
        :param direction: Direction
        :param end: End point (alternatively to end)
        """
        self.start = np.array(start)
        if end is not None:
            self.direction: Vector2D = Vector2D.get_vector(start=np.array(start), end=np.array(end))
        else:
            self.direction: Vector2D = Vector2D(direction) if not isinstance(direction, Vector2D) else direction
        self.length = self.direction.get_length()

    def normalize(self) -> None:
        """
        Normalizes the ray to a length of 1
        """
        self.direction = self.direction.normalized()
        self.length = 1.0

    def normalized(self) -> 'Ray2D':
        """
        Returns the normalized ray of this one with a length of 1
        """
        return Ray2D(self.start, self.direction.normalized())

    def point_on_ray(self, distance) -> np.ndarray:
        """
        Returns a point on the ray at given
        :param distance: The distance from the starting point, may also be negative
        :return: The point on the ray
        """
        if self.length == 1.0:
            return self.start + self.direction.value * distance
        else:
            return self.start + self.direction.value * distance / self.length

    def parallel(self, other, tolerance=1E-5) -> bool:
        """
        Returns if another ray is nearly parallel to this ray
        :param other: The other ray
        :param tolerance: The comparison tolerance
        :return: True if the condition is met
        """

        def det(x_dirs, y_dirs) -> float:
            """
            Returns the determinant defined by vectors x_diff and y diff, holding the x and y differences of two rays
            :param x_dirs: Contains the x difference of a vector a and b
            :param y_dirs: Contains the y difference of a vector a and b
            :return: The determinant
            """
            return x_dirs[0] * y_dirs[1] - x_dirs[1] * y_dirs[0]

        x_diff = (self.direction.value[0], other.direction.value[0])
        y_diff = (self.direction.value[1], other.direction.value[1])
        div = det(x_diff, y_diff)
        return abs(div) < tolerance

    @classmethod
    def ray_ray_intersection(cls, ras, rad, rbs, rbd, return_coordinate=False):
        """
        Calculates the intersection of two 2D rays
        :param ras: Ray A start coordinate
        :param rad: Ray A direction
        :param rbs: Ray B start coordinate
        :param rbd: Ray B direction
        :param return_coordinate: Defines if also the intersection coordinate shall be returned
        :return: None values if the lines are parallel. ([IntersectionCoordinate], U, V]) on success. U and V
        represent the percentual scaling of the directions of both rays, so the intersection point is ras+u*rad and
        rbs+v*rbd.
        """
        # Source Peter Mortensen: https://stackoverflow.com/questions/2931573/determining-if-two-rays-intersect
        dx = rbs[0] - ras[0]
        dy = rbs[1] - ras[1]
        det = rbd[0] * rad[1] - rbd[1] * rad[0]
        if det == 0:
            return None, None, None if return_coordinate else (None, None)
        u = (dy * rbd[0] - dx * rbd[1]) / det
        v = (dy * rad[0] - dx * rad[1]) / det
        return (ras + u * rad, u, v) if return_coordinate else (u, v)

    def intersection(self, other: 'Ray2D', return_coordinate=False):
        """
        Tests if this ray intersects with another
        :param other: The other ray
        :param return_coordinate: Returns if the coordinate shall be returned as well.
        :return: ([Coordinate], Percental position on this ray, Percental position on other's ray), ([None], None, None)
        if failed
        """
        return self.ray_ray_intersection(self.start, self.direction.value, other.start, other.direction.value,
                                         return_coordinate=return_coordinate)


class _TestRay2D(TestCase):
    """
    Unit tests for class Ray2D
    """

    rayA = Ray2D(start=(50, 100), end=(400, 300))  # Construction with start and end
    rayB = Ray2D(start=[200, 20], direction=Vector2D([100, 800]))  # Construction with start and direction
    rayC = Ray2D(start=[300, 80], direction=Vector2D([100, 800]))  # Parallel to B, just a bit offset
    rayD = Ray2D(start=[300, 80], direction=Vector2D([-100, -800]))  # Parallel to B&C, inverse
    rayE = Ray2D(start=[200, 300], direction=Vector2D([100, 500]))  # Ray below Ray A which would hit it "backwards"

    def test_basic_function(self):
        """
        Tests the basic functionality
        :return:
        """
        self.assertGreater(self.rayA.direction.value[0], self.rayA.direction.value[1],
                           "X increment should be slightly greater")

    def test_normalizing(self):
        """
        Tests the normalization functions
        """
        normalized_val = self.rayB.direction.normalized()
        squared_sum = np.sum(normalized_val.value ** 2)
        self.assertAlmostEqual(squared_sum ** 0.5, 1.0, msg="Normalized vector length should be one")
        norm_b = self.rayB.normalized()
        self.assertAlmostEqual(np.sum((normalized_val.value - norm_b.direction.value) ** 2) ** 0.5, 0.0)
        norm_b_2 = Ray2D(start=self.rayB.start, direction=self.rayB.direction)
        norm_b_2.normalize()
        self.assertAlmostEqual(np.sum((normalized_val.value - norm_b_2.direction.value) ** 2) ** 0.5, 0.0)

    def test_parallelism(self):
        """
        Tests the parallelism functions
        :return:
        """
        self.assertTrue(self.rayB.parallel(self.rayC), "Rays should be recognized as parallel")
        self.assertFalse(self.rayB.parallel(self.rayA), "Rays are not parallel")
        self.assertTrue(self.rayB.parallel(self.rayD), "Rays is parallel but flipped")

    def test_intersection(self):
        """
        Tests the intersection functions
        :return:
        """
        u, v = self.rayA.intersection(self.rayB)
        self.assertGreaterEqual(u, 0)
        self.assertLessEqual(u, 1.0)
        self.assertGreaterEqual(v, 0)
        self.assertLessEqual(v, 1.0)
        coordinate_from_u = self.rayA.start + self.rayA.direction.value * u
        coordinate_from_v = self.rayB.start + self.rayB.direction.value * v
        coordinate, _, _ = self.rayA.intersection(self.rayB, return_coordinate=True)
        coordinate_from_point_on_ray = self.rayA.point_on_ray(u * self.rayA.length)
        # All result coordinates should be equal
        self.assertAlmostEqual(coordinate_from_u[0], coordinate[0])
        self.assertAlmostEqual(coordinate_from_u[1], coordinate[1])
        self.assertAlmostEqual(coordinate_from_v[0], coordinate[0])
        self.assertAlmostEqual(coordinate_from_v[1], coordinate[1])
        self.assertAlmostEqual(coordinate_from_point_on_ray[0], coordinate[0])
        self.assertAlmostEqual(coordinate_from_point_on_ray[1], coordinate[1])
