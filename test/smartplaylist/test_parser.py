import logging

import pytest

from wickedjukebox.smartplaylist.parser import (
    ParserSyntaxError,
    get_tokens,
    parse_query,
)


def test_plparser_short_operators():
    query = (
        '(genre = rock | genre = "Heavy Metal" or genre = Industrial) & '
        'title ~ wicked'
    )
    result = parse_query(query)
    expected = (
        "(genre.name = 'rock' OR "
        "genre.name = 'Heavy Metal' OR "
        "genre.name = 'Industrial') "
        "AND song.title LIKE 'wicked'")
    assert result == expected


def test_plparser_long_operators():
    query = ('artist is "Nine Inch Nails" or '
             'artist is "Black Sabbath" or '
             'artist is Clawfinger or '
             'album contains "Nativity in Black" '
             'or artist is Incubus')
    result = parse_query(query)
    expected = (
        "artist.name = 'Nine Inch Nails' OR "
        "artist.name = 'Black Sabbath' OR "
        "artist.name = 'Clawfinger' OR "
        "album.name LIKE 'Nativity in Black' OR "
        "artist.name = 'Incubus'"
    )
    assert result == expected


def test_plparser_invalid_character(caplog):
    caplog.set_level(logging.DEBUG)
    query = 'artist ´is "Nine Inch Nails"'
    result = parse_query(query)
    messages = [record.getMessage() for record in caplog.records]
    assert "Skipping illegal character '´'" in messages


def test_plparser_song_title():
    query = 'title is "Nine Inch Nails"'
    expected = "song.title = 'Nine Inch Nails'"
    result = parse_query(query)
    assert result == expected

def test_plparser_syntax_error():
    query = 'title is title'
    with pytest.raises(ParserSyntaxError) as exc:
        result = parse_query(query)
    exc.match('Syntax error.*title')


def test_tokenizer():
    query = 'title is "Nine Inch Nails"'
    result = [vars(token) for token in get_tokens(query)]
    for item in result:
        # The "lexer" item is an object and we don't know the exact instance at
        # time of testing. And we really only care about the other values.
        item.pop('lexer')
    expected = [
        {'lexpos': 0, 'lineno': 1, 'type': 'FIELD', 'value': 'title'},
        {'lexpos': 6, 'lineno': 1, 'type': 'EQUALS', 'value': 'is'},
        {'lexpos': 9, 'lineno': 1, 'type': 'VALUE', 'value': 'Nine Inch Nails'},
    ]
    assert result == expected
