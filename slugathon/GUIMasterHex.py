#!/usr/bin/env python2

import Tkinter as tk
import math
import Image
import ImageTk
import tkFont

import guiutils
import colors

SQRT3 = math.sqrt(3.0)
RAD_TO_DEG = 180. / math.pi

# Where to place the label, by hexside.  Derived experimentally.
x_font_position = [0.5, 0.75, 0.75, 0.5, 0.25, 0.25]
y_font_position = [0.1, 0.125, 0.875, 0.95, 0.875, 0.125]

class GUIMasterHex:

    def __init__(self, hex, guiboard):
        self.hex = hex
        self.guiboard = guiboard
        scale = self.guiboard.scale
        self.cx = hex.x * 4 * scale
        self.cy = hex.y * 4 * SQRT3 * scale
        if not hex.inverted:
            self.cy += SQRT3 * scale

        self.init_vertexes()
        self.center = (self.cx + 3 * scale, self.cy + 1.5 * SQRT3 * scale)

        self.init_hexagon()
        self.init_gates()
        self.init_overlay()
        self.init_label()


    def init_vertexes(self):
        """Setup the hex vertexes."""
        self.vertexes = []
        for i in range(6):
            self.vertexes.append(None)
        cx = self.cx
        cy = self.cy
        scale = self.guiboard.scale
        if self.hex.inverted:
            self.vertexes[0] = (cx + scale, cy)
            self.vertexes[1] = (cx + 5 * scale, cy)
            self.vertexes[2] = (cx + 6 * scale, cy + SQRT3 * scale)
            self.vertexes[3] = (cx + 4 * scale, cy + 3 * SQRT3 * scale)
            self.vertexes[4] = (cx + 2 * scale, cy + 3 * SQRT3 * scale)
            self.vertexes[5] = (cx, cy + SQRT3 * scale)
        else:
            self.vertexes[0] = (cx + 2 * scale, cy)
            self.vertexes[1] = (cx + 4 * scale, cy)
            self.vertexes[2] = (cx + 6 * scale, cy + 2 * SQRT3 * scale)
            self.vertexes[3] = (cx + 5 * scale, cy + 3 * SQRT3 * scale)
            self.vertexes[4] = (cx + scale, cy + 3 * SQRT3 * scale)
            self.vertexes[5] = (cx, cy + 2 * SQRT3 * scale)

    def init_hexagon(self):
        """Create the polygon, filled with the terrain color.""" 
        fillcolor = colors.TkColors[colors.terrainColors[self.hex.terrain]]
        self.hexagon = self.guiboard.canvas.create_polygon(
                guiutils.flatten_point_list(self.vertexes),
                fill=fillcolor, outline='black', width=1)

    def init_gates(self):
        """Draw the entrance and exit gates.

           There are up to 3 gates to draw.  Each is 1/6 of a hexside
           square.  The first is positioned from 1/6 to 1/3 of the way
           along the hexside, the second from 5/12 to 7/12, and the
           third from 2/3 to 5/6.  The inner edge of each is 1/12 of a
           hexside inside the hexside, and the outer edge is 1/12 of a
           hexside outside the hexside.

           Since exits extend into adjacent hexes, they can be overdrawn,
           so we need to draw both exits and entrances for both hexes.
        """
        hex = self.hex
        vertexes = self.vertexes
        for i in range(6):
            n = (i + 1) % 6
            if hex.exits[i] != None:
                self.drawGate(vertexes[i][0], vertexes[i][1],
                              vertexes[n][0], vertexes[n][1], hex.exits[i])
            elif hex.entrances[i] != None:
                self.drawGate(vertexes[n][0], vertexes[n][1],
                              vertexes[i][0], vertexes[i][1], hex.entrances[i])

    def drawGate(self, vx1, vy1, vx2, vy2, gateType):
        """Draw gate on one entrance / exit hexside."""
        x0 = vx1 + (vx2 - vx1) / 6.
        y0 = vy1 + (vy2 - vy1) / 6.
        x1 = vx1 + (vx2 - vx1) / 3.
        y1 = vy1 + (vy2 - vy1) / 3.
        theta = math.atan2(vy2 - vy1, vx2 - vx1)
        third = self.guiboard.scale / 3.
        xy = []

        if gateType == 'BLOCK':
            xy.append(x0 - third * math.sin(theta))
            xy.append(y0 + third * math.cos(theta))
            xy.append(x0 + third * math.sin(theta))
            xy.append(y0 - third * math.cos(theta))
            xy.append(x1 + third * math.sin(theta))
            xy.append(y1 - third * math.cos(theta))
            xy.append(x1 - third * math.sin(theta))
            xy.append(y1 + third * math.cos(theta))
            polygon = self.guiboard.canvas.create_polygon(xy,
                fill='white', outline='black', width=1)

        elif gateType == 'ARCH':
            xy.append(x0 - third * math.sin(theta))
            xy.append(y0 + third * math.cos(theta))
            xy.append(x0 + third * math.sin(theta))
            xy.append(y0 - third * math.cos(theta))
            xy.append(x1 + third * math.sin(theta))
            xy.append(y1 - third * math.cos(theta))
            xy.append(x1 - third * math.sin(theta))
            xy.append(y1 + third * math.cos(theta))

            x2 = (x0 + x1) / 2.
            y2 = (y0 + y1) / 2.

            rect_x = x2 - third;
            rect_y = y2 - third;
            rect_width = 2. * third;
            rect_height = 2. * third;
            theta_deg = int(theta * RAD_TO_DEG)

            arc = self.guiboard.canvas.create_arc(rect_x, rect_y,
                rect_x + rect_width, rect_y + rect_height, start=theta_deg,
                extent=180, style='chord', fill='white', outline='black')

            xy[4] = xy[0];
            xy[5] = xy[1];
            xy[0] = x1;
            xy[1] = y1;
            xy[2] = xy[6];
            xy[3] = xy[7];
            xy[6] = x0;
            xy[7] = y0;

            polygon = self.guiboard.canvas.create_polygon(xy,
                fill='white', outline='black', width=1)

            # Erase the existing hexside line.
            line = self.guiboard.canvas.create_line(x0, y0, x1, y1, 
                fill='white');

            line = self.guiboard.canvas.create_line(x1, y1, xy[2], xy[3],
                fill='black');
            line = self.guiboard.canvas.create_line(xy[4], xy[5], x0, y0,
                fill='black');

        elif gateType == 'ARROW':
            xy.append(x0 - third * math.sin(theta))
            xy.append(y0 + third * math.cos(theta))
            xy.append((x0 + x1) / 2. + third * math.sin(theta))
            xy.append((y0 + y1) / 2. - third * math.cos(theta))
            xy.append(x1 - third * math.sin(theta))
            xy.append(y1 + third * math.cos(theta))

            polygon = self.guiboard.canvas.create_polygon(xy,
                fill='white', outline='black', width=1)

        elif gateType == 'ARROWS':
            for j in range(3):
                x0 = vx1 + (vx2 - vx1) * (2 + 3 * j) / 12.
                y0 = vy1 + (vy2 - vy1) * (2 + 3 * j) / 12.
                x1 = vx1 + (vx2 - vx1) * (4 + 3 * j) / 12.
                y1 = vy1 + (vy2 - vy1) * (4 + 3 * j) / 12.

                xy = []
                xy.append(x0 - third * math.sin(theta))
                xy.append(y0 + third * math.cos(theta))
                xy.append((x0 + x1) / 2. + third * math.sin(theta))
                xy.append((y0 + y1) / 2. - third * math.cos(theta))
                xy.append(x1 - third * math.sin(theta))
                xy.append(y1 + third * math.cos(theta))
                polygon = self.guiboard.canvas.create_polygon(xy,
                    fill='white', outline='black', width=1)



    def init_overlay(self):
        """Setup the overlay with terrain name and image."""
        image_filename = guiutils.IMAGE_DIR + self.hex.overlay_filename
        self.image = Image.open(image_filename)
        scale = self.guiboard.scale
        self.bboxsize = (6 * scale, int(3 * SQRT3 * scale))
        self.image.thumbnail(self.bboxsize, Image.ANTIALIAS)
        self.tkim = ImageTk.PhotoImage(self.image)
        self.overlay = self.guiboard.canvas.create_image(self.center[0],
                self.center[1], image=self.tkim, anchor="center")


    def init_label(self):
        """Display the hex label."""
        # TODO Font size should vary with scale and actual width of font.
        font = tkFont.Font(family="times", size=8, weight=tk.NORMAL)
        label = str(self.hex.label)
        half_text_width = 0.5 * font.measure(label)
        half_text_height = 0.5 * font.metrics('linespace')
        side = self.hex.label_side

        x = self.cx + self.bboxsize[0] * x_font_position[side]
        y = self.cy + self.bboxsize[1] * y_font_position[side]
        self.guiboard.canvas.create_text(x, y, anchor=tk.CENTER, fill='black',
                text=label, font=font)

