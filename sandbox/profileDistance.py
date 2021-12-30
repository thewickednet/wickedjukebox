#!/usr/bin/python
import sys
from io import StringIO

from sqlalchemy import and_, join, outerjoin, select

from wickedjukebox.demon.model import songStandingTable, songTable, usersTable


def similarity(s1, s2):
    same_rating_count = 0
    significant_length = 0
    for pos, char in enumerate(s1):
        if s2[pos] == char and char != '0':
            same_rating_count += 1
        if s2[pos] != '0' and char != '0':
            significant_length += 1
    if significant_length == 0:
        return 0
    return float(same_rating_count) / significant_length


def levenshtein_wikibooks(s1, s2):
    d_curr = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        d_prev, d_curr = d_curr, [i]
        for j, c2 in enumerate(s2):
            d_curr.append(
                min(d_prev[j] + (c1 != c2), d_prev[j + 1] + 1, d_curr[j] + 1)
            )
    return d_curr[len(s2)]


def levenshtein_distance(first, second):
    """Find the Levenshtein distance between two strings."""
    if len(first) > len(second):
        first, second = second, first
    if len(second) == 0:
        return len(first)
    first_length = len(first) + 1
    second_length = len(second) + 1
    distance_matrix = [list(range(second_length)) for x in range(first_length)]
    for i in range(1, first_length):
        for j in range(1, second_length):
            deletion = distance_matrix[i - 1][j] + 1
            insertion = distance_matrix[i][j - 1] + 1
            substitution = distance_matrix[i - 1][j - 1]
            if first[i - 1] != second[j - 1]:
                substitution += 1
            distance_matrix[i][j] = min(insertion, deletion, substitution)

    return distance_matrix[first_length - 1][second_length - 1]


def construct_string(user_id):
    """
    Construct a string representation of a users love/hate settings.
    Each character represents a standing where:
      0 = indifferent
      1 = love
      2 = hate
    """

    if not user_id:
        raise ValueError("user_id must not be None")

    user_id = int(user_id)

    buffer = StringIO()
    frobj = join(
        usersTable,
        songStandingTable,
        and_(
            usersTable.c.id == songStandingTable.c.user_id,
            usersTable.c.id == user_id,
        ),
    )

    main_join = outerjoin(songTable, frobj)

    x = select(
        [songStandingTable.c.standing + 0],
        from_obj=[main_join],
        order_by=[songTable.c.id],
    )

    for row in x.execute().fetchall():
        if row[0]:
            buffer.write("%d" % int(row[0]))
        else:
            buffer.write("0")

    buffer.flush()
    string_value = buffer.getvalue()
    buffer.close()
    return string_value


def test():
    print(2, similarity(construct_string(2), construct_string(1)))
    print(4, similarity(construct_string(4), construct_string(1)))
    print(5, similarity(construct_string(5), construct_string(1)))
    print(9, similarity(construct_string(9), construct_string(1)))
    print(12, similarity(construct_string(12), construct_string(1)))
    print(14, similarity(construct_string(14), construct_string(1)))


def usage():
    print(
        """
Usage:
   %s <user_id> <user_id>

Compute profile similarity between two users (given by user_id)
"""
        % sys.argv[0]
    )


if __name__ == "__main__":
    if len(sys.argv) < 3:
        usage()
        sys.exit(1)
    user_1 = int(sys.argv[1])
    user_2 = int(sys.argv[2])
    print(
        "Similarity between user %2d and user %2d: %3.2f%%"
        % (
            user_1,
            user_2,
            similarity(construct_string(user_1), construct_string(user_2))
            * 100,
        )
    )
