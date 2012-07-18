"""
Test script for the jukebox model.
"""

def main():
    import logging
    import sys
    from wickedjukebox.model.fs import Mediadir
    import wickedjukebox.model.db as db
    from os import unlink
    try:
        unlink('data.db')
    except Exception as exc:
        print >>sys.stderr, exc

    db.init('sqlite:///data.db')

    sess = db.SESSION()
    log = logging.getLogger(__name__)

    logging.basicConfig(level=logging.DEBUG)
    md = Mediadir(u'/media/')

    def processor(meta):
        if not meta.titles:
            log.warning(u'{0} did not have a title... skipping!'.format(meta))
            return

        song = db.Song.get_or_add(sess, meta.titles[0])

        if meta.artists:
            psong = db.PerformedSong()
            psong.song = song.id
            psong.band = db.Band.get_or_add(sess, meta.artists[0]).id
            if psong.song:
                sess.add(psong)
            else:
                print ">>>>>>>", psong

    md.walk(processor=processor)
    sess.commit()

if __name__ == '__main__':
    main()
