Slugathon is a free (licensed under the GPLv2; see slugathon/docs/COPYING.txt)
clone of the classic Avalon Hill boardgame Titan. The focus is on playing
against other humans across the Internet.

It's still in heavy development and not enduser-friendly yet.  It may crash.
There's no AI yet, so you have to play all the players, or else find a friend
or two to help.

If you want to try it anyway:

1. Install all the dependencies listed at
http://wiki.github.com/dripton/Slugathon/dependencies.

2. Add some users and passwords to ~/.slugathon/globalprefs/passwd
(See slugathon/docs/passwd.txt for an example of the format.)

3. In one terminal run "python slugathon-server"

4. In a second terminal (on the same or a different computer), cd to slugathon
and run "python slugathon-client"

5. In a third terminal, (on the same or a different computer), cd to slugathon
and run "python slugathon-client", picking a different player.  You can add up
to a total of 6 players.

6. Chat with each other in the Anteroom window.

7. Have the first player form a game, then have the other player(s) join it,
then have the first player start it, then play some Titan.

8. If you actually did this successfully, please let me know.

For documentation, see the Wiki at http://wiki.github.com/dripton/Slugathon
