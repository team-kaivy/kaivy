########################################################################################################################
#                                                                                                                      #
#                                             This file is part of kAIvy                                               #
#                                                                                                                      #
#                                      Copyright (c) 2019-2021 by the kAIvy team and contributors                                      #
#                                                                                                                      #
########################################################################################################################
"""
    Defines the GraphData, defining a single graph row within a subplot
"""

import math


class GraphData:
    """
    Defines a single graph within a plots, e.g. one of multiple lines
    """

    TYPE_PLOT = 1  # Line plots
    TYPE_SCATTER = 2  # Scatter plots
    TYPE_HISTOGRAM = 3  # Histogram plots

    def __init__(self, graph_type=TYPE_PLOT, x_data=None, y_data=None, plot_data=None):
        """
        Initializer
        :param graph_type: The type of the graph, e.g. plots or scatter, see TYPE_
        :param x_data: The initial x data
        :param y_data: The initial y data
        :param plot_data: The plots parent object
        :param dummy: Defines if dummy data shall be stored
        """
        self.x_axis = x_data  # The x axis' data
        self.y_axis = y_data  # The y axis' data
        self.y_label = None  # The y-axis label
        self.y_label_font_size = 10  # The title font's size
        self.x_lim = (None, None)  # Minimum and maximum x
        self.y_lim = (None, None)  # Minimum and maximum y
        self.x_ticks = None  # The ticks along the x axis
        self.y_ticks = None  # The ticks along the y axis
        self.x_labels = None  # The labels along the x axis
        self.y_labels = None  # The labels along the y axis
        self.plot_data = plot_data
        self.graph_type = graph_type
        # histogram specific
        self.bins = 10

    def pyplot_visualize(self, plot):
        """
        Visualizes the graph in pyplot
        :param plot: The plots
        """
        if self.graph_type == self.TYPE_PLOT:
            plot.plot(self.x_axis)
        elif self.graph_type == self.TYPE_SCATTER:
            plot.scatter(self.x_axis, self.y_axis)
        elif self.graph_type == self.TYPE_HISTOGRAM:
            plot.hist(self.x_axis, bins=self.bins)
        self.py_apply_limits(plot)
        self.py_apply_ticks(plot)

    def py_apply_ticks(self, plot):
        """
        Applies the ticks to the plot
        :param plot: The plot handle
        """
        if self.x_ticks is not None:
            plot.set_xticks(self.x_ticks)
        if self.x_labels is not None:
            plot.set_xticklabels(self.x_labels)
        if self.y_ticks is not None:
            plot.set_yticks(self.y_ticks)
        if self.y_labels is not None:
            plot.set_yticklabels(self.y_labels)

    def py_apply_limits(self, plot):
        """
        Applies the limits to the plot
        :param plot: The plot handle
        """
        if any(x is not None for x in self.x_lim):
            if self.x_lim[0] is not None: # at least left?
                if self.x_lim[1] is not None: # left and right?
                    plot.set_xlim(left=self.x_lim[0], right=self.x_lim[1])
                else:
                    plot.set_xlim(left=self.x_lim[0])
            else:  # just right
                plot.set_xlim(rigt=self.x_lim[1])
        if any(y is not None for y in self.y_lim):
            if self.y_lim[0] is not None:  # at least bottom?
                if self.y_lim[1] is not None:
                    plot.set_ylim(bottom=self.y_lim[0], top=self.y_lim[1])
                else:
                    plot.set_ylim(bottom=self.y_lim[0])
            else:
                plot.set_ylim(top=self.y_lim[1])

    def set_data(self, x = None, y = None):
        """
        Updates the data rows
        :param x: X values
        :param y: Y values
        """
        self.x_axis = x
        self.y_axis = y