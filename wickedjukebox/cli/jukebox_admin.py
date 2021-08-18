#!/usr/bin/python

import argparse


import cmd
import logging
import sys
from os import path
from os.path import exists
from wickedjukebox.scanner import scan

from blessings import Terminal
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import and_, bindparam, func, insert, select, update
from wickedjukebox import __version__, setup_logging
from wickedjukebox.demon.dbmodel import (Artist, Session, Setting, albumTable,
                                         artistTable, channelTable, genreTable,
                                         groupsTable, settingTable,
                                         song_has_genre, song_has_tag,
                                         songStandingTable, songStatsTable,
                                         songTable, usersTable)

LOG = logging.getLogger(__name__)


def colorprompt(term, color, label):
    return '{color}{label:>20}{normal} '.format(
        color=getattr(term, color),
        label=label,
        normal=term.normal)


def get_artists(glob="*"):
    # type: (str, str) -> Iterable
    if not glob.strip():
        glob = "*"

    glob = glob.replace("*", "%")
    query = select([artistTable],
                   artistTable.c.name.like(glob),
                   order_by=["name"]
                   )
    result = query.execute()
    return result.fetchall()


def get_albums(aname, glob="*"):
    # type: (str, str) -> Iterable
    if not glob.strip():
        glob = "*"

    glob = glob.replace("*", "%")
    query = select([albumTable])
    query = query.where(artistTable.c.name == aname)
    query = query.where(albumTable.c.artist_id == artistTable.c.id)
    query = query.where(albumTable.c.name.like(glob))
    query = query.order_by("name")
    result = query.execute()
    return result.fetchall()


def get_songs(bname, glob):
    # type: (str, str) -> Iterable
    if not glob.strip():
        glob = "*"

    glob = glob.replace("*", "%")
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

    # pylint: disable=too-many-public-methods
    #
    # Having many public methods is normal in Cmd subclasses

    __ctx_artist = "unset"
    __ctx_album = "unset"
    __path = []  # type: List[str]

    def __init__(self):
        # type: () -> None
        "Bootstrap the command line interpreter"
        cmd.Cmd.__init__(self)
        self.term = Terminal()
        self.set_promt()
        self.user_id = None

    def _orphaned_artists(self):
        # type: () -> Generator[Tuple[int, str, int], None, None]
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
        # type: () -> Generator[Tuple[int, str, int], None, None]
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
        # type: () -> Generator[Tuple[int, str], None, None]
        """
        Return rows of (song_id, path) of songs that are no longer on disk.
        """
        query = select([songTable.c.id, songTable.c.localpath])
        query = query.order_by("localpath")
        for row in query.execute():
            if not path.exists(row[1]):
                yield row

    def complete_rescan(self, line):
        # type: (str) -> List[str]
        mediadirs = [x for x in Setting.get('mediadir', '').split(' ')
                     if exists(x)]
        from os import listdir
        folders = []
        for root in mediadirs:
            folders.extend(listdir(root))
        candidates = [x for x in folders if x.startswith(line)]
        return candidates

    def emptyline(self):
        # type: () -> None
        """Do nothing on empty input line"""
        pass

    def set_promt(self):
        # type: () -> None
        """
        Sets the default prompt
        """
        if not self.__path:
            self.prompt = self.term.green('jukebox> ')
        else:
            self.prompt = ("{t.green}jukebox:{t.blue}{path}{t.green}>"
                           "{t.normal} ").format(
                t=self.term,
                path="/".join(self.__path)
            )

    def get_string(self, string):
        # type: (str) -> str
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
        # type: (str) -> None
        """Quits you out of Quitter."""
        print("bye")
        return 1

    def do_update_tags(self, line):
        # type: (str) -> None
        """
        Updates song tags via Last.FM

        To avoid hammering the Lasst.FM API we will add a small sleep between
        function call, so this may take a long time!

        SYNOPSIS
            update_tags <artist>

        PARAMETERS
            artist - The artis name
        """
        print('This is currently not implemented for Python 3')
        # TODO sess = Session()
        # TODO api_key = Setting.get("lastfm_api_key", None)
        # TODO if not api_key:
        # TODO     print("ERROR: No API key specified. You can do this it in the "
        # TODO           "settings")
        # TODO     return
        # TODO api = lastfm.Api(api_key)
        # TODO artist = sess.query(Artist).filter_by(name=line).first()
        # TODO if not artist:
        # TODO     sess.close()
        # TODO     print("Artist %r not found" % line)
        # TODO     return
        # TODO songs = artist.songs
        # TODO print("%5d songs to update" % len(songs))
        # TODO from time import sleep
        # TODO for song in songs:
        # TODO     song.update_tags(api)
        # TODO     sleep(1)
        # TODO     print("%-40s has now %4d tags" % (song.title, len(song.tags)))

        # TODO sess.close()

    def do_orphans(self, line):
        # type: (str) -> None
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
        # type: (str) -> None
        """
        Lists genres stored in the DB

        SYNOPSIS
            genres [order]

        PARAMETERS
            order  - may be one of "name" or "count". If ommitted, "count" is
                        used.
        """
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
            print("%5d | %-30s | %d" %
                  (genre.id, genre.name, genre.song_count))
        print("------+--------------------------------+-------")
        print(" id    | Genre                                  | count ")

    def do_merge_genre(self, line):
        # type: (str) -> None
        """
        Moves genre A into genre B (only B remains!)

        SYNOPSIS
            merge_genre A B

        PARAMETERS
            Both "A" and "B" are id's to genres in the database. Use "genres"
            to get a list
        """
        try:
            old_genre, new_genre = line.split(" ")
        except Exception as ex:  # pylint: disable=broad-except
            print(str(ex))
            return

        old_genre = int(old_genre)
        new_genre = int(new_genre)
        query = song_has_genre.update(
            song_has_genre.c.genre_id == bindparam("a"),
            values={'genre_id': bindparam("b")})
        query.execute(a=old_genre, b=new_genre)

    def do_genre_songs(self, line):
        # type: (str) -> None
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
        # type: (str) -> None
        """
        Renames a genre

        SYNOPSIS
            rename_genre <genre_id> <new_name>
        """
        try:
            args = line.split(" ")
            gid = int(args[0])
            name = " ".join(args[1:])
            name = self.get_string(name)
        except Exception as ex:  # pylint: disable=broad-except
            print(str(ex))
            return

        query = genreTable.update(
            genreTable.c.id == bindparam("gid"),
            values={'name': bindparam("name")}
        )
        query.execute(gid=gid, name=name)

    def do_find_duplicates(self, line):
        # type: (str) -> None
        """
        Finds duplicates based on artist/track name.

        SYNOPSIS
            find_duplicates [log_file]

        PARAMETERS
            log_file -- path to a log file
        """
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
        # type: (str) -> None
        """
        Changes context. Three levels possible: Root -> Artist -> Album

        SYNOPSIS
            cd <path>

        PARAMETERS
            path     - name of the artist/album or ".."
        """
        arg = self.get_string(line)

        if arg.strip() == "..":
            if self.__path:
                self.__path.pop()
            self.set_promt()
            return

        if len(self.__path) == 2:
            return

        self.__path.append(arg)
        self.set_promt()

    def do_ls(self, line):
        # type: (str) -> None
        """
        Lists entries in the current context
        """
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
        # type: (str) -> None
        """
        Lists users currently online in the web interface
        """
        query = select([usersTable], func.addtime(
            usersTable.c.proof_of_life, '0:03:00') > func.now())
        result = query.execute()
        for row in result.fetchall():
            print(row)

    def do_channels(self, line):
        # type: (str) -> None
        """
        List existing channels.
        """
        sel = select([
            channelTable.c.name,
            channelTable.c.backend,
            channelTable.c.backend_params])
        res = sel.execute()
        for row in res.fetchall():
            print("%-15s | %-10s | %s" % tuple(row))

    def do_add_channel(self, line):
        # type: (str) -> None
        """
        Adds a new channel to the database.

        SYNOPSIS
            add_channel <name> <backend> <params>

        PARAMETERS
            name            - The channel name
            backend         - Backend (currently tested and supported:
                              'mpd')
            backend_params  - Parameters for the backend (comma-separated
                              key/avlue pairs.)

        EXAMPLE
            add_channel mychannel mpd host=127.0.0.1,port=6600
        """
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
        # type: (str) -> None
        """
        Peeks at the top 10 elements returned from a random query

        SYNOPSIS
            test_random <random_mode_name> [channel_id]

        PARAMETERS
            random_mode_name - The name of the random mode to test
            channel_id       - The channel ID. If none is given, "1" is
                               assumed as default.
        """
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
        # type: (str) -> None
        """
        Creates a user-session.
        """
        from getpass import getpass
        username = input(colorprompt(self.term, 'yellow', 'Login'))
        passwd = getpass(colorprompt(self.term, 'yellow', 'Password'))
        username = username.decode(sys.stdin.encoding)
        passwd = passwd.decode(sys.stdin.encoding)
        query = select([usersTable.c.id])
        query = query.where(usersTable.c.username == username)
        identity = query.execute().fetchone()
        if not identity:
            print('{t.red}Acceess denied!{t.normal}'.format(t=self.term))
            return

        self.user_id = identity[0]

    def do_register(self, line):
        # type: (str) -> None
        """
        Registers a new user.
        """
        from getpass import getpass
        from hashlib import md5
        from os import urandom
        try:
            username = input(colorprompt(self.term, 'yellow', 'Login'))
            passwd = getpass(colorprompt(self.term, 'yellow', 'Password'))
            passwd2 = getpass(colorprompt(
                self.term, 'yellow', 'Verify password'))
            username = username.decode(sys.stdin.encoding)
        except KeyboardInterrupt:
            print(self.term.yellow('Aborted!'))
            return

        if passwd != passwd2:
            print(self.term.red('Passwords do not match!'))
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
            print(self.term.green('User created!\nYou may now login.'))
        except IntegrityError as exc:
            print(self.term.red('ERROR:%s' % exc))

    def do_add_group(self, line: str) -> None:
        """
        Adds a new user-group to the database.
        """
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


def process_rescan(args: argparse.Namespace) -> int:
    for path in args.path:
        scan(path)
    return 0

def parse_args() -> argparse.Namespace:
    """
    Parses the command-line arguments
    """
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="Subcommands help")
    rescan_parser = subparsers.add_parser("rescan")
    rescan_parser.add_argument("path", nargs=1)
    rescan_parser.set_defaults(func=process_rescan)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return args.func(args)
    setup_logging()
    logging.getLogger('wickedjukebox.scanner').setLevel(logging.WARNING)
    # TODO: Catch logging messages from the scanner!
    print(" Wicked Jukebox {0} ".format(__version__).center(79, '#'))
    app = Console()
    app.cmdloop()
