#!/usr/bin/env python2.3

try:
    import pygtk
    pygtk.require('2.0')
except ImportError, AttributeError:
    pass
import gtk
from gtk import glade
import gobject
import sys
import os
import Server
import Client
from twisted.internet import reactor


class Anteroom:
    """GUI for a multiplayer chat and game finding lobby."""
    def __init__(self, user):
        self.user = user
        self.glade = glade.XML('../glade/anteroom.glade')
        self.widgets = ['anteroomWindow', 'chatEntry', 'chatView', 'gameList',
          'userList']
        for widgetName in self.widgets:
            setattr(self, widgetName, self.glade.get_widget(widgetName))
        self.users = []
        self.games = []
        self.anteroomWindow.connect("destroy", quit)
        pixbuf = gtk.gdk.pixbuf_new_from_file(
          '../images/creature/Colossus.gif')
        self.anteroomWindow.set_icon(pixbuf)
        def1 = user.callRemote("getUserNames")
        def1.addCallbacks(self.gotUserNames, self.failure)

    def gotUserNames(self, usernames):
        self.usernames = usernames
        def1 = self.user.callRemote("getGames")
        def1.addCallbacks(self.gotGames, self.failure)

    def gotGames(self, games):
        self.games = games

        self.userStore = gtk.ListStore(gobject.TYPE_STRING)
        for user in self.users:
            it = self.userStore.append()
            self.userStore.set(it, 0, user)
        self.userList.set_model(self.userStore)
        column = gtk.TreeViewColumn('User Name', gtk.CellRendererText(),
          text=0)
        self.userList.append_column(column)

        self.gameStore = gtk.ListStore(gobject.TYPE_STRING)
        for game in self.games:
            it = self.gameStore.append()
            self.gameStore.set(it, 0, game)
        self.gameList.set_model(self.gameStore)
        column = gtk.TreeViewColumn('Game Name', gtk.CellRendererText(),
          text=0)
        self.gameList.append_column(column)

        self.anteroomWindow.show_all()


    def failure(self, error):
        print "Anteroom.failure", self, error
        reactor.stop()


def quit(unused):
    sys.exit()

