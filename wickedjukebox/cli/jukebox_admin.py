#!/usr/bin/python
# -*- coding: utf8 -*-

from __future__ import print_function

import cmd
import logging
import sys
from os import path

from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import and_, bindparam, func, insert, select, update
from wickedjukebox import __version__, setup_logging
from wickedjukebox.demon.dbmodel import (Artist, Session, Setting, albumTable,
                                         artistTable, channelTable, genreTable,
                                         groupsTable, settingTable,
                                         song_has_genre, song_has_tag,
                                         songStandingTable, songStatsTable,
                                         songTable, usersTable)
from wickedjukebox.remotes import lastfm
from wickedjukebox.util import TerminalController, direxists

LOG = logging.getLogger(__name__)


def get_artists(glob=u"*"):
    if not glob.strip():
        glob = u"*"

    glob = glob.replace(u"*", u"%")
    query = select([artistTable],
                   artistTable.c.name.like(glob),
                   order_by=["name"]
                   )
    result = query.execute()
    return result.fetchall()


def get_albums(aname, glob=u"*"):
    if not glob.strip():
        glob = u"*"

    glob = glob.replace(u"*", u"%")
    query = select([albumTable])
    query = query.where(artistTable.c.name == aname)
    query = query.where(albumTable.c.artist_id == artistTable.c.id)
    query = query.where(albumTable.c.name.like(glob))
    query = query.order_by("name")
    result = query.execute()
    return result.fetchall()


def get_songs(bname, glob):
    if not glob.strip():
        glob = u"*"

    glob = glob.replace(u"*", u"%")
    query = select([songTable])
    query = query.where(albumTable.c.name == bname)
    query = query.where(songTable.c.album_id == albumTable.c.id)
    query = query.where(songTable.c.title.like(glob))
    query = query.order_by("title")
    result = query.execute()
    return result.fetchall()


class Console(cmd.Cmd):
    # pylint: disable=unused-argument
    #
    # Cmd subclasses require an argument "line", which is not always useful. So
    # we disable "unused-argument" messages in this class.

    # pylint: disable=no-self-use
    #
    # We disable "no-self-use" here because "Cmd" subclassed are mainly
    # wrappers and syntactic sugar for command-line interfaces. There is a good
    # chance that the functions don't need to use "self".

    __ctx_artist = "unset"
    __ctx_album = "unset"
    __path = []

    def __init__(self):
        "Bootstrap the command line interpreter"
        cmd.Cmd.__init__(self)
        self.term = TerminalController()
        self.set_promt()
        self.user_id = None

    def _orphaned_artists(self):
        """
        Return rows of (artist_id, name, song_count) of artists without
        attached songs
        """
        query = select([
            artistTable.c.id,
            artistTable.c.name,
            func.count(songTable.c.id)
        ], from_obj=[
            artistTable.outerjoin(songTable,
                                  artistTable.c.id == songTable.c.artist_id)
        ])
        query = query.group_by("artist.id, artist.name")
        query = query.order_by("name")
        for row in query.execute():
            if row[2] == 0:
                yield row

    def _orphaned_albums(self):
        """
        Return rows of (album_id, name, song_count) of albums without attached
        songs.
        """
        query = select([
            albumTable.c.id,
            albumTable.c.name,
            func.count(songTable.c.id)
        ], from_obj=[
            albumTable.outerjoin(songTable,
                                 albumTable.c.id == songTable.c.album_id)
        ])
        query = query.group_by("album.id, album.name")
        query = query.order_by("name")
        for row in query.execute():
            if row[2] == 0:
                yield row

    def _orphaned_songs(self):
        """
        Return rows of (song_id, path) of songs that are no longer on disk.
        """
        query = select([songTable.c.id, songTable.c.localpath])
        query = query.order_by("localpath")
        for row in query.execute():
            if not path.exists(row[1]):
                yield row

    def list_settings(self, channel_id=None, user_id=None):
        """
        List settings

        @param channel_id: If set, list only settings for that channel
        @param user_id: If set, list only settings for that user
        """
        sel = settingTable.select()

        if channel_id:
            sel = sel.where(settingTable.c.channel_id == int(channel_id))

        if user_id:
            sel = sel.where(settingTable.c.user_id == int(user_id))

        sel = sel.order_by("user_id", "channel_id", "var")
        print(" Channel ID | User ID | Setting                         | Value")
        previous_channel = None
        for row in sel.execute().fetchall():
            if row["channel_id"] != previous_channel:
                print(
                    "---------+------------+---------------------------+----------------")
                previous_channel = row['channel_id']
            print(" %10d | %7d | %-25s | %s" % (
                row["channel_id"],
                row["user_id"],
                row["var"],
                row["value"],
            ))

    def complete_rescan(self, line, *args):
        mediadirs = [x for x in Setting.get('mediadir', '').split(' ')
                     if direxists(x)]
        from os import listdir
        folders = []
        for root in mediadirs:
            folders.extend(listdir(root))
        candidates = filter(lambda x: x.startswith(line), folders)
        return candidates

    def emptyline(self):
        """Do nothing on empty input line"""
        pass

    def set_promt(self):
        """
        Sets the default prompt
        """
        if not self.__path:
            self.prompt = self.term.render("${GREEN}jukebox>${NORMAL} ")
        else:
            self.prompt = self.term.render(
                "${GREEN}jukebox:${BLUE}%s${GREEN}>${NORMAL} " % "/".join(self.__path))

    def get_string(self, string):
        """
        If a string is enclosed with quotes, remove them and return the proper
        string
        """
        if string == "":
            return string
        # remove quotes
        if string[0] in ['"', "'"]:
            string = string[1:-1]
        return string

    def do_quit(self, line):
        """Quits you out of Quitter."""
        print("bye")
        return 1

    def do_rescan(self, line, force=0):
        """
        Scan the defined library folders for new songs.

        SYNOPSIS
            rescan <folder>[*]

        PARAMETERS
            folder  -  Only scan files withing the named folder. If the
                       foldername ends with an asterisk (*), then all folders
                       starting with the given name will be scanned.

        EXAMPLES
            jukebox> rescan Depeche Mode
            jukebox> rescan Dep*
        """
        line = line.decode(sys.stdin.encoding)

        print(self.term.HIDE_CURSOR)
        mediadirs = [x for x in Setting.get('mediadir', '').split(' ')
                     if direxists(x)]
        import wickedjukebox.scanner
        print("Scanning inside %s" % ", ".join(mediadirs))
        try:
            wickedjukebox.scanner.scan(mediadirs[0], line)
            print("done")
        except KeyboardInterrupt:
            print("\naborted!")
        print(self.term.SHOW_CURSOR)

    def do_update_tags(self, line):
        """
        Updates song tags via Last.FM

        To avoid hammering the Lasst.FM API we will add a small sleep between
        function call, so this may take a long time!

        SYNOPSIS
            update_tags <artist>

        PARAMETERS
            artist - The artis name
        """
        line = line.decode(sys.stdin.encoding)

        sess = Session()
        api_key = Setting.get("lastfm_api_key", None)
        if not api_key:
            print("ERROR: No API key specified. You can do this it in the "
                  "settings")
            return
        api = lastfm.Api(api_key)
        artist = sess.query(Artist).filter_by(name=line).first()
        if not artist:
            sess.close()
            print("Artist %r not found" % line)
            return
        songs = artist.songs
        print("%5d songs to update" % len(songs))
        from time import sleep
        for song in songs:
            song.update_tags(api)
            sleep(1)
            print("%-40s has now %4d tags" % (song.title, len(song.tags)))

        sess.close()

    def do_orphans(self, line):
        """
        Find files that are in the database but not on disk

        SYNOPSIS
            orphans [-d] [-q]

        PARAMETERS
            -d     - If specified, this command will remove all orphaned songs
                     from the DB
            -q     - Don't pint each matching row. Print only overall info
                     (counts)
        """
        line = line.decode(sys.stdin.encoding)

        params = set([_.strip().lower() for _ in line.split()])
        delete = False
        quiet = False

        if "-d" in params:
            delete = True
        if "-q" in params:
            quiet = True

        count = 0
        for row in self._orphaned_songs():
            if not quiet:
                print("%10d %s" % (row[0], row[1]))
            count += 1
            if delete:
                del_query = songStandingTable.delete().where(
                    songStandingTable.c.song_id == row[0])
                del_query.execute()
                del_query = song_has_genre.delete().where(
                    song_has_genre.c.song_id == row[0])
                del_query.execute()
                del_query = song_has_tag.delete().where(
                    song_has_tag.c.song_id == row[0])
                del_query.execute()
                del_query = songStandingTable.delete().where(
                    songStandingTable.c.song_id == row[0])
                del_query.execute()
                del_query = songStatsTable.delete().where(
                    songStatsTable.c.song_id == row[0])
                del_query.execute()
                del_query = songTable.delete().where(
                    songTable.c.id == row[0])
                del_query.execute()
        print("%d orphaned songs found" % count)

        count = 0
        for row in self._orphaned_albums():
            if not quiet:
                print(row)
            if delete:
                del_query = albumTable.delete().where(
                    albumTable.c.id == row[0])
                del_query.execute()
            count += 1
        print("%d orphaned albums found" % count)

        count = 0
        for row in self._orphaned_artists():
            if not quiet:
                print(row)
            if delete:
                del_query = artistTable.delete().where(
                    artistTable.c.id == row[0])
                del_query.execute()
            count += 1
        print("%d orphaned artists found" % count)

    def do_genres(self, line):
        """
        Lists genres stored in the DB

        SYNOPSIS
            genres [order]

        PARAMETERS
            order  - may be one of "name" or "count". If ommitted, "count" is
                        used.
        """
        line = line.decode(sys.stdin.encoding)

        if line in ("count", ""):
            order_by = "song_count"
        elif line == "name":
            order_by = "name"

        query = select([genreTable.c.id, genreTable.c.name,
                        func.count(song_has_genre.c.song_id).label('song_count')],
                       genreTable.c.id == song_has_genre.c.genre_id,
                       group_by=genreTable.c.id,
                       order_by=order_by)
        result = query.execute()

        print(" id    | Genre                                  | count ")
        print("------+--------------------------------+-------")
        for genre in result.fetchall():
            print("%5d | %-30s | %d" % (genre.id, genre.name, genre.song_count))
        print("------+--------------------------------+-------")
        print(" id    | Genre                                  | count ")

    def do_merge_genre(self, line):
        """
        Moves genre A into genre B (only B remains!)

        SYNOPSIS
            merge_genre A B

        PARAMETERS
            Both "A" and "B" are id's to genres in the database. Use "genres"
            to get a list
        """
        line = line.decode(sys.stdin.encoding)

        try:
            old_genre, new_genre = line.split(" ")
        except Exception as ex:
            print(str(ex))
            return

        old_genre = int(old_genre)
        new_genre = int(new_genre)
        query = song_has_genre.update(
            song_has_genre.c.genre_id == bindparam("a"),
            values={'genre_id': bindparam("b")})
        query.execute(a=old_genre, b=new_genre)

    def do_genre_songs(self, line):
        """
        Lists songs of a given genre

        SYNOPSIS
            genre_songs <genre_id>
        """
        genre_id = int(line)
        query = select([
            songTable.c.id,
            artistTable.c.name.label("aname"),
            albumTable.c.name.label("bname"),
            songTable.c.title
        ], and_(
            songTable.c.id == song_has_genre.c.song_id,
            song_has_genre.c.genre_id == genre_id,
            songTable.c.artist_id == artistTable.c.id,
            songTable.c.album_id == albumTable.c.id
        ), order_by=["aname", "bname", "title"])
        result = query.execute()
        for song in result.fetchall():
            aname = song.aname if song.aname is not None else "None"
            bname = song.bname if song.bname is not None else "None"
            title = song.title if song.title is not None else "None"
            print("%5d | %-30s | %-30s | %-30s" %
                  (song.id, aname, bname, title))

    def do_rename_genre(self, line):
        """
        Renames a genre

        SYNOPSIS
            rename_genre <genre_id> <new_name>
        """
        line = line.decode(sys.stdin.encoding)

        try:
            args = line.split(" ")
            gid = int(args[0])
            name = " ".join(args[1:])
            name = self.get_string(name)
        except Exception as ex:
            print(str(ex))
            return

        query = genreTable.update(
            genreTable.c.id == bindparam("gid"),
            values={'name': bindparam("name")}
        )
        query.execute(gid=gid, name=name)

    def do_find_duplicates(self, line):
        """
        Finds duplicates based on artist/track name.

        SYNOPSIS
            find_duplicates [log_file]

        PARAMETERS
            log_file -- path to a log file
        """
        line = line.decode(sys.stdin.encoding)

        hashtable = {}
        logfile = None
        default_out = sys.stdout
        if line != '':
            try:
                if path.exists(line):
                    print("File %s exists" % line)
                    return
                logfile = open(line, 'w')
                sys.stdout = logfile
            except IOError:
                print("Unable to open %r" % line)
                return

        query = select([
            songTable.c.id,
            songTable.c.localpath,
            songTable.c.title,
            artistTable.c.name
        ], songTable.c.artist_id == artistTable.c.id)

        result = query.execute().fetchall()

        for row in result:
            key = "%s - %s" % (row[3], row[2])
            if key in hashtable:
                hashtable[key].append(row[1])
            else:
                hashtable[key] = [row[1]]

        for key in hashtable:
            if len(hashtable[key]) == 1:
                continue

            print("key: %r" % key)
            for localpath in hashtable[key]:
                print("    %r" % localpath)
            print(80 * "-")
        sys.stdout = default_out

    def do_cd(self, line):
        """
        Changes context. Three levels possible: Root -> Artist -> Album

        SYNOPSIS
            cd <path>

        PARAMETERS
            path     - name of the artist/album or ".."
        """
        line = line.decode(sys.stdin.encoding)
        arg = self.get_string(line)

        if arg.strip() == "..":
            try:
                self.__path.pop()
            except:
                pass
            self.set_promt()
            return

        if len(self.__path) == 2:
            return

        self.__path.append(arg)
        self.set_promt()

    def do_ls(self, line):
        """
        Lists entries in the current context
        """
        line = line.decode(sys.stdin.encoding)

        glob = self.get_string(line)
        if not self.__path:
            artists = get_artists(glob)
            for artist in artists:
                if artist.name is None:
                    continue
                print(artist.name)
        elif len(self.__path) == 1:
            albums = get_albums(self.__path[-1], glob)
            for album in albums:
                if album.name is None:
                    continue
                print(album.name)
        elif len(self.__path) == 2:
            songs = get_songs(self.__path[-1], glob)
            for song in songs:
                if song.title is None:
                    continue
                print(song.title)

    def do_online_users(self, line):
        """
        Lists users currently online in the web interface
        """
        query = select([usersTable], func.addtime(
            usersTable.c.proof_of_life, '0:03:00') > func.now())
        result = query.execute()
        for row in result.fetchall():
            print(row)

    def do_settings(self, line):
        """
        Lists or set application settings

        SYNOPSIS
            settings [channel_id [user_id [setting value]]]

        PARAMETERS
            channel_id - if specified, list only settings of that channel
            user_id    - if specified, list only settings for that user (and
                         channel)
            setting    - the setting name (when modifying the setting)
            value      - if specified, change that setting
        """
        line = line.decode(sys.stdin.encoding)
        params = line.split()

        if len(params) <= 2:
            self.list_settings(*params)
            return

        if len(params) == 3:
            channel_id, user_id, var = params
            # we already have the setting. Go and update it
            upq = update(settingTable)
            upq = upq.where(settingTable.c.channel_id == int(channel_id))
            upq = upq.where(settingTable.c.user_id == int(user_id))
            upq = upq.where(settingTable.c.var == var)
            upq = upq.values({"value": None})
            upq.execute()
            print('Setting %s-%s-%s reverted to "NULL"' % (
                channel_id, user_id, var))
            return

        channel_id, user_id, var, value = params
        testsel = select([settingTable.c.value])
        testsel = testsel.where(settingTable.c.channel_id == int(channel_id))
        testsel = testsel.where(settingTable.c.user_id == int(user_id))
        testsel = testsel.where(settingTable.c.var == var)
        res = testsel.execute()
        if res and res.fetchone():
            # we already have the setting. Go and update it
            upq = update(settingTable)
            upq = upq.where(settingTable.c.channel_id == int(channel_id))
            upq = upq.where(settingTable.c.user_id == int(user_id))
            upq = upq.where(settingTable.c.var == var)
            upq = upq.values({"value": value})
            upq.execute()
        else:
            # new setting -> insert
            insq = insert(settingTable)
            insq = insq.values({
                "channel_id": int(channel_id),
                "user_id": int(user_id),
                "var": var,
                "value": value
            })
            insq.execute()
        LOG.debug("New setting stored: %r" % params)

    def do_channel_settings(self, line):
        """
        Modify the settings of one channel.

        SYNOPSIS
            channel_settings <channel> <settings>

        PARAMETERS
            channel - The channel name
        """
        line = line.decode(sys.stdin.encoding)
        params = line.split(' ', 1)

        if len(params) != 2:
            print("Error. See `help channel_settings`")
            return

        name, params = params

        query = channelTable.update(channelTable.c.name == name,
                                    values={'backend_params': params})
        query.execute()

    def do_channels(self, line):
        """
        List existing channels.
        """
        line = line.decode(sys.stdin.encoding)

        sel = select([
            channelTable.c.name,
            channelTable.c.backend,
            channelTable.c.backend_params])
        res = sel.execute()
        for row in res.fetchall():
            print("%-15s | %-10s | %s" % tuple(row))

    def do_add_channel(self, line):
        """
        Adds a new channel to the database.

        SYNOPSIS
            add_channel <name> <backend> <params>

        PARAMETERS
            name            - The channel name
            backend         - Backend (currently tested and supported:
                              'icecast')
            backend_params  - Parameters for the backend.
        """
        line = line.decode(sys.stdin.encoding)
        params = line.split(' ', 2)

        if len(params) != 3:
            print("Error. See `help add_channel`")
            return

        name, back, be_parms = params
        insq = insert(channelTable)
        insq = insq.values({
            "name": name,
            "backend": back,
            "backend_params": be_parms,
        })
        insq.execute()

    def do_test_random(self, line):
        """
        Peeks at the top 10 elements returned from a random query

        SYNOPSIS
            test_random <random_mode_name> [channel_id]

        PARAMETERS
            random_mode_name - The name of the random mode to test
            channel_id       - The channel ID. If none is given, "1" is
                               assumed as default.
        """
        line = line.decode(sys.stdin.encoding)
        params = line.split()

        if not params:
            print("You need to specify a random mode!")
            return

        if len(params) > 2:
            print("You did not pass the right number of params. Expected 1 "
                  "but got %d" % len(params))

        if len(params) == 2 and not params[1].isdigit():
            print("The second parameter must be numeric!")

        if len(params) == 1:
            # set the default value for the channel
            params.append(1)

        # unpack. For readability
        strat_name, channel_id = params

        import wickedjukebox.demon.playmodes
        try:
            strategy = wickedjukebox.demon.playmodes.create(strat_name)
            strategy.bootstrap(channel_id)
        except ImportError:
            print("Unknown random mode!")
            return

        result = strategy.test(channel_id)
        if not result:
            print("No results returned!")
            return

        from pprint import pprint

        for row in result:
            if not row:
                continue
            data, stat = row
            print(data)
            pprint(stat)

    def do_login(self, line):
        """
        Creates a user-session.
        """
        from getpass import getpass
        username = raw_input(self.term.render(
            '${YELLOW}%20s:${NORMAL} ' % 'Login'))
        passwd = getpass(self.term.render(
            '${YELLOW}%20s:${NORMAL} ' % 'Password'))
        username = username.decode(sys.stdin.encoding)
        passwd = passwd.decode(sys.stdin.encoding)
        query = select([usersTable.c.id])
        query = query.where(usersTable.c.username == username)
        identity = query.execute().fetchone()
        if not identity:
            print(self.term.render('${RED}Acceess denied!${NORMAL}'))
            return

        self.user_id = identity[0]

    def do_register(self, line):
        """
        Registers a new user.
        """
        from getpass import getpass
        from hashlib import md5
        from os import urandom
        try:
            username = raw_input(self.term.render(
                '${YELLOW}%20s:${NORMAL} ' % 'Login'))
            passwd = getpass(self.term.render(
                '${YELLOW}%20s:${NORMAL} ' % 'Password'))
            passwd2 = getpass(self.term.render(
                '${YELLOW}%20s:${NORMAL} ' % 'Verify password'))
            username = username.decode(sys.stdin.encoding)
        except KeyboardInterrupt:
            print(self.term.render('${YELLOW}Aborted!${NORMAL}'))
            return

        if passwd != passwd2:
            print(self.term.render('${RED}Passwords do not match!${NORMAL}'))
            return

        passwd = md5(passwd.decode(sys.stdin.encoding)).hexdigest()
        group_select = select([groupsTable.c.id])
        group_select = group_select.where(groupsTable.c.title == 'User')
        insq = insert(usersTable)
        insq = insq.values({
            'username': username,
            'cookie': md5(urandom(30)).hexdigest(),
            'password': passwd,
            'fullname': username,
            'email': '',
            'credits': 10,
            'group_id': group_select.scalar(),
            'added': func.now(),
            'proof_of_life': func.now(),
            'IP': '',
            'picture': '{0}.jpg'.format(username.encode('ascii', 'replace')),
            'lifetime': 0
        })

        try:
            insq.execute()
            print(self.term.render('${GREEN}User created!${NORMAL}\n'
                                   'You may now login.'))
        except IntegrityError as exc:
            print(self.term.render('${RED}ERROR:${NORMAL}%s' % exc))

    def do_add_group(self, line):
        """
        Adds a new group.
        """
        line = line.decode(sys.stdin.encoding)

        insq = insert(groupsTable)
        insq = insq.values({
            'title': line.strip()
        })
        insq.execute()
        query = select([groupsTable.c.id, groupsTable.c.title])
        for group_id, title in query.execute():
            print(group_id, title)

    do_exit = do_quit
    do_q = do_quit
    do_EOF = do_quit


def main():
    setup_logging()
    logging.getLogger('wickedjukebox.scanner').setLevel(logging.WARNING)
    # TODO: Catch logging messages from the scanner!
    print(" Wicked Jukebox {0} ".format(__version__).center(79, '#'))
    app = Console()
    app.cmdloop()
