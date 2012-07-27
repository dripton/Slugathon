Slugathon is a free (licensed under the GPLv2; see slugathon/docs/COPYING.txt)
clone of the classic Avalon Hill boardgame Titan. The focus is on playing
against other humans across the Internet.

Installation is currently really easy on Windows (just download and run an
.exe file), pretty easy on Linux (install some dependencies with your package
manager then run a command), and kind of a pain on Mac OS.  I'm working to
make it easier everywhere.

1. If you're on Windows and in a hurry, download the latest .exe from the
Downloads page and skip to step 5.

2. Install all the dependencies listed at
http://wiki.github.com/dripton/Slugathon/dependencies.

See
http://wiki.github.com/dripton/Slugathon/Building-on-Linux
http://wiki.github.com/dripton/Slugathon/Building-on-Mac-OS
http://wiki.github.com/dripton/Slugathon/Building-on-Windows
for details.

3. Clone Slugathon with Git, or download and uncompress a zip or tar
version.

4. Run "python setup.py install" to install the game.  This will probably
require root permissions, so use su or sudo.

5. In one terminal, run "slugathon server -n"

6. In a second terminal (on the same or a different computer) run
"slugathon client".  Pick the IP or hostname of the computer where you
ran the server, and connect.

7. If you want multiple human players, then in a third terminal, (on the same
or a different computer), run "slugathon client", picking a different player.

(You can add up to a total of 6 players.)

8. Chat with each other in the Lobby window.

9. Have the first player form a game, then have the other player(s) join it.
If you want AI players, then set "Min players" to more than the number of
human players, and AIs will join in.  When all humans have joined, have the
first player click "Start Game Now", and play some Titan.

For documentation, see the Wiki at http://wiki.github.com/dripton/Slugathon
