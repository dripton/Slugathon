try:
    import pygtk
    pygtk.require('2.0')
except (ImportError, AttributeError):
    pass
import gtk
from gtk import glade


class NewGame:
    """Form new game dialog."""
    def __init__(self, user):
        self.name = None
        self.min_players = None
        self.max_players = None
        self.user = user
        self.glade = glade.XML('../glade/newgame.glade')
        self.widgets = ['newgameDialog', 'nameEntry', 'minplayersSpin', 
          'maxplayersSpin']
        for widgetName in self.widgets:
            setattr(self, widgetName, self.glade.get_widget(widgetName))
        pixbuf = gtk.gdk.pixbuf_new_from_file(
          '../images/creature/Colossus.gif')
        self.newgameDialog.set_icon(pixbuf)

        response = self.newgameDialog.run()
        if response == gtk.RESPONSE_OK:
            self.ok()
        else:
            self.cancel()

    def ok(self): 
        print "ok"
        self.name = self.nameEntry.get_text()
        self.min_players = self.minplayersSpin.get_value_as_int()
        self.max_players = self.maxplayersSpin.get_value_as_int()
        def1 = self.user.callRemote("form_game", self.name, self.min_players,
          self.max_players)
        def1.addErrback(self.failure)
        self.newgameDialog.destroy()

    def cancel(self): 
        print "cancel"
        self.newgameDialog.destroy()

    def failure(self, error): 
        print error
