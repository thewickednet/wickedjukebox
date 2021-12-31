"""
This module contains functions to convert a "smart playlist" into database
construcsts.
"""

import logging
from typing import Generator

from sqlalchemy.sql import select

from wickedjukebox.model.db import DynamicPlaylist
from wickedjukebox.smartplaylist.parser import ParserSyntaxError, parse_query

LOG = logging.getLogger(__name__)


def parse_dynamic_playlists() -> Generator[str, None, None]:
    """
    Convert a dynamic playlist into "WHERE" clauses
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
                yield "(" + parse_query(dpl["query"]) + ")"
            break  # only one query will be parsed. for now.... this is a big TODO
            # as it triggers an unexpected behaviour (bug). i.e.: Why the
            # heck does it only activate one playlist?!?
        except ParserSyntaxError as ex:
            import traceback

            traceback.print_exc()
            LOG.error(str(ex))
            LOG.error("Query was: %s", dpl.query)
        except Exception:  # pylint: disable=broad-except
            # catchall for graceful degradation
            LOG.exception("Unhandled exception")
