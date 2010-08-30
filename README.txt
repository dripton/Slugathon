Slugathon is a free (licensed under the GPLv2; see slugathon/docs/COPYING.txt)
clone of the classic Avalon Hill boardgame Titan. The focus is on playing
against other humans across the Internet.

It's still in heavy development and not enduser-friendly yet.  It may crash.

If you want to try it anyway:

1. Install all the dependencies listed at
http://wiki.github.com/dripton/Slugathon/dependencies.
(This is easy on Linux, harder on Windows or MacOS.)

2. Clone Slugathon with Git, or download and uncompress a zip or tar
version.

3. Run "python setup.py install" to install the game.  This will probably
require root permissions, so use su or sudo.

4. Add some users and passwords to ~/.slugathon/globalprefs/passwd
(See slugathon/docs/passwd.txt for an example of the format.)

5. In one terminal, run "python slugathon-server"

6. In a second terminal (on the same or a different computer) run
"python slugathon-client"

7. In a third terminal, (on the same or a different computer), run
"python slugathon-aiclient", picking a different player.  The AI
doesn't have a GUI so you'll need to set everything with command-line
arguments; use -h to list them.

(You can add up to a total of 6 players.)

8. Chat with each other in the Anteroom window.

9. Have the first player form a game, then have the other player(s) join it,
(AIs currently join all games automatically), then have the first player start
it, then play some Titan.

10. If you actually do this successfully, please let me know.

For documentation, see the Wiki at http://wiki.github.com/dripton/Slugathon
