try:
    import pygtk
    pygtk.require('2.0')
except (ImportError, AttributeError):
    pass
import gtk
import gtk.glade
from twisted.internet import reactor
from playercolordata import colors


class PickColor:
    """Dialog to pick a player color."""
    def __init__(self, user, username, game_name, colors_left):
        print "PickColor.__init__"
        self.user = user
        self.username = username
        self.game_name = game_name
        self.glade = gtk.glade.XML('../glade/pickcolor.glade')
        self.widgets = ['pick_color_dialog', 'label1'] + colors
        for widget_name in self.widgets:
            setattr(self, widget_name, self.glade.get_widget(widget_name))

        pixbuf = gtk.gdk.pixbuf_new_from_file(
          '../images/creature/Colossus.png')
        self.pick_color_dialog.set_icon(pixbuf)
        self.pick_color_dialog.set_title("%s - %s" % (
          self.pick_color_dialog.get_title(), self.username))

        for button_name in colors:
            button = getattr(self, button_name)
            if button_name in colors_left: 
                button.connect('button-press-event', self.cb_click)
                print "connecting button for", button_name
            else:
                button.disable()

    def cb_click(self, widget, event):
        print self, widget, event
        color = widget.get_label()
        def1 = self.user.callRemote("pick_color", self.game_name, color)
        def1.addErrback(self.failure)
        self.pick_color_dialog.destroy()

    def failure(self, error):
        print "PickColor.failure", error
