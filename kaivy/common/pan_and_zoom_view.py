########################################################################################################################
#                                                                                                                      #
#                                             This file is part of kAIvy                                               #
#                                                                                                                      #
#                                      Copyright (c) 2019-2021 by the kAIvy team and contributors                                      #
#                                                                                                                      #
########################################################################################################################

import time
from kivy.uix.stencilview import StencilView
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Rectangle, Color, Line, SmoothLine
from kivy.graphics.scissor_instructions import ScissorPush, ScissorPop
from kivy.clock import Clock
from kaivy.geometry.geometry_provider import GeometryProvider
from kaivy.geometry.geometry2d import Geometry2D, Transformation2D
from kaivy.geometry.line2d import Line2D
import numpy as np


class PanAndZoomView(StencilView, FloatLayout):
    """
    The pan and zoom view is able to store another Widget such as an Image and make it pannable and zoomable.
    The embedded view has to provide a function named get_original_image_size which returns it's origin size in pixels.

    Events:
        - on_geometry_moved(geometry) - When ever a geometry was moved
    """

    DRAGGING_MODE_OFF = 0  # No panning active
    DRAGGING_MODE_PAN = 1  # Moving view
    DRAGGING_MODE_NODE = 2  # Moving a node
    DRAGGING_MODE_OBJECT = 3  # Moving an object

    EDIT_GEOMETRY_NODES = 1  # May edit nodes?
    EDIT_GEOMETRY_OBJECTS = 2  # May edit objects?

    def __init__(self, **kwargs):
        """
        Initializer
        :param kwargs: Configuration properties
        """
        super().__init__(**kwargs)
        self.dynamic_widget = None
        self.pan_zoom = 1.0
        self.bind(size=self.on_size_changed)
        self.current_size = [1, 1]
        self.fit_size = True
        self.may_zoom = True
        self.scroll_speed = 1.2
        self.fit_zoom = 1.0
        self.max_zoom = 32.0
        self.size_check_timer = Clock.schedule_interval(self.verify_size,
                                                        0.5)  # regularly verifies if the size has changed

        # dragging variables
        self.pan_offset = (0, 0)
        self.last_drag_pos = (0, 0)
        self.drag_sensitivity = 15
        self.drag_blocked = False  # Blocks the dragging til a certain minimum movement
        self.drag_time_unblock = 0.5  # Unblock dragging after given amount of seconds
        self.drag_start_time = 0  # Time when dragging started
        self.dragging_mode = self.DRAGGING_MODE_OFF  # Current dragging mode

        # Custom rendering
        self.geometry_instructions = InstructionGroup()
        self.canvas.after.add(self.geometry_instructions)
        self.pre_widget_instructions = InstructionGroup()
        self.canvas.add(self.pre_widget_instructions)

        # Hook geometry instructions
        self.editing_modes = {self.EDIT_GEOMETRY_NODES, self.EDIT_GEOMETRY_OBJECTS}  # Geometry editing enabled?
        self.show_geometry = True  # Defines if geometry shall be shown
        self.geometry_provider: GeometryProvider = None  # Link to a geometry.GeometryProvider
        self.selected_node = None  # The currently selected node's tuple (geometry, index, position, color)
        self.selected_geometry: Geometry2D = None  # The currently selected geometry
        self.editable_nodes = []  # List of editable nodes
        self.geometry_catch_radius = 12  # The radius in which the geometry shall be catchable
        self.node_catch_radius_sqr = 12 ** 2  # The radius in which the node shall be catchable
        self.geometry_line_list = []  # A list of tuples containing object's and their lines

        # Custom geometry rendering - all receive the parameters: panview, instruction group, offset, scaling
        self.on_pre_widget_rendering = None  # Called before the widget is rendered
        self.on_pre_geometry_rendering = None  # Called before the geometry is rendered
        self.on_post_geometry_rendering = None  # Called after the geometry is rendered

        self.register_event_type('on_geometry_moved')

    def transform(self, points):
        """
        Transforms a set of points by position and scaling

        :param points: A list of 2D coordinates
        :return: The transformed list of 2D coordinates
        """
        org_points = np.array(points)
        return org_points * self.pan_zoom + self.dynamic_widget.pos

    def set_geometry_provider(self, provider):
        """
        Assigns a geometry provider
        :param provider: The new provider
        """
        self.geometry_provider = provider
        self.update_geometry_instructions()

    def set_editing_modes(self, modes):
        """
        Sets the list of valid editing modes
        :param modes: The valid editing modes
        """
        self.editing_modes = modes
        self.update_geometry_instructions()

    def set_show_geometry(self, state):
        """
        Defines if the geometry shall be shown
        :param state: THe new state
        """
        if self.show_geometry == state:
            return

        self.show_geometry = state
        self.update_geometry_instructions()

    def clip_position(self):
        """
        Limits the dragging position to the image's bounding
        :return:
        """
        max_x = self.current_size[0] * self.pan_zoom / 2
        max_y = self.current_size[1] * self.pan_zoom / 2
        drag_pos = list(self.pan_offset)
        if drag_pos[0] < -max_x:
            drag_pos[0] = -max_x
        if drag_pos[1] < -max_y:
            drag_pos[1] = -max_y
        if drag_pos[0] > max_x:
            drag_pos[0] = max_x
        if drag_pos[1] > max_y:
            drag_pos[1] = max_y
        self.pan_offset = drag_pos

    def on_geometry_moved(self, geometry):
        """
        Called when a geometry was moved
        """
        pass

    def handle_zooming(self, touch):
        """
        Handles the zoom process using the mouse wheel
        :param touch: The kivy touch event
        """
        self.fit_size = False
        if touch.button == 'scrolldown':
            if self.pan_zoom < self.max_zoom:
                old_zoom = self.pan_zoom
                self.pan_zoom = self.pan_zoom * self.scroll_speed
                if self.pan_zoom>self.max_zoom:
                    self.pan_zoom = self.max_zoom
                zoom_diff = self.pan_zoom/old_zoom
                self.pan_offset = (self.pan_offset[0] * zoom_diff, self.pan_offset[1] * zoom_diff)
        elif touch.button == 'scrollup':
            self.pan_zoom = self.pan_zoom / self.scroll_speed
            self.pan_offset = (self.pan_offset[0] / self.scroll_speed, self.pan_offset[1] / self.scroll_speed)
            if self.pan_zoom < self.fit_zoom:
                self.pan_zoom = self.fit_zoom

        self.clip_position()
        self.reposition_view()

    def handle_panning(self, drag_movement):
        """
        Handles the panning process
        :param touch: The kivy touch event
        """
        self.pan_offset = (self.pan_offset[0] + drag_movement[0], self.pan_offset[1] + drag_movement[1])
        self.clip_position()
        self.reposition_view()

    def handle_node_movement(self, movement):
        """
        Handles the movement of a single node
        :param movement: The movement
        :return:
        """
        geometry: Geometry2D = self.selected_node[0]
        array_data = self.selected_node[2]
        array_data += np.array(movement) / self.pan_zoom
        index = self.selected_node[1]
        geometry.update_node(index, self.selected_node[2])
        self.update_geometry_instructions()
        self.dispatch('on_geometry_moved', geometry)

    def handle_geometry_movement(self, movement):
        """
        Handles the movement of a single node
        :param movement: The movement
        :return:
        """
        if self.selected_geometry is None:
            return
        self.selected_geometry.move_by(np.array(movement) / self.pan_zoom)
        self.update_geometry_instructions()
        self.dispatch('on_geometry_moved', self.selected_geometry)

    def handle_dragging(self, touch):
        """
        Handles the drag behavior
        :param touch: The kivy touch event
        """
        drag_diff = (touch.pos[0] - self.last_drag_pos[0], touch.pos[1] - self.last_drag_pos[1])

        if time.time() - self.drag_start_time > self.drag_time_unblock:  # Unblock dragging after given amount of time
            self.drag_blocked = False

        # block drag until a given threshold of movement has been reached
        if self.drag_blocked and drag_diff[0] ** 2 + drag_diff[1] ** 2 < self.drag_sensitivity ** 2:
            return
        else:
            self.drag_blocked = False

        if self.dragging_mode == self.DRAGGING_MODE_PAN:  # Dragging node?
            self.handle_panning(drag_diff)
        elif self.dragging_mode == self.DRAGGING_MODE_OBJECT:  # Dragging object?
            self.handle_geometry_movement(drag_diff)
        elif self.dragging_mode == self.DRAGGING_MODE_NODE:  # Dragging?
            self.handle_node_movement(drag_diff)

        self.last_drag_pos = touch.pos

    def handle_drag_start(self, touch):
        """
        Initializes the dragging process
        :param touch: The kivy touch event
        """
        self.last_drag_pos = touch.pos
        self.drag_blocked = True
        self.selected_node = None
        self.selected_geometry = True
        self.drag_start_time = time.time()

        # Check if a node was clicked
        if self.EDIT_GEOMETRY_NODES in self.editing_modes:
            offset = np.array(self.dynamic_widget.pos)
            scaling = self.pan_zoom
            # for all nodes
            for node_tuple in self.editable_nodes:
                local_coord = node_tuple[2] * scaling + offset
                if ((np.array(touch.pos) - local_coord) ** 2).sum() < self.node_catch_radius_sqr:
                    self.dragging_mode = self.DRAGGING_MODE_NODE
                    self.selected_node = node_tuple
                    return

        # Check if a line was clicked
        if self.EDIT_GEOMETRY_OBJECTS in self.editing_modes:
            offset = np.array(self.dynamic_widget.pos)
            scaling = self.pan_zoom
            # for all geometries...
            for cur_line_list in self.geometry_line_list.get(Geometry2D.GO_TAG_LINE_LIST, []):  # for all lineLists stored
                owner = cur_line_list[Geometry2D.GO_TAG_OWNER]
                line_list = cur_line_list[Geometry2D.GO_TAG_LINE_LIST_LINES]
                # for all lines...
                for cur_line_index in range(len(line_list) - 1):
                    line_dist, coord = Line2D.line_distance_to_point(line_list[cur_line_index:cur_line_index + 2, :],
                                                                     touch.pos)
                    if line_dist is not None and line_dist < self.geometry_catch_radius:
                        self.dragging_mode = self.DRAGGING_MODE_OBJECT
                        self.selected_geometry = owner
                        return

        self.dragging_mode = self.DRAGGING_MODE_PAN

    def set_dynamic_widget(self, widget):
        """
        Assigns the main widget which shall be zoomable and pannable
        :param widget: The widget to make zoomable. Has to provide a function named get_original_image_size
        """
        self.dynamic_widget = widget
        self.dynamic_widget.size = self.size

    def get_fit_zoom(self):
        """
        Returns the scaling factor required so the view will fit the whole screen
        :return: The scaling factor
        """
        if self.dynamic_widget is None:
            return 1.0

        if self.current_size[0] != 0 and self.current_size[1] != 0:
            x_scaling = self.size[0] / self.current_size[0]
            y_scaling = self.size[1] / self.current_size[1]
            scaling = y_scaling if y_scaling < x_scaling else x_scaling
            return scaling
        return 1.0

    def fit_zoom_to_size(self):
        """
        Sets the scaling factor so that the widget will fill this one's whole area
        """
        self.fit_zoom = self.get_fit_zoom()
        self.pan_zoom = self.fit_zoom

    def handle_geometry_changed(self):
        """
        Call this when the geometric data changed
        """
        self.editable_nodes.clear()
        self.geometry_line_list = {}
        self.update_geometry_instructions()

    def update_geometry_instructions(self):
        """
        Is called to update geometrical overlay views
        """

        offset = np.array(self.dynamic_widget.pos)
        scaling = self.pan_zoom

        # ---------- Pre pass (below widget) ----------

        self.pre_widget_instructions.clear()

        if self.on_pre_widget_rendering is not None:
            self.pre_widget_instructions.add(ScissorPush(x=0, y=0, width=self.width, height=self.height))
            self.on_pre_widget_rendering(self, self.pre_widget_instructions, offset, scaling)
            self.pre_widget_instructions.add(ScissorPop())

        self.geometry_instructions.clear()
        self.geometry_instructions.add(ScissorPush(x=0, y=0, width=self.width, height=self.height))

        # ---------- Main pass - underlay ----------

        if self.on_pre_geometry_rendering is not None:
            self.on_pre_geometry_rendering(self, self.geometry_instructions, offset, scaling)

        # ---------- Main pass - geometry ----------

        self.geometry_line_list = {}
        self.editable_nodes.clear()

        if self.geometry_provider is not None and self.show_geometry:  # Editable objects provided?
            # fetch all elements
            geometry_data = self.geometry_provider.get_geometry()

            transformation = Transformation2D(offset, scaling)

            # render elements
            for element in geometry_data:
                element.render_to_kivy(self.geometry_instructions,  transformation=transformation,
                                       geometry_out=self.geometry_line_list)

            for element in geometry_data:
                if self.EDIT_GEOMETRY_NODES in self.editing_modes:
                    editable_nodes = element.get_editable_nodes()
                    if editable_nodes is None:
                        continue
                    for node_tuple in editable_nodes:
                        local_coord = (node_tuple[2] * scaling + offset).astype(np.int)
                        outer_box_size = 10
                        outer_coord = (local_coord - (outer_box_size // 2, outer_box_size // 2))
                        inner_box_size = 6
                        inner_coord = (local_coord - (inner_box_size // 2, inner_box_size // 2))
                        self.geometry_instructions.add(Color(1.0, 0.0, 0.0, 1.0))
                        self.geometry_instructions.add(
                            Rectangle(pos=outer_coord, size=(outer_box_size, outer_box_size)))
                        self.geometry_instructions.add(Color(0.0, 0.0, 0.0, 1.0))
                        self.geometry_instructions.add(
                            Rectangle(pos=inner_coord, size=(inner_box_size, inner_box_size)))

                    self.editable_nodes += editable_nodes

        # ---------- Main pass - overlay ----------
        if self.on_post_geometry_rendering is not None:
            self.on_post_geometry_rendering(self, self.geometry_instructions, offset, scaling)

        self.geometry_instructions.add(ScissorPop())

    def reposition_view(self):
        """
        Updates the view's position
        """
        if self.dynamic_widget is None:
            return
        original_size = self.dynamic_widget.get_original_image_size()
        self.current_size = [original_size[0], original_size[1]]

        if self.fit_size:
            self.fit_zoom_to_size()

        target_size = (int(self.current_size[0] * self.pan_zoom), int(self.current_size[1] * self.pan_zoom))
        self.dynamic_widget.pos = (self.size[0] // 2 - target_size[0] // 2 + self.pan_offset[0],
                                   self.size[1] // 2 - target_size[1] // 2 + self.pan_offset[1])

        self.dynamic_widget.size = target_size
        self.update_geometry_instructions()

    def verify_size(self, _):
        """
        Called regularly to check if the image input size may have changed
        :param _:
        """
        if self.dynamic_widget is None:
            return
        # check if the texture size changed meanwhile
        self.fit_zoom = self.get_fit_zoom()
        cur_size = self.dynamic_widget.get_original_image_size()
        if cur_size != self.current_size:
            self.reposition_view()

    def on_touch_down(self, touch):
        """
        Kivy touch down handler. Also triggered by mouse wheel
        :param touch: The touch event
        :return:
        """
        if not self.collide_point(*touch.pos):
            return

        if touch.is_mouse_scrolling and self.may_zoom:
            self.handle_zooming(touch)

        if touch.button == 'left':
            self.handle_drag_start(touch)

        super().on_touch_down(touch)

    def on_touch_up(self, touch):
        """
        Kivy touch up handler.
        :param touch: The touch event
        :return:
        """
        if touch.button == 'left':
            self.dragging_mode = self.DRAGGING_MODE_OFF
        super().on_touch_up(touch)

    def on_touch_move(self, touch):
        """
        Kivy touch movement/dragging handler
        :param touch: The kivy move event
        """
        if self.dragging_mode != self.DRAGGING_MODE_OFF:
            self.handle_dragging(touch)
        super().on_touch_move(touch)

    def on_size_changed(self, view, value):
        """
        Called when this view's size has changed
        :param view: The view
        :param value: The new size
        """
        self.reposition_view()
