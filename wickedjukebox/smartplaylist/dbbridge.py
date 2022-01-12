"""
This module contains functions to convert a "smart playlist" into database
construcsts.
"""

import logging

from sqlalchemy.orm.query import Query
from sqlalchemy.sql import select

from wickedjukebox.model.db.playback import DynamicPlaylist
from wickedjukebox.smartplaylist.parser import ParserSyntaxError, parse_query

LOG = logging.getLogger(__name__)


def parse_dynamic_playlists(query: Query) -> Query:
    """
    Apply additional filters to a query based on dynamic playlists
    """
    # TODO An issue with table-aliasing causes cartesian products.
    #      Investigate where this comes from.
    sel = select([DynamicPlaylist.query])
    sel = sel.where(DynamicPlaylist.group_id > 0)
    sel = sel.order_by("group_id")
    res = sel.execute().fetchall()
    for dpl in res:
        try:
            if parse_query(dpl["query"]):
                # TODO: prevent SQL injections (already somewhat safe due to
                # lexx/yacc parsing)
                query = query.where("(" + parse_query(dpl["query"]) + ")")
            break  # only one query will be parsed. for now.... this is a big TODO
            # as it triggers an unexpected behaviour (bug). i.e.: Why the
            # heck does it only activate one playlist?!?
        except ParserSyntaxError as ex:
            LOG.error(
                "Unable to process dynamic playlist %r",
                dpl.query,
                exc_info=True,
            )
        except Exception:  # pylint: disable=broad-except
            # catchall for graceful degradation
            LOG.exception("Unhandled exception")
    return query
