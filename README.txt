Slugathon is a free (licensed under the GPLv2; see slugathon/docs/COPYING.txt)
clone of the classic Avalon Hill boardgame Titan. The focus is on playing
against other humans across the Internet.

Installation is currently pretty easy on Linux (install some dependencies with
your package manager then run a command), and kind of a pain on Windows and Mac
OS.  (I had .exe files for Windows, but Github removed their downloads feature
so they're gone for now.  Let me know if you need them.)  I'm working to make
it easier everywhere.

Note that pip can't install Slugathon because it can't install PyGI.  But
once you have PyGI installed, pip should be able to do the rest.

1. Install all the dependencies listed at
http://github.com/dripton/Slugathon/wiki/Dependencies

(You basically need a recent Python 3, PyGI, PyGI-Cairo, and pip3.  Then
you can pip install -r requirements.txt to get the rest.)

See
http://github.com/dripton/Slugathon/wiki/Building-on-Linux
http://github.com/dripton/Slugathon/wiki/Building-on-Mac-OS
http://github.com/dripton/Slugathon/wiki/Building-on-Windows
for details.

2. Clone Slugathon with Git, or download and uncompress a zip or tar
version.

3. Run "python3 setup.py install" to install the game.  This will probably
require root permissions, so use su or sudo.

4. In one terminal, run "slugathon server -n"

5. In a second terminal (on the same or a different computer) run
"slugathon client".  Pick the IP or hostname of the computer where you
ran the server, and connect.

6. If you want multiple human players, then in a third terminal, (on the same
or a different computer), run "slugathon client", picking a different player.

(You can add up to a total of 6 players.)

7. Chat with each other in the Lobby window.

8. Have the first player form a game, then have the other player(s) join it.
If you want AI players, then set "Min players" to more than the number of
human players, and AIs will join in.  When all humans have joined, have the
first player click "Start Game Now", and play some Titan.

For documentation, see the Wiki at http://github.com/dripton/Slugathon/wiki
