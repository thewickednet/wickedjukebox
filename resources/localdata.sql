-- phpMyAdmin SQL Dump
-- version 3.4.10.1deb1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Erstellungszeit: 31. Okt 2012 um 14:55
-- Server Version: 5.5.28
-- PHP-Version: 5.3.10-1ubuntu3.4

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

-- INSERT INTO `setting_text` (`var`, `text_en`) VALUES
-- ('channel_cycle', 'Sleep time between channel updates.'),
-- ('hates_affect_random', 'Let my hates affect the random play'),
-- ('jingles_folder', 'Folder containing jingles that are played from time to time in the stream'),
-- ('jingles_interval', 'The count of songs after which a jingle will be played. The value is either a fixed number (f.ex.: "5") meaning that after each 5 songs a jingle will be picked at random from the jingles_folder and played.\r\n\r\nOr, the value can be a "random-range" like "4-8" meaning that after at least 4, but at most 8 songs a jingle will be played.'),
-- ('lastfm_pass', 'LastFM password'),
-- ('lastfm_user', 'LastFM user name'),
-- ('loves_affect_random', 'Let my "loves" affect random play'),
-- ('max_credits', 'Maximum credits per user. Credits will automatically be restocked up to this amount.'),
-- ('max_random_duration', 'No songs longer than this duration will be queued at random'),
-- ('mediadir', 'comma separated list of folders containing audio files'),
-- ('proofoflife_timeout', 'Conencted web-users are considered "gone" after this amount of time (seconds)'),
-- ('queue_model', 'python module to use for song queuing. Module must be located in demon/playmodes'),
-- ('random_model', 'python module to use for random song selection. Module must be located in demon/playmodes'),
-- ('recognizedTypes', 'Space separated list of recognised filetypes'),
-- ('scoring_lastPlayed', 'weight of the time since song was last played in the random_weighed module\r\n\r\nmaximum score (value of this variable) is reached after 2 weeks and gradually declines the the more recent the song was played'),
-- ('scoring_neverPlayed', 'Score boost if a song was never played before for the random_weighed module.'),
-- ('scoring_randomness', 'The "random" queue score is affected by this value. With a value of "5", the score will be randomly adjusted by -5 to +5'),
-- ('scoring_songAge', 'weight of the song age (when the song was added to the db) for the random_weighed module'),
-- ('scoring_userRating', 'weight of the user rating (lova/hate)'),
-- ('shoutbox', 'activate shoutbox'),
-- ('songs_threshold', 'artist must have at least this song count to be listed in artist index'),
-- ('sys_utctime', 'Wether the system runs on UTC time or localtime. 1 = UTC-Time.\r\nYou will see the effect on your lastfm status page. If the times are wrong, this might be the cause.');


-- INSERT INTO channel  (name,backend,backend_params) VALUES ( 'wicked', 'icecast', 'port=8001, mount=/wicked.mp3, pwd=mussdulauschtren, admin_url=http://localhost:8001/admin, admin_username=admin, admin_password=matourenstepp' );


--    INSERT INTO groups (title, admin, nocredits, queue_skip, queue_remove, queue_add) VALUES ('anonymous', 0, 0, 0, 0, 0);
--    INSERT INTO groups (title, admin, nocredits, queue_skip, queue_remove, queue_add) VALUES ('User', 0, 0, 0, 0, 1);
--    INSERT INTO groups (title, admin, nocredits, queue_skip, queue_remove, queue_add) VALUES ('VIP', 0, 0, 1, 1, 1);
--    INSERT INTO groups (title, admin, nocredits, queue_skip, queue_remove, queue_add) VALUES ('DJ', 0, 1, 1, 1, 1);
--    INSERT INTO groups (title, admin, nocredits, queue_skip, queue_remove, queue_add) VALUES ('Admin', 1, 0, 1, 1, 1);

    INSERT INTO users(username,cookie,password,fullname,credits,group_id) VALUES ('exhuma','','','',30,15);

BEGIN;

    INSERT INTO `setting` (`var`, `value`, `channel_id`, `user_id`) VALUES
    ('channel_cycle', '1', 0, 0),
    ('jingles_folder', '/var/mp3/jingles', 0, 0),
    ('jingles_interval', '10', 0, 0),
    ('max_credits', '30', 0, 0),
    ('max_random_duration', '600', 0, 0),
    ('mediadir', '/var/mp3/Tagged', 0, 0),
    ('proofoflife_timeout', '120', 0, 0),
    ('queue_model', 'queue_positioned', 0, 0),
    ('random_model', 'random_wr2', 0, 0),
    ('recency_threshold', '120', 0, 0),
    ('recognizedTypes', 'mp3', 0, 0),
    ('scoring_lastPlayed', '4', 0, 0),
    ('scoring_neverPlayed', '4', 0, 0),
    ('scoring_randomness', '1', 0, 0),
    ('scoring_songAge', '0', 0, 0),
    ('scoring_userRating', '6', 0, 0),
    ('shoutbox', '1', 0, 0),
    ('songs_threshold', '2', 0, 0),
    ('sys_utctime', '1', 0, 0);

    INSERT INTO `render_presets` (`id`, `category`, `preset`, `hmax`, `wmax`, `placeholder`, `noproportion`, `force_mime`) VALUES
    (1, 'artist', 'list', 100, 150, 'artist_placeholder.png', 0, 'image/png'),
    (2, 'artist', 'detail', 250, 300, 'artist_placeholder.png', 0, 'image/png'),
    (3, 'album', 'list', 100, 100, 'album_placeholder.png', 0, 'image/png'),
    (4, 'album', 'detail', 250, 300, 'album_placeholder.png', 0, 'image/png'),
    (5, 'song', 'queue', 80, 80, 'album_placeholder.png', 0, 'image/png'),
    (6, 'song', 'player', 140, 140, 'album_placeholder.png', 0, 'image/png'),
    (7, 'user', 'profile', 140, 140, NULL, 0, 'image/png'),
    (8, 'user', 'icon', 60, 60, NULL, 0, 'image/png'),
    (9, 'user', 'favorites', 80, 80, NULL, 0, 'image/png'),
    (10, 'song', 'splash', 180, 180, 'album_placeholder.png', 0, 'image/png'),
    (11, 'album', 'latest', 160, 160, 'album_placeholder.png', 0, 'image/png'),
    (12, 'song', 'tiny', 20, 20, 'album_placeholder.png', 0, 'image/png'),
    (13, 'event', 'list', 100, 100, 'event_placeholder.jpg', 0, ''),
    (14, 'event', 'detail', 300, 300, 'event_placeholder.jpg', 0, ''),
    (15, 'artist', 'splash', 180, 180, 'artist_placeholder.png', 0, 'image/png');


COMMIT;

