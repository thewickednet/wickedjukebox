"""
Test script for the jukebox model.
"""

def main():
    import logging
    import sys
    from datetime import datetime
    from wickedjukebox.model.fs import Mediadir
    import wickedjukebox.model.db as db
    from os import unlink
    try:
        unlink('data.db')
    except Exception as exc:
        print >>sys.stderr, exc

    db.init('sqlite:///data.db')
    db.BASE.metadata.create_all()

    sess = db.SESSION()
    log = logging.getLogger(__name__)

    logging.basicConfig(level=logging.DEBUG)
    md = Mediadir(u'/media/')

    def processor(meta):
        if not meta.titles:
            log.warning(u'{0} did not have a title... skipping!'.format(meta))
            return

        mw = db.MusicalWork.get_or_add(sess, meta.titles[0])
        band = db.Band.get_or_add(sess, meta.artists[0])
        album = db.Album.get_or_add(sess, meta.albums[0])
        album.release_date = meta.date

        mm = db.MusicalManifestation.get_or_add(sess, band, mw)
        mm.duration = meta.length
        mm.release_date = meta.date
        mm.filename = meta.filename
        if album:
            mm.albums.append(album)
        mm.last_scanned = datetime.now()

    md.walk(processor=processor)
    sess.commit()

if __name__ == '__main__':
    main()
