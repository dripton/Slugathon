#!/usr/bin/env python

__copyright__ = "Copyright (c) 2012 David Ripton"
__license__ = "GNU GPL v2"


from twisted.internet import gtk2reactor
try:
    gtk2reactor.install()
except AssertionError:
    pass
import gtk
from twisted.internet import reactor
from twisted.python import log

from slugathon.gui import icon, ConfirmDialog
from slugathon.util import prefs


class MainWindow(gtk.Window):
    """Main GUI window."""
    def __init__(self, playername=None, scale=None):
        gtk.Window.__init__(self)

        self.playername = playername
        self.game = None
        self.anteroom = None
        self.guiboard = None

        self.set_icon(icon.pixbuf)
        self.set_title("Slugathon - %s" % (self.playername))
        self.connect("delete-event", self.cb_delete_event)
        self.connect("destroy", self.cb_destroy)
        self.connect("configure-event", self.cb_configure_event)

        if scale is None:
            self.scale = self.compute_scale()
        else:
            self.scale = scale
        # TODO
        self.set_default_size(1024, 768)

        if self.playername:
            tup = prefs.load_window_position(self.playername,
              self.__class__.__name__)
            if tup:
                x, y = tup
                self.move(x, y)
            tup = prefs.load_window_size(self.playername,
              self.__class__.__name__)
            if tup:
                width, height = tup
                self.resize(width, height)

        self.notebook = gtk.Notebook()
        self.add(self.notebook)
        self.notebook.set_tab_pos(gtk.POS_BOTTOM)
        self.show_all()

    def add_anteroom(self, anteroom):
        self.anteroom = anteroom
        label = gtk.Label("Anteroom")
        self.notebook.prepend_page(anteroom, label)
        self.show_all()

    def add_guiboard(self, guiboard):
        self.guiboard = guiboard
        label = gtk.Label("MasterBoard")
        self.notebook.append_page(guiboard, label)
        self.show_all()

    def remove_guiboard(self):
        if self.guiboard:
            page_num = self.notebook.page_num(self.guiboard)
            self.notebook.remove_page(page_num)
            self.guiboard = None

    def add_guimap(self, guimap):
        self.guimap = guimap
        label = gtk.Label("BattleMap")
        self.notebook.append_page(guimap, label)
        self.show_all()

    def remove_guimap(self):
        if self.guimap:
            accel_group = self.guimap.ui.get_accel_group()
            self.remove_accel_group(accel_group)
            page_num = self.notebook.page_num(self.guimap)
            self.notebook.remove_page(page_num)
            self.guimap = None

    def cb_delete_event(self, widget, event):
        if self.game is None or self.game.over:
            self.cb_destroy(True)
        else:
            confirm_dialog, def1 = ConfirmDialog.new(self, "Confirm",
              "Are you sure you want to quit?")
            def1.addCallback(self.cb_destroy)
            def1.addErrback(self.failure)
        return True

    def cb_destroy(self, confirmed):
        """Withdraw from the game, and destroy the GUIMasterBoard."""
        if confirmed:
            self.destroyed = True
            if self.game:
                def1 = self.user.callRemote("withdraw", self.game.name)
                def1.addErrback(self.failure)
            self.destroy()

    def cb_withdraw2(self, confirmed):
        """Withdraw from the game, but do not destroy the GUIMasterBoard."""
        if confirmed:
            if self.game:
                def1 = self.user.callRemote("withdraw", self.game.name)
                def1.addErrback(self.failure)

    def cb_configure_event(self, event, unused):
        if self.playername:
            x, y = self.get_position()
            prefs.save_window_position(self.playername,
              self.__class__.__name__, x, y)
            width, height = self.get_size()
            prefs.save_window_size(self.playername, self.__class__.__name__,
              width, height)
        return False

    def compute_scale(self):
        """Return the approximate maximum scale that let the board fit on
        the screen."""
        # TODO
        return 15

    def failure(self, arg):
        log.err(arg)


def main():
    import time
    from slugathon.game import Game
    from slugathon.util.NullUser import NullUser
    from slugathon.gui import Anteroom

    now = time.time()
    user = NullUser()
    playername = "Player 1"
    game = Game.Game("g1", "Player 1", now, now, 2, 6)
    playernames = [playername]
    games = [game]
    main_window = MainWindow()
    anteroom = Anteroom.Anteroom(user, playername, playernames, games,
      main_window)
    main_window.add_anteroom(anteroom)

    reactor.run()


if __name__ == "__main__":
    main()
