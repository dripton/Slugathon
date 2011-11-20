Slugathon is a free (licensed under the GPLv2; see slugathon/docs/COPYING.txt)
clone of the classic Avalon Hill boardgame Titan. The focus is on playing
against other humans across the Internet.

Installation is still kind of rough, but if you want to try it:

1. Install all the dependencies listed at
http://wiki.github.com/dripton/Slugathon/dependencies.
See
http://wiki.github.com/dripton/Slugathon/Building-on-Linux
http://wiki.github.com/dripton/Slugathon/Building-on-Mac-OS
http://wiki.github.com/dripton/Slugathon/Building-on-Windows
for details.

2. Clone Slugathon with Git, or download and uncompress a zip or tar
version.

3. Run "python setup.py install" to install the game.  This will probably
require root permissions, so use su or sudo.

4. Add some users and passwords to ~/.slugathon/globalprefs/passwd
(See slugathon/docs/passwd.txt for an example of the format.)

5. In one terminal, run "python slugathon-server"

6. In a second terminal (on the same or a different computer) run
"python slugathon-client"

7. If you want multiple human players, then in a third terminal, (on the same
or a different computer), run "python slugathon-client", picking a different
player.

(You can add up to a total of 6 players.)

8. Chat with each other in the Anteroom window.

9. Have the first player form a game, then have the other player(s) join it.
If you want AI players, then set "Min players" to more than the number of
human players, and AIs will join in.  When all humans have joined, have the
first player click "Start Game Now", and play some Titan.

10. If you actually do this successfully, please let me know.

For documentation, see the Wiki at http://wiki.github.com/dripton/Slugathon
