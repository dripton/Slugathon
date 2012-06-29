#!/usr/bin/env python

__copyright__ = "Copyright (c) 2010-2012 David Ripton"
__license__ = "GNU GPL v2"

import gtk
import pango
import pangocairo
from zope.interface import implementer

from slugathon.gui import Marker
from slugathon.util.Observer import IObserver
from slugathon.game import Action


@implementer(IObserver)
class TurnTrack(gtk.DrawingArea):
    """Widget to show the battle turn."""
    def __init__(self, attacker, defender, game, scale):
        gtk.DrawingArea.__init__(self)
        self.attacker = attacker
        self.defender = defender
        self.game = game
        self.scale = scale
        self.set_size_request(self.compute_width(), self.compute_height())
        marker_scale = int(round(0.5 * self.scale))
        self.attacker_marker = Marker.Marker(attacker,
                                             False,
                                             scale=marker_scale)
        self.defender_marker = Marker.Marker(defender,
                                             False,
                                             scale=marker_scale)
        self.battle_turn = 1
        self.active_marker = self.defender_marker
        self.connect("expose-event", self.cb_area_expose)
        self.show_all()

    def compute_width(self):
        """Return the width of the area in pixels."""
        return int(round(13.5 * self.scale))

    def compute_height(self):
        """Return the height of the area in pixels."""
        return int(round(3 * self.scale))

    def draw_turn_box(self, ctx, ii):
        cx = int(round((0.6 + ii * 1.8) * self.scale))
        cy = int(round(0.75 * self.scale))
        ctx.set_source_rgb(0, 0, 0)
        ctx.move_to(cx, cy)
        ctx.line_to(int(round(cx + 1.5 * self.scale)), cy)
        ctx.line_to(int(round(cx + 1.5 * self.scale)),
                    int(round(cy + 1.5 * self.scale)))
        ctx.line_to(cx, int(round(cy + 1.5 * self.scale)))
        ctx.close_path()
        ctx.stroke()

    def draw_turn_number(self, ctx, ii):
        pctx = pangocairo.CairoContext(ctx)
        layout = pctx.create_layout()
        # TODO Vary font size with scale
        desc = pango.FontDescription("Sans 17")
        layout.set_font_description(desc)
        layout.set_alignment(pango.ALIGN_CENTER)
        layout.set_text(str(ii + 1))
        cx = int(round((1.23 + ii * 1.8) * self.scale))
        cy = int(round(1.32 * self.scale))
        ctx.set_source_rgb(0, 0, 0)
        ctx.move_to(cx, cy)
        pctx.show_layout(layout)

    def draw_marker(self, ctx):
        ii = self.battle_turn - 1
        marker = self.active_marker
        cx = int(round((0.6 + ii * 1.8) * self.scale))
        cy = int(round(0 * self.scale))
        if marker == self.attacker_marker:
            cy += int(round(1.5 * self.scale))
        ctx.set_source_surface(marker.surface, cx, cy)
        ctx.paint()

    def cb_area_expose(self, area, event):
        self.update_gui(event=event)
        return True

    def update_gui(self, event=None):
        if not self.get_window():
            return
        ctx = self.get_window().cairo_create()
        if event:
            clip_rect = event.area
            ctx.rectangle(*clip_rect)
            ctx.clip()
        ctx.set_source_rgb(1, 1, 1)
        width, height = self.size_request()
        ctx.rectangle(0, 0, width, height)
        ctx.fill()
        ctx.set_line_width(round(0.06 * self.scale))
        for ii in xrange(7):
            self.draw_turn_box(ctx, ii)
        for ii in xrange(7):
            self.draw_turn_number(ctx, ii)
        self.draw_marker(ctx)

    def repaint(self):
        self.update_gui()

    def update(self, observed, action, names):
        if isinstance(action, Action.StartReinforceBattlePhase):
            self.battle_turn = action.battle_turn
            if action.playername == self.defender.player.name:
                self.active_marker = self.defender_marker
            else:
                self.active_marker = self.attacker_marker
            self.repaint()

if __name__ == "__main__":
    from slugathon.util import guiutils
    from slugathon.game import Legion

    window = gtk.Window()
    attacker = Legion.Legion(None, "Rd01", [], 1)
    defender = Legion.Legion(None, "Bu01", [], 2)
    turntrack = TurnTrack(attacker, defender, None, 50)
    turntrack.connect("destroy", guiutils.exit)
    window.add(turntrack)
    window.show_all()
    gtk.main()
