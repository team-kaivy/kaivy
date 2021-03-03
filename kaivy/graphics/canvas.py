#######################################################################################################################
#                                                                                                                      #
#                                             This file is part of kAIvy                                               #
#                                                                                                                      #
#                                      Copyright (c) 2019-2021 by the kAIvy team and contributors                                      #
#                                                                                                                      #
########################################################################################################################


from kivy.graphics import Color, Line, SmoothLine, Rectangle, Ellipse
from kivy.uix.label import Label
import numpy as np
from kaivy.geometry.arc2d import Arc2D
from kaivy.geometry.transformation2d import Transformation2D

class KaivyCanvas:
    """
    Rendering command wrapping class for Kivy (and potential alternative future renderers)

    Converts simple canvas command such as draw_line into appropriate Kivy instruction group commands.
    """

    def __init__(self, instruction_group, size, offset=(0.0, 0.0), scaling=1.0, y_top_down=True, cache={}):
        """
        Initializer
        :param instruction_group: The target Kivy instruction group
        :param size: The canvas area
        :param offset: The panning offset
        :param scaling: The scaling factor
        :param y_top_down: Defines if y 0 shall be at the top (like in Window GDI) instead of at bottom (Kivy)
        :param cache: A dictionary which enables this canvas to cache specific elements
        """
        self.font_scale = False  # Defines if text output shall be scaled in size automatically too
        self.instruction_group = instruction_group  # The kivy instruction group
        self.size = size  # The painting area's size
        self.org_scaling = 1.0
        self.org_offset = (0.0, 0.0)
        self.offset: np.ndarray = np.array([0.0, 0.0])
        self.scaling: np.ndarray = np.array([1.0, 1.0])
        self.y_top_down: bool = False  # Defines if y is at top
        self.update_transformation(offset, scaling, y_top_down=y_top_down)
        self.y_top_down = y_top_down  # Remember if y 0 is at top
        self.cache = cache  # Cache e.g. for text output textures
        self.main_color = (1.0, 1.0, 1.0, 1.0)  # Main color
        self.secondary_color = (1.0, 1.0, 1.0, 1.0)  # Secondary color, e.g. border
        self.selected_color = self.main_color  # The currently selected painting color
        self.transformation_stack = []  # Stack holding backuped transformations

    def update_transformation(self, offset=None, scaling=None, y_top_down=True):
        self.y_top_down = y_top_down  # Defines if y is at top
        if self.scaling is not None:
            self.org_scaling = scaling  # Original scaling setting
        if offset is not None:
            self.org_offset = offset  # Original offset
            self.offset = np.array(offset)  # The current panning offset
            if y_top_down:
                self.offset = np.array([self.offset[0], self.offset[1] + self.size[1] * self.org_scaling])
        self.scaling = (scaling, -scaling if y_top_down else scaling)

    def push_transformation(self):
        """
        Pushes the current transformation settings onto the stack
        """
        self.transformation_stack.append([self.offset, self.scaling, self.y_top_down])

    def pop_transformation(self):
        """
        Pops the last transformation from the stack
        :return: Restores the last pushed transformation
        """
        transformation = self.transformation_stack.pop(len(self.transformation_stack) - 1)
        self.offset, self.scaling, self.y_top_down = transformation

    def transform_coordinates(self, coordinates):
        """
        Transforms given coordinates by the current panning and scaling
        :param coordinates: Input coordinates
        :return: Transformed coordinates
        """
        if not isinstance(coordinates, np.ndarray):
            coordinates = np.array(coordinates)
        return coordinates * self.scaling + self.offset

    def transform_coordinates_to_unscaled(self, coordinates):
        """
        Transforms given coordinates so that they can be used in an unscaled canvas, respecting the current y direction.
        Afterwards they can be used in a canvas with a scaling of 1.0 and no panning effects.
        :param coordinates: Input coordinates
        :return: Transformed coordinates
        """
        if not isinstance(coordinates, np.ndarray):
            coordinates = np.array(coordinates)
        result = coordinates * self.scaling + self.offset
        if self.y_top_down:
            if len(result.shape) == 1:
                result[1] = -result[1] + self.size[1]
            else:
                result[:, 1] = result[:, 1] * (-1) + self.size[1]
        return result

    def transform_size(self, size):
        """
        Transforms given size definition
        :param size: The size in form of width, height
        :return: The scaled size
        """
        return np.array(size) * self.scaling

    def transform_size_pixel(self, size):
        """
        Transforms given size definition, just flips y element if y axis is top to bottom
        :param size: The size in form of width, height
        :return: The scaled size
        """
        return np.array(size) * (1.0, -1 if self.y_top_down else +1.0)

    def _select_color(self, color):
        """
        Selects a new color in Kivy (and adds it to the instruction group)
        :param color: The new color, an RGBA tuple from 0 to 1
        """
        if self.selected_color != color:
            self.instruction_group.add(Color(*color))
            self.selected_color = color

    def set_color(self, color):
        """
        Defines the current main output color
        :param color: The new color, an RGBA tuple from 0 to 1
        """
        self.main_color = color

    def set_secondary_color(self, color):
        """
        Defines the current secondary output color, e.g. the border of a polygon
        :param color: The new color, an RGBA tuple from 0 to 1
        """
        self.secondary_color = color

    def draw_line(self, start=None, end=None, points=None, line_width=1, smooth=False):
        """
        Draws a line from given start to end or between points
        :param start: The start coordinate
        :param end: The end coordinate
        :points: Instead of start and end a list of points may be passed
        :param line_width: The line's width
        :param smooth: Defines if the line shall be drawn smooth
        """
        if self.selected_color != self.main_color:
            self._select_color(self.main_color)
        points = self.transform_coordinates(np.array(points if points is not None else [start, end]))
        points = points.flatten().tolist()

        if not smooth:
            self.instruction_group.add(Line(points=points, width=line_width))
        else:
            self.instruction_group.add(SmoothLine(points=points, width=line_width))

    def draw_polygon(self, points, filled=False, line_width=1, smooth=False):
        """
        Draws a polygon. FILLING is not yet supported
        :param points: The list of points
        :param filled: Defines if the polygon shall be filled
        :param line_width: Defines the border's width in pixels
        :param smooth: Defines if the outer border shall be smoothened
        """
        if len(points) < 2:
            return
        if self.selected_color != self.main_color:
            self._select_color(self.main_color)
        points = self.transform_coordinates(points)
        is_line = len(points) <= 2
        # draw points+1 lines if it defines an area. draw just a line if has just two points
        line_count = len(points) if not is_line else 0
        if isinstance(points, np.ndarray):
            points = points.flatten().tolist()
        for index in range(line_count):
            cindex = index * 2
            nindex = ((index + 1) * 2) % len(points)
            self.instruction_group.add(
                Line(points=(*points[cindex:cindex + 2], *points[nindex:nindex + 2]), width=line_width, smooth=smooth))

    def draw_rectangle(self, pos, size, filled=True, border=0, pixel_size=False):
        """
        Draws a rectangle
        :param pos: The position in pixels
        :param size: The size in pixels
        :param filled: Defines if the rectangle shall be filled
        :param border: The rectangle's border (in secondary color)
        :param pixel_size: Size is defined in pixels (and won't be further scaled)
        """

        pos = self.transform_coordinates(pos)
        size = self.transform_size_pixel(size) if pixel_size else self.transform_size(size)

        if filled:
            self._select_color(self.main_color)
            self.instruction_group.add(Rectangle(pos=pos, size=size))
        if border > 0:
            self._select_color(self.secondary_color)
            self.instruction_group.add(Rectangle(pos=pos, size=(size[0], border)))
            self.instruction_group.add(Rectangle(pos=(pos[0], pos[1] + border), size=(border, size[1] - 2 * border)))
            self.instruction_group.add(
                Rectangle(pos=(pos[0] + size[0] - border, pos[1] + border), size=(border, size[1] - 2 * border)))
            self.instruction_group.add(Rectangle(pos=(pos[0], pos[1] + size[1] - border), size=(size[0], border)))

    def draw_ellipse(self, pos=None, size=(1, 1), center_pos=None, filled=True, border=0, pixel_size=False):
        """
        Draws an ellipse
        :param pos: The position of the upper lef edge in pixels
        :param size: The size in pixels
        :param center_pos: The center position in pixels (alternative to pos)
        :param filled: Defines if the ellipse shall be filled
        :param border: The rectangle's border (in secondary color)
        :param pixel_size: Size is defined in pixels (and won't be further scaled)
        """
        size = self.transform_size_pixel(size) if pixel_size else self.transform_size(size)
        if center_pos is not None:
            pos = self.transform_coordinates(center_pos) - size / 2
        else:
            pos = self.transform_coordinates(pos)

        if filled:
            self._select_color(self.main_color)
            self.instruction_group.add(Ellipse(pos=pos, size=size))
        if border > 0:
            self._select_color(self.secondary_color)
            self.instruction_group.add(SmoothLine(ellipse=(pos[0], pos[1], size[0], size[1], 0.0, 360.0), width=border))

    def draw_arc(self, center_pos, start_angle, end_angle,  inner_rad, outer_rad, border_size=1.0,
                 perimeter_segment_relation=None):
        """
        Draws a partial circle
        :param center_pos: The circle's center
        :param start_angle: The circle's start angle in degree
        :param end_angle: The circle's end angle in degree
        :param inner_rad: The circle's inner radius
        :param outer_rad: The circle's outer radius
        :param border_size: The border size
        :param perimeter_segment_relation: The relation between circle size and segments drawn. Around 0.1 by default.
        """
        transformation = Transformation2D(self.offset, self.scaling)

        displ_arc = Arc2D(center_pos, start_angle=start_angle, end_angle=end_angle, inner_radius=inner_rad,
                           outer_radius=outer_rad)
        if perimeter_segment_relation is not None:
            displ_arc.perimeter_segment_relation = perimeter_segment_relation
        displ_arc.color = self.main_color
        displ_arc.border_color = self.secondary_color
        displ_arc.border_size = border_size
        displ_arc.render_to_kivy(self.instruction_group, transformation)

    @staticmethod
    def get_text_handle_static(text, font_settings={}, cache={}, cache_id=None):
        """
        Creates a font label in form of a texture which can be rendered using functions such as draw_text
        :param text: The text
        :param font_settings: The font settings such as fontName, fontSize, textColor, bold and italic
        :param cache: The cache dictionary
        :param cache_id: A cache id which can be used to backup the rendered texture for multiple frames as long as
        none of the properties changes.
        """
        cached_label: Label = None
        italic = font_settings.get('italic', False)
        bold = font_settings.get('bold', False)
        font_name = font_settings.get('fontName', 'Roboto')
        font_size = font_settings.get('fontSize', 14)
        text_color = font_settings.get('textColor', (0.0, 0.0, 0.0, 1.0))
        if cache_id is not None:  # If cachable try to fetch from cache
            cached_label = cache.get(cache_id, None)
        if cached_label is not None and cached_label.text == text and cached_label.font_size == font_size and \
                cached_label.bold == bold and cached_label.italic == italic and cached_label.font_name == font_name:
            return cached_label
        else:
            temp_label = Label(text=text, color=text_color, pos_hint=(0, 0),
                               font_size=font_size, bold=bold, italic=italic)
            if cache_id is not None:  # Cache if possible
                cache[cache_id] = temp_label
            if font_name is not None:
                temp_label.font_name = font_name
            temp_label.texture_update()
            temp_label.size = temp_label.texture_size
            return temp_label

    def get_text_handle(self, text, font_settings={}, cache_id=None):
        """
        Creates a font label in form of a texture which can be rendered using functions such as draw_text
        :param text: The text to be printed
        :param font_settings: The font settings such as fontName, fontSize, italic and bold
        :param cache_id: An id to recycle the text image between frames. Needs to be unique for this canvas and stable.
        :return: The handle
        """
        if self.font_scale:
            font_settings['fontSize'] = font_settings.get('fontSize', 14.0) * self.scaling[0] + 0.5

        return self.get_text_handle_static(text=text, font_settings=font_settings, cache_id=cache_id, cache=self.cache)

    def draw_text(self, position, text_handle):
        """
        Draws given handle received from get_text_handle*
        :param position: The output position
        :param text_handle: The text handle
        """
        position = (self.transform_coordinates(position)).tolist()
        text_handle.pos = position
        if self.y_top_down:
            text_handle.y -= text_handle.texture_size[1]
        self.instruction_group.add(text_handle.canvas)
