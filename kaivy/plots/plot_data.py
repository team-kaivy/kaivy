########################################################################################################################
#                                                                                                                      #
#                                             This file is part of kAIvy                                               #
#                                                                                                                      #
#                                      Copyright (c) 2019-2021 by the kAIvy team and contributors                                      #
#                                                                                                                      #
########################################################################################################################
"""
    Defines PlotData class which holds the data of a single sub plots within a figure.
"""

from kaivy.plots.graph_data import *


class PlotData:
    """
    Defines a single plots within a figure
    """

    def __init__(self, figure_data):
        """
        Initializer
        :param figure_data: The parent figure data object
        """
        self.graphs = []  # The single plots to be rendered
        self.figure_data = figure_data

    def pyplot_visualize(self, plot):
        """
        Visualizes the plots using pyplot
        :param plot: The plots handle
        """
        for graph in self.graphs:
            graph.pyplot_visualize(plot)

    def add_graph(self, graph):
        """
        Adds a new graph
        :param graph: The graph
        :return The new graph
        """
        graph.plot_data = self
        self.graphs.append(graph)
        return graph