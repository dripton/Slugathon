import sys
try:
    import pygtk
    pygtk.require("2.0")
except (ImportError, AttributeError):
    pass
import gtk

ui_string = """<ui>
  <menubar name="Menubar">
    <menu action="GameMenu">
      <menuitem action="Quit"/>
    </menu>
    <menu action="PhaseMenu">
      <menuitem action="Done"/>
      <menuitem action="Undo"/>
      <menuitem action="Redo"/>
      <separator/>
      <menuitem action="Mulligan"/>
    </menu>
    <menu action="HelpMenu">
      <menuitem action="About"/>
    </menu>
  </menubar>
  <toolbar name="Toolbar">
    <toolitem action="Done"/>
    <toolitem action="Undo"/>
    <toolitem action="Redo"/>
    <separator/>
    <toolitem action="Mulligan"/>
  </toolbar>
</ui>"""


def quit(unused):
    sys.exit()


class BoardRoot(gtk.Window):
    """Root Window for GUIMasterBoard."""
    def __init__(self, username):
        print "BoardRoot.__init__(%s)" % username
        gtk.Window.__init__(self)
        self.username = username

        pixbuf = gtk.gdk.pixbuf_new_from_file(
          "../images/creature/Colossus.png")
        self.set_icon(pixbuf)
        self.set_title("Slugathon - Masterboard - %s" % self.username)
        self.connect("destroy", quit)

        self.vbox = gtk.VBox()
        self.add(self.vbox)
        self.create_ui()
        self.vbox.pack_start(self.ui.get_widget("/Menubar"), False, False, 0)
        self.vbox.pack_start(self.ui.get_widget("/Toolbar"), False, False, 0)


    def create_ui(self):
        ag = gtk.ActionGroup("MasterActions")
        # TODO confirm quit
        actions = [
          ("GameMenu", None, "_Game"),
          ("Quit", gtk.STOCK_QUIT, "_Quit", "<control>Q", "Quit program",
            quit),
          ("PhaseMenu", None, "_Phase"),
          ("Quit", gtk.STOCK_QUIT, "_Quit", "<control>Q", "Quit program", 
            quit),
          ("Done", gtk.STOCK_APPLY, "_Done", "d", "Done", self.cb_done),
          ("Undo", gtk.STOCK_UNDO, "_Undo", "u", "Undo", self.cb_undo),
          ("Redo", gtk.STOCK_REDO, "_Redo", "r", "Redo", self.cb_redo),
          ("Mulligan", gtk.STOCK_MEDIA_REWIND, "_Mulligan", "m", "Mulligan", 
            self.cb_mulligan),
          ("HelpMenu", None, "_Help"),
          ("About", gtk.STOCK_ABOUT, "_About", None, "About", self.cb_about),
        ]
        ag.add_actions(actions)
        self.ui = gtk.UIManager()
        self.ui.insert_action_group(ag, 0)
        self.ui.add_ui_from_string(ui_string)
        self.add_accel_group(self.ui.get_accel_group())


    # TODO
    def cb_done(self, action):
        print "done", action

    def cb_undo(self, action):
        print "undo", action

    def cb_redo(self, action):
        print "redo", action

    def cb_mulligan(self, action):
        print "mulligan", action

    def cb_about(self, action):
        print "about", action

