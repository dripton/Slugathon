try:
    import pygtk
    pygtk.require('2.0')
except (ImportError, AttributeError):
    pass
import gtk
import gtk.glade


class NewGame:
    """Form new game dialog."""
    def __init__(self, user, username):
        self.name = None
        self.min_players = None
        self.max_players = None
        self.user = user
        self.username = username
        self.glade = gtk.glade.XML('../glade/newgame.glade')
        self.widgets = ['new_game_dialog', 'name_entry', 'min_players_spin', 
          'max_players_spin']
        for widgetName in self.widgets:
            setattr(self, widgetName, self.glade.get_widget(widgetName))
        pixbuf = gtk.gdk.pixbuf_new_from_file(
          '../images/creature/Colossus.gif')
        self.new_game_dialog.set_icon(pixbuf)
        self.new_game_dialog.set_title("%s - %s" % (
          self.new_game_dialog.get_title(), self.username))


        response = self.new_game_dialog.run()
        if response == gtk.RESPONSE_OK:
            self.ok()
        else:
            self.cancel()

    def ok(self): 
        self.name = self.name_entry.get_text()
        self.min_players = self.min_players_spin.get_value_as_int()
        self.max_players = self.max_players_spin.get_value_as_int()
        def1 = self.user.callRemote("form_game", self.name, self.min_players,
          self.max_players)
        def1.addErrback(self.failure)
        self.new_game_dialog.destroy()

    def cancel(self): 
        self.new_game_dialog.destroy()

    def failure(self, error): 
        print "NewGame", error
