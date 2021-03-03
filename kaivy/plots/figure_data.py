########################################################################################################################
#                                                                                                                      #
#                                             This file is part of kAIvy                                               #
#                                                                                                                      #
#                                      Copyright (c) 2019-2021 by the kAIvy team and contributors                                      #
#                                                                                                                      #
########################################################################################################################
"""
    Defines FigureData - a graph view consisting of one or multiple plots
"""

from kaivy.plots.plot_data import *
import matplotlib.pyplot as plt

class FigureData:
    """
    Defines the complete data set of a figure consisting of one or more plots
    """

    def __init__(self, columns=1, rows=1):
        """
        Initializer
        :param columns: The number of columns
        :param rows: The number of rows
        """
        # graph properties
        self.title = None  # The graph's title, can be set to None
        self.title_font_size = 10  # The title font's size
        self.plots = [PlotData(self)]  # The data for the single sub plots
        self.columns = columns  # The mumber of plots
        self.rows = rows  # The number of rows

    def pyplot_visualize(self, figure):
        """
        Visualizes the figure
        :param figure: The pyplot figure
        """

        if self.title is not None:
            plt.title(self.title)

        for index, cur_plot in enumerate(self.plots):
            plot = figure.add_subplot(self.rows, self.columns, index + 1)
            cur_plot.pyplot_visualize(plot)