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
from sets import Set
import Server
import Client
from twisted.internet import reactor
import NewGame


class Anteroom:
    """GUI for a multiplayer chat and game finding lobby."""
    def __init__(self, user):
        self.user = user
        self.glade = glade.XML('../glade/anteroom.glade')
        self.widgets = ['anteroomWindow', 'chatEntry', 'chatView', 'gameList',
          'userList', 'newGameButton']
        for widgetName in self.widgets:
            setattr(self, widgetName, self.glade.get_widget(widgetName))
        self.usernames = Set()
        self.games = {}
        self.anteroomWindow.connect("destroy", quit)

        self.chatEntry.connect("key-press-event", self.cb_keypress)
        self.newGameButton.connect("button-press-event", self.cb_click)

        pixbuf = gtk.gdk.pixbuf_new_from_file(
          '../images/creature/Colossus.gif')
        self.anteroomWindow.set_icon(pixbuf)
        def1 = user.callRemote("getUserNames")
        def1.addCallbacks(self.gotUserNames, self.failure)

    def gotUserNames(self, usernames):
        self.usernames = Set(usernames)
        print "Anteroom got usernames", usernames
        def1 = self.user.callRemote("getGames")
        def1.addCallbacks(self.gotGames, self.failure)

    def gotGames(self, games):
        print "Anteroom got games", games
        self.games = games

        self.userStore = gtk.ListStore(str)
        self.updateUserStore()
        self.userList.set_model(self.userStore)
        column = gtk.TreeViewColumn('User Name', gtk.CellRendererText(),
          text=0)
        self.userList.append_column(column)

        self.gameStore = gtk.ListStore(str)
        self.updateGameStore()
        self.gameList.set_model(self.gameStore)
        column = gtk.TreeViewColumn('Game Name', gtk.CellRendererText(),
          text=0)
        self.gameList.append_column(column)

        self.anteroomWindow.show_all()

    def updateUserStore(self):
        sorted_usernames = list(self.usernames)
        sorted_usernames.sort()
        leng = len(self.userStore)
        for ii, username in enumerate(sorted_usernames):
            if ii < leng:
                self.userStore[ii, 0] = (username,)
            else:
                self.userStore.append((username,))
        leng = len(sorted_usernames)
        while len(self.userStore) > leng:
            del self.userStore[leng]

    def updateGameStore(self):
        for game in self.games:
            it = self.gameStore.append()
            self.gameStore.set(it, 0, game)

    def failure(self, error):
        print "Anteroom.failure", self, error
        reactor.stop()


    def addUsername(self, username):
        self.usernames.add(username)
        self.updateUserStore()

    def delUsername(self, username):
        self.usernames.remove(username)
        self.updateUserStore()

    def cb_insert_text(self, *args):
        print "cb_insert_text", args

    def cb_keypress(self, entry, event):
        ENTER_KEY = 65293  # XXX Find a cleaner way to do this.
        if event.keyval == ENTER_KEY:
            text = self.chatEntry.get_text()
            if text:
                def1 = self.user.callRemote("send_chat_message", text)
                self.chatEntry.set_text("")

    def cb_click(self, widget, event):
        print "clicked new game button"
        newgame = NewGame.NewGame(self.user)

    def receive_chat_message(self, message):
        buffer = self.chatView.get_buffer()
        message = message.strip() + "\n"
        it = buffer.get_end_iter()
        buffer.insert(it, message)
        self.chatView.scroll_to_mark(buffer.get_insert(), 0)

    def add_game(self, name, creator, create_time, start_time, min_players,
      max_players):
        pass
        

def quit(unused):
    sys.exit()

