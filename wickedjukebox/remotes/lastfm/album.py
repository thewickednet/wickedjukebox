#!/usr/bin/env python
"""Module for calling Album related last.fm web services API methods"""

__author__ = "Abhinav Sarkar <abhinav@abhinavsarkar.net>"
__version__ = "0.2"
__license__ = "GNU Lesser General Public License"
__package__ = "lastfm"

from lastfm.base import LastfmBase
from lastfm.mixins import Cacheable, Searchable, Taggable
from lastfm.decorators import cached_property, top_property

class Album(LastfmBase, Cacheable, Searchable, Taggable):
    """A class representing an album."""
    def init(self,
                 api,
                 name = None,
                 artist = None,
                 id = None,
                 mbid = None,
                 url = None,
                 release_date = None,
                 image = None,
                 stats = None,
                 top_tags = None,
                 streamable = None,
                 subject = None):
        """
        Create an Album object by providing all the data related to it.
        
        @param api:             an instance of L{Api}
        @type api:              L{Api}
        @param name:            the album name
        @type name:             L{str}
        @param artist:          the album artist name 
        @type artist:           L{Artist}
        @param id:              the album ID
        @type id:               L{str}
        @param mbid:            MBID of the album
        @type mbid:             L{str}
        @param url:             URL of the album on last.fm
        @type url:              L{str}
        @param release_date:    release date of the album
        @type release_date:     C{datetime.datetime}
        @param image:           the cover images of the album in various sizes
        @type image:            L{dict}
        @param stats:           the album statistics
        @type stats:            L{Stats}
        @param top_tags:        top tags for the album
        @type top_tags:         L{list} of L{Tag}
        @param streamable:      flag indicating if the album is streamable from last.fm
        @type streamable:       L{bool}
        @param subject:         the subject to which this instance belongs to
        @type subject:          L{User} OR L{Artist} OR L{Tag} OR L{WeeklyChart}
        
        @raise InvalidParametersError: If an instance of L{Api} is not provided as the first
                                       parameter then an Exception is raised.
        """
        if not isinstance(api, Api):
            raise InvalidParametersError("api reference must be supplied as an argument")
        Taggable.init(self, api)
        self._api = api
        self._name = name
        self._artist = artist
        self._id = id
        self._mbid = mbid
        self._url = url
        self._release_date = release_date
        self._image = image
        self._stats = stats and Stats(
                             subject = self,
                             listeners = stats.listeners,
                             playcount = stats.playcount,
                             match = stats.match,
                             rank = stats.rank
                            )
        self._top_tags = top_tags
        self._streamable = streamable
        self._subject = subject
    
    @property
    def name(self):
        """
        name of the album
        @rtype: L{str}
        """
        return self._name
    
    @property
    def artist(self):
        """
        artist of the album
        @rtype: L{Artist}
        """
        return self._artist
    
    @property
    def id(self):
        """
        id of the album
        @rtype: L{int}
        """
        if self._id is None:
            self._fill_info()
        return self._id

    @property
    def mbid(self):
        """
        MBID of the album
        @rtype: L{str}
        """
        if self._mbid is None:
            self._fill_info()
        return self._mbid

    @property
    def url(self):
        """
        url of the album's page
        @rtype: L{str}
        """
        if self._url is None:
            self._fill_info()
        return self._url

    @property
    def release_date(self):
        """
        release date of the album
        @rtype: C{datetime.datetime}
        """
        if self._release_date is None:
            self._fill_info()
        return self._release_date

    @property
    def image(self):
        """
        cover images of the album
        @rtype: L{dict}
        """
        if self._image is None:
            self._fill_info()
        return self._image

    @property
    def stats(self):
        """
        stats related to the album
        @rtype: L{Stats}
        """
        if self._stats is None:
            self._fill_info()
        return self._stats
    
    @property
    def streamable(self):
        """
        is the album streamable on last.fm
        @rtype: L{bool}
        """
        return self._streamable

    @cached_property
    def top_tags(self):
        """
        top tags for the album
        @rtype: L{list} of L{Tag}
        """
        params = {'method': 'album.getInfo'}
        if self.artist and self.name:
            params.update({'artist': self.artist.name, 'album': self.name})
        elif self.mbid:
            params.update({'mbid': self.mbid})
        data = self._api._fetch_data(params).find('album')
        return [
                Tag(
                    self._api,
                    subject = self,
                    name = t.findtext('name'),
                    url = t.findtext('url')
                    )
                for t in data.findall('toptags/tag')
                ]

    @top_property("top_tags")
    def top_tag(self):
        """
        top tag for the album
        @rtype: L{Tag}
        """
        pass
    
    @cached_property
    def playlist(self):
        """
        playlist for the album
        @rtype: L{Playlist}
        """
        return Playlist.fetch(self._api, "lastfm://playlist/album/%s" % self.id)
    
    @staticmethod
    def get_info(api, artist = None, album = None, mbid = None):
        """
        Get the data for the album.
        
        @param api:      an instance of L{Api}
        @type api:       L{Api}
        @param artist:   the album artist name 
        @type artist:    L{str} OR L{Artist}
        @param album:    the album name
        @type album:     L{str}
        @param mbid:     MBID of the album
        @type mbid:      L{str}
        
        @return:         an Album object corresponding to the provided album name
        @rtype:          L{Album}
        
        @raise lastfm.InvalidParametersError: Either album and artist parameters or 
                                              mbid parameter has to be provided. 
                                              Otherwise exception is raised.
        
        @note: Use the L{Api.get_album} method instead of using this method directly.
        """
        data = Album._fetch_data(api, artist, album, mbid)
        a = Album(
                  api,
                  name = data.findtext('name'),
                  artist = Artist(
                                  api,
                                  name = data.findtext('artist'),
                                  ),
                  )
        a._fill_info()
        return a
        
    def _default_params(self, extra_params = {}):
        if not (self.artist and self.name):
            raise InvalidParametersError("artist and album have to be provided.")
        params = {'artist': self.artist.name, 'album': self.name}
        params.update(extra_params)
        return params
    
    @staticmethod
    def _fetch_data(api,
                artist = None,
                album = None,
                mbid = None):
        params = {'method': 'album.getInfo'}
        if not ((artist and album) or mbid):
            raise InvalidParametersError("either (artist and album) or mbid has to be given as argument.")
        if artist and album:
            params.update({'artist': artist, 'album': album})
        elif mbid:
            params.update({'mbid': mbid})
        return api._fetch_data(params).find('album')
    
    def _fill_info(self):
        data = Album._fetch_data(self._api, self.artist.name, self.name)
        self._id = int(data.findtext('id'))
        self._mbid = data.findtext('mbid')
        self._url = data.findtext('url')
        self._release_date = data.findtext('releasedate') and data.findtext('releasedate').strip() and \
                            datetime(*(time.strptime(data.findtext('releasedate').strip(), '%d %b %Y, 00:00')[0:6]))
        self._image = dict([(i.get('size'), i.text) for i in data.findall('image')])
        if not self._stats:
            self._stats = Stats(
                       subject = self,
                       listeners = int(data.findtext('listeners')),
                       playcount = int(data.findtext('playcount')),
                       )
        self._top_tags = [
                    Tag(
                        self._api,
                        subject = self,
                        name = t.findtext('name'),
                        url = t.findtext('url')
                        ) 
                    for t in data.findall('toptags/tag')
                    ]
                         
    @staticmethod
    def _search_yield_func(api, album):
        return Album(
                      api,
                      name = album.findtext('name'),
                      artist = Artist(
                                      api,
                                      name = album.findtext('artist')
                                      ),
                      id = int(album.findtext('id')),
                      url = album.findtext('url'),
                      image = dict([(i.get('size'), i.text) for i in album.findall('image')]),
                      streamable = (album.findtext('streamable') == '1'),
                      )
    
    @staticmethod
    def _hash_func(*args, **kwds):
        try:
            return hash("%s%s" % (kwds['name'], hash(kwds['artist'])))
        except KeyError:
            raise InvalidParametersError("name and artist have to be provided for hashing")
        
    def __hash__(self):
        return self.__class__._hash_func(name = self.name, artist = self.artist)
        
    def __eq__(self, other):
        if self.id and other.id:
            return self.id == other.id
        if self.mbid and other.mbid:
            return self.mbid == other.mbid
        if self.url and other.url:
            return self.url == other.url
        if (self.name and self.artist) and (other.name and other.artist):
            return (self.name == other.name) and (self.artist == other.artist)
        return super(Album, self).__eq__(other)
    
    def __lt__(self, other):
        return self.name < other.name
    
    def __repr__(self):
        return "<lastfm.Album: '%s' by %s>" % (self.name, self.artist.name)
        
                     
from datetime import datetime
import time

from lastfm.api import Api
from lastfm.artist import Artist
from lastfm.error import InvalidParametersError
from lastfm.playlist import Playlist
from lastfm.stats import Stats
from lastfm.tag import Tag