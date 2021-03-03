########################################################################################################################
#                                                                                                                      #
#                                             This file is part of kAIvy                                               #
#                                                                                                                      #
#                                      Copyright (c) 2019-2021 by the kAIvy team and contributors                                      #
#                                                                                                                      #
########################################################################################################################
"""
    Implements the MatPlot class to visualize Matplotlib.Plotly charts in Kivy
"""

from kivy.uix.boxlayout import BoxLayout
import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from kaivy.common.advanced_image import AdvancedImage
from kaivy.plots import *
from kaivy.windows.virtual_window import VirtualWindowRootView
from kaivy.vision.color_formats import *


class MatPlotView(BoxLayout, VirtualWindowRootView):
    """
    Displays a matplotlib figure
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_image = None
        matplotlib.use('agg')
        self.figure_data = FigureData()
        self.image_view = AdvancedImage()
        self.add_widget(self.image_view)
        self.refresh_graph()

    def refresh_graph(self):
        """
        Refreshes the graph's content
        """
        fig = self.get_figure()
        self.update_image(fig)
        plt.close()

    def update_image(self, fig):
        """
        Convers the figure data to an image to display it in Kivy
        :param fig: The pyplot figure
        :return:
        """
        fig.canvas.draw()
        img = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
        self.last_image = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        self.last_image = ColorFormatConverter.ensure_format_cv(self.last_image, ColorFormatConverter.BGR,
                                                                bgr_order=False)
        self.image_view.set_image_data(self.last_image)

    def get_figure(self):
        """
        Figure creation function. You may override this with your customized figure creation function
        :return: The pyplot figure
        """
        plt.clf()
        fig = plt.figure()
        self.figure_data.pyplot_visualize(fig)
        return fig

    def get_optimal_size(self):
        """
        Returns the optimum view size in pixels
        :return: The size in pixels as tuple
        """
        return (self.last_image.shape[1], self.last_image.shape[0]) if self.last_image is not None else (100, 100)
