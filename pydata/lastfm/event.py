#!/usr/bin/env python
"""Module for calling Event related last.fm web services API methods"""

__author__ = "Abhinav Sarkar <abhinav@abhinavsarkar.net>"
__version__ = "0.2"
__license__ = "GNU Lesser General Public License"
__package__ = "lastfm"

from lastfm.base import LastfmBase
from lastfm.mixins import Cacheable, Sharable, Shoutable

class Event(LastfmBase, Cacheable, Sharable, Shoutable):
    """A class representing an event."""
    STATUS_ATTENDING = 0
    STATUS_MAYBE = 1
    STATUS_NOT = 2

    def init(self,
                 api,
                 id = None,
                 title = None,
                 artists = None,
                 headliner = None,
                 venue = None,
                 start_date = None,
                 description = None,
                 image = None,
                 url = None,
                 stats = None,
                 tag = None,
                 **kwargs):
        """
        Create an Event object by providing all the data related to it.
        
        @param api:             an instance of L{Api}
        @type api:              L{Api}
        @param id:              ID of the event
        @type id:               L{int}
        @param title:           title of the event
        @type title:            L{str}
        @param artists:         artists performing in the event
        @type artists:          L{list} of L{Artist}
        @param headliner:       headliner artist of the event
        @type headliner:        L{Artist}
        @param venue:           venue of the event
        @type venue:            L{Venue}
        @param start_date:      start date and time of the event
        @type start_date:       C{datetime.datetime}
        @param description:     description of the event
        @type description:      L{str}
        @param image:           poster images of the event in various sizes
        @type image:            L{dict}
        @param url:             URL of the event on last.fm
        @type url:              L{str}
        @param stats:           the statistics of the event (attendance and no. of reviews)
        @type stats:            L{Stats}
        @param tag:             tag for the event
        @type tag:              L{str}
        """
        if not isinstance(api, Api):
            raise InvalidParametersError("api reference must be supplied as an argument")
        Sharable.init(self, api)
        Shoutable.init(self, api)
        
        self._api = api
        self._id = id
        self._title = title
        self._artists = artists
        self._headliner = headliner
        self._venue = venue
        self._start_date = start_date
        self._description = description
        self._image = image
        self._url = url
        self._stats = stats and Stats(
                             subject = self,
                             attendance = stats.attendance,
                             reviews = stats.reviews
                            )
        self._tag = tag

    @property
    def id(self):
        """
        id of the event
        @rtype: L{int}
        """
        return self._id

    @property
    def title(self):
        """
        title of the event
        @rtype: L{str}
        """
        return self._title

    @property
    def artists(self):
        """
        artists performing in the event
        @rtype: L{list} of L{Artist}
        """
        return self._artists

    @property
    def headliner(self):
        """
        headliner artist of the event
        @rtype: L{Artist}
        """
        return self._headliner

    @property
    def venue(self):
        """
        venue of the event
        @rtype: L{Venue}
        """
        return self._venue

    @property
    def start_date(self):
        """
        start date of the event
        @rtype: C{datetime.datetime}
        """
        return self._start_date

    @property
    def description(self):
        """
        description of the event
        @rtype: L{str}
        """
        return self._description

    @property
    def image(self):
        """
        poster of the event
        @rtype: L{dict}
        """
        return self._image

    @property
    def url(self):
        """
        url of the event's page
        @rtype: L{str}
        """
        return self._url

    @property
    def stats(self):
        """
        statistics for the event
        @rtype: L{Stats}
        """
        return self._stats

    @property
    def tag(self):
        """
        tag for the event
        @rtype: L{str}
        """
        return self._tag

    def attend(self, status = STATUS_ATTENDING):
        """
        Set the attendance status of the authenticated user for this event.
        
        @param status:    attendance status, should be one of: 
                          L{Event.STATUS_ATTENDING} OR L{Event.STATUS_MAYBE} OR L{Event.STATUS_NOT}
        @type status:     L{int}
        
        @raise InvalidParametersError: If status parameters is not one of the allowed values
                                       then an exception is raised.
        """
        if status not in [Event.STATUS_ATTENDING, Event.STATUS_MAYBE, Event.STATUS_NOT]:
            InvalidParametersError("status has to be 0, 1 or 2")
        params = self._default_params({'method': 'event.attend', 'status': status})
        self._api._post_data(params)

    @staticmethod
    def get_info(api, event):
        """
        Get the data for the event.
        
        @param api:      an instance of L{Api}
        @type api:       L{Api}
        @param event:    ID of the event
        @type event:     L{int}
        
        @return:         an Event object corresponding to the provided event id
        @rtype:          L{Event}
        
        @note: Use the L{Api.get_event} method instead of using this method directly.        
        """
        params = {'method': 'event.getInfo', 'event': event}
        data = api._fetch_data(params).find('event')
        return Event.create_from_data(api, data)

    @staticmethod
    def create_from_data(api, data):
        """
        Create the Event object from the provided XML element.
        
        @param api:      an instance of L{Api}
        @type api:       L{Api}
        @param data:     XML element
        @type data:      C{xml.etree.ElementTree.Element}
        
        @return:         an Event object corresponding to the provided XML element
        @rtype:          L{Event}
        
        @note: Use the L{Api.get_event} method instead of using this method directly.
        """
        start_date = None

        if data.findtext('startTime') is not None:
            start_date = datetime(*(
                time.strptime(
                    "%s %s" % (
                        data.findtext('startDate').strip(),
                        data.findtext('startTime').strip()
                    ),
                    '%a, %d %b %Y %H:%M'
                )[0:6])
            )
        else:
            try:
                start_date = datetime(*(
                    time.strptime(
                        data.findtext('startDate').strip(),
                        '%a, %d %b %Y %H:%M:%S'
                    )[0:6])
                )
            except ValueError:
                try:
                    start_date = datetime(*(
                        time.strptime(
                            data.findtext('startDate').strip(),
                            '%a, %d %b %Y'
                        )[0:6])
                    )
                except ValueError:
                    pass

        latitude = data.findtext('venue/location/{%s}point/{%s}lat' % ((Location.XMLNS,)*2))
        longitude = data.findtext('venue/location/{%s}point/{%s}long' % ((Location.XMLNS,)*2))
        
        return Event(
                     api,
                     id = int(data.findtext('id')),
                     title = data.findtext('title'),
                     artists = [Artist(api, name = a.text) for a in data.findall('artists/artist')],
                     headliner = Artist(api, name = data.findtext('artists/headliner')),
                     venue = Venue(
                                   api,
                                   name = data.findtext('venue/name'),
                                   location = Location(
                                       api,
                                       city = data.findtext('venue/location/city'),
                                       country = Country(
                                            api,
                                            name = data.findtext('venue/location/country')
                                            ),
                                       street = data.findtext('venue/location/street'),
                                       postal_code = data.findtext('venue/location/postalcode'),
                                       latitude = (latitude.strip()!= '') and float(latitude) or None,
                                       longitude = (longitude.strip()!= '') and float(longitude) or None,
                                       #timezone = data.findtext('venue/location/timezone')
                                       ),
                                   url = data.findtext('venue/url')
                                   ),
                     start_date = start_date,
                     description = data.findtext('description'),
                     image = dict([(i.get('size'), i.text) for i in data.findall('image')]),
                     url = data.findtext('url'),
                     stats = Stats(
                                   subject = int(data.findtext('id')),
                                   attendance = int(data.findtext('attendance')),
                                   reviews = int(data.findtext('reviews')),
                                   ),
                     tag = data.findtext('tag')
                    )

    def _default_params(self, extra_params = None):
        if not self.id:
            raise InvalidParametersError("id has to be provided.")
        params = {'event': self.id}
        if extra_params is not None:
            params.update(extra_params)
        return params

    @staticmethod
    def _hash_func(*args, **kwds):
        try:
            return hash(kwds['id'])
        except KeyError:
            raise InvalidParametersError("id has to be provided for hashing")

    def __hash__(self):
        return Event._hash_func(id = self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __lt__(self, other):
        return self.start_date < other.start_date

    def __repr__(self):
        return "<lastfm.Event: %s at %s on %s>" % (self.title, self.venue.name, self.start_date.strftime("%x"))

from datetime import datetime
import time

from lastfm.api import Api
from lastfm.artist import Artist
from lastfm.error import InvalidParametersError
from lastfm.geo import Location, Country
from lastfm.stats import Stats
from lastfm.venue import Venue