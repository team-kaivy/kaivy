########################################################################################################################
#                                                                                                                      #
#                                             This file is part of kAIvy                                               #
#                                                                                                                      #
#                                      Copyright (c) 2019-2021 by the kAIvy team and contributors                                      #
#                                                                                                                      #
########################################################################################################################
"""
    Implements the SimpleTableView component to visualize simple table data with static data assignment
"""

from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.properties import NumericProperty
from kivy.graphics import *


class SimpleTableView(GridLayout):
    """
    A straight forward table view grid with minimal complexity
    """

    ROW_HEIGHT = 30  # The default row height

    header_rows = NumericProperty(0)  # The number of fixed rows
    header_columns = NumericProperty(0)  # The number of fixed columns

    def __init__(self, table_data=None, **kwargs):
        """
        Initializer
        :param table_data: The initial table data
        """
        super().__init__(**kwargs)
        self.background_view_ig = InstructionGroup()
        self.canvas.before.add(self.background_view_ig)
        self.table_rows = 0  # Number of rows
        self.table_cols = 0  # Number of columns
        self.cells = [[]]  # List containing all cells, rows by columns
        self.table_data = None
        self.set_data(table_data if table_data is not None else [[]])
        self.update_background_view()
        self.bind(size=self.update_background_view)
        self.bind(pos=self.update_background_view)
        self.size_hint = (1.0, None)
        self.size = self.get_optimal_size()

    def set_data(self, new_data):
        """
        Sets new data
        :param new_data: The new data, a list of lists defining the table's content
        :return:
        """
        new_rows, new_cols = self.get_list_rows_columns(new_data)
        self.table_data = new_data
        if new_rows != self.table_rows or new_cols != self.table_cols:
            self.rows = self.table_rows = new_rows
            self.cols = self.table_cols = new_cols
            self.recreate_table()
        self.update_cell_content()

    def recreate_table(self):
        """
        Recreates the table's views
        """
        self.clear_widgets()
        self.cells = []
        for row_index in range(self.table_rows):
            row_widgets = []
            for col_index in range(self.table_cols):
                new_label = Label()
                new_label.bold = row_index < self.header_rows or col_index<self.header_columns
                new_label.color = (0, 0, 0, 1)
                self.add_widget(new_label)
                row_widgets.append(new_label)
            self.cells.append(row_widgets)

    def update_cell_content(self):
        """
        Updates the cell content of all cells
        :return:
        """
        # update content
        for row_index, row in enumerate(self.table_data):  # for all rows do...
            for col_index, col in enumerate(row):  # for all columns do...
                label = self.cells[row_index][col_index]
                label.text = str(col)

    @staticmethod
    def get_list_rows_columns(list_data):
        """
        Returns the rows and maximum number in given list
        :param list_data: The list data
        :return: Number of rows, Number of columns
        """
        max_cols = 0
        for row in list_data:
            max_cols = max(max_cols, len(row))
        return len(list_data), max_cols

    def update_background_view(self, _=None, __=None):
        self.background_view_ig.clear()
        self.background_view_ig.add(Color(1, 1, 1, 1))
        self.background_view_ig.add(Rectangle(pos=self.pos, size=list(self.size)))

        if self._rows is not None:
            self.background_view_ig.add(Color(0, 0, 0, 1))
            for i, x, y, w, h in self._iterate_layout(len(self.children)):
                self.background_view_ig.add(Line(rectangle=(x, y, w, h)))

    def get_optimal_size(self):
        return 400, self.table_rows * self.ROW_HEIGHT

    def auto_size(self):
        """
        Sets the own size to the optimal size
        """
        self.size = self.get_optimal_size()