try:
    import pygtk
    pygtk.require("2.0")
except (ImportError, AttributeError):
    pass
import gtk
import os
import math
import guiutils
import colors

SQRT3 = math.sqrt(3.0)
RAD_TO_DEG = 180. / math.pi


class GUIBattleHex(object):
    def __init__(self, battlehex, guimap):
        self.battlehex = battlehex
        self.guimap = guimap
        scale = self.guimap.scale
        self.cx = battlehex.x * 4 * scale
        self.cy = battlehex.y * 4 * SQRT3 * scale
        if battlehex.down:
            self.cy += SQRT3 * scale
        self.fillcolor = self.find_fillcolor()
        self.center = (self.cx + 3 * scale, self.cy + 1.5 * SQRT3 * scale)
        self.selected = False

        self.init_vertexes()
        iv = guiutils.scale_polygon(self.vertexes, 0.7)
        self.inner_vertexes = []
        for point in iv:
            self.inner_vertexes.append((int(round(point[0])),
                                       int(round(point[1]))))
        self.init_overlay()

    def find_fillcolor(self):
        terrain = self.battlehex.terrain
        color = colors.battle_terrain_colors.get((terrain,
          self.battlehex.elevation), None)
        if not color:
            color = colors.battle_terrain_colors.get(terrain)
        return guiutils.rgb_to_gtk(colors.rgb_colors[color])

    def init_vertexes(self):
        """Setup the hex vertexes.

        Each vertex is the midpoint between the vertexes of the two
        bordering hexes.
        """
        self.vertexes = []
        for unused in xrange(6):
            self.vertexes.append(None)
        cx = self.cx
        cy = self.cy
        scale = self.guimap.scale
        self.vertexes[0] = (cx, cy)
        self.vertexes[1] = (cx + 2 * scale, cy)
        self.vertexes[2] = (cx + 3 * scale, int(round(cy + SQRT3 * scale)))
        self.vertexes[3] = (cx + 2 * scale, int(round(cy + 2 * SQRT3 * scale)))
        self.vertexes[4] = (cx, int(round(cy + 2 * SQRT3 * scale)))
        self.vertexes[5] = (cx - scale, int(round(cy + SQRT3 * scale)))


    def draw_hexagon(self, gc, style):
        """Create the polygon, filled with the terrain color."""

        # TODO Fix random black/white edge color on border between selected
        # and unselected hexes.

        colormap = self.guimap.area.get_colormap()

        if self.selected:
            # outer portion
            fg = colormap.alloc_color("white")
            gc.foreground = fg
            self.guimap.area.window.draw_polygon(gc, True, self.points)

            # inner hex
            fg = colormap.alloc_color(*self.fillcolor)
            gc.foreground = fg
            self.guimap.area.window.draw_polygon(gc, True,
                self.inner_vertexes)

            # outline
            fg = colormap.alloc_color("black")
            gc.foreground = fg
            self.guimap.area.window.draw_polygon(gc, False, self.points)

        else:
            # hex
            fg = colormap.alloc_color(*self.fillcolor)
            gc.foreground = fg
            self.guimap.area.window.draw_polygon(gc, True, self.points)

            # outline
            fg = colormap.alloc_color("white")
            gc.foreground = fg
            self.guimap.area.window.draw_polygon(gc, False, self.points)




    def init_overlay(self):
        """Setup the overlay with terrain name and image."""
        overlay_filename = self.battlehex.overlay_filename
        if overlay_filename is None:
            return
        scale = self.guimap.scale
        self.bboxsize = (6 * scale, int(3 * SQRT3 * scale))

        myboxsize = [0.85 * mag for mag in self.bboxsize]
        self.dest_x = int(round(self.center[0] - myboxsize[0] / 2.))
        self.dest_y = int(round(self.center[1] - myboxsize[1] / 2.))

        image_filename = os.path.join("../images/battlehex", 
          overlay_filename)
        pixbuf = gtk.gdk.pixbuf_new_from_file(image_filename)
        self.pixbuf = pixbuf.scale_simple(int(round(myboxsize[0])),
            int(round(myboxsize[1])), gtk.gdk.INTERP_BILINEAR)


    def draw_overlay(self, gc, style):
        if self.battlehex.overlay_filename is None:
            return
        drawable = self.guimap.area.window
        drawable.draw_pixbuf(gc, self.pixbuf, 0, 0, self.dest_x, self.dest_y,
          -1, -1, gtk.gdk.RGB_DITHER_NORMAL, 0, 0)


    def draw_label(self, gc, style):
        """Display the hex label."""
        label = str(self.battlehex.label)
        layout = self.guimap.area.create_pango_layout(label)
        text_width, text_height = layout.get_pixel_size()
        half_text_width = 0.5 * text_width
        half_text_height = 0.5 * text_height
        side = self.battlehex.label_side

        x = int(round((self.cx + self.bboxsize[0] * x_font_position[side] -
                half_text_width)))
        y = int(round((self.cy + self.bboxsize[1] * y_font_position[side] -
                half_text_height)))

        colormap = self.guimap.area.get_colormap()
        fg = colormap.alloc_color("black")
        gc.foreground = fg

        self.guimap.area.window.draw_layout(gc, x, y, layout)


    def update_gui(self, gc, style):
        self.draw_hexagon(gc, style)
        self.draw_overlay(gc, style)
        self.draw_label(gc, style)

    def toggle_selection(self):
        self.selected = not self.selected

