try:
    import pygtk
    pygtk.require('2.0')
except (ImportError, AttributeError):
    pass
import gtk
import gtk.glade
from twisted.internet import reactor


class PickColor:
    """Dialog to pick a player color."""

    player_colors = ['Black', 'Blue', 'Brown', 'Gold', 'Green', 'Red']

    def __init__(self, user, colors_left):
        self.user = user
        self.glade = gtk.glade.XML('../glade/pickcolor.glade')
        self.widgets = ['pick_color_dialog', 'label1'] + self.player_colors
        for widget_name in self.widgets:
            setattr(self, widget_name, self.glade.get_widget(widget_name))

        pixbuf = gtk.gdk.pixbuf_new_from_file(
          '../images/creature/Colossus.gif')
        self.pickColorDialog.set_icon(pixbuf)

        for button_name in self.player_colors:
            button = getattr(self, button_name)
            if button_name in colors_left: 
                button.connect('button-press-event', self.cb_click)
            else:
                button.disable()

    def cb_click(self, widget, event):
        print self, widget, event
        color = widget.get_text()
        def1 = self.user.callRemote("pick_color", color)
        def1.addErrback(self.failure)
        self.pickColorDialog.destroy()

    def failure(self, error):
        print "PickColor.failure", error
