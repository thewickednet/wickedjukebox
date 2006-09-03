-- phpMyAdmin SQL Dump
-- version 2.8.2
-- http://www.phpmyadmin.net
-- 
-- Host: localhost
-- Generation Time: Jul 29, 2006 at 02:29 AM
-- Server version: 5.0.22
-- PHP Version: 5.1.4-pl4-gentoo
-- 
-- Database: `wickedjukebox`
-- 

-- 
-- Dumping data for table `channels`
-- 

INSERT INTO `channels` (`channel_id`, `name`, `public`, `backend`, `backend_params`) VALUES (1, 'Wicked Jukebox Soundcard 0', 1, 'mpd', 'host=localhost, port=6600, rootFolder=/mp3');

-- 
-- Dumping data for table `genres`
-- 

INSERT INTO `genres` (`genre_id`, `name`) VALUES (1, 'Rock');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (2, 'A Cappella');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (3, 'Acid');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (4, 'Acid Jazz');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (5, 'Acid Punk');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (6, 'Acoustic');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (7, 'Alt. Rock');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (8, 'Alternative');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (9, 'Ambient');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (10, 'Anime');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (11, 'Avantgarde');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (12, 'Ballad');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (13, 'Bass');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (14, 'Beat');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (15, 'Bebob');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (16, 'Big Band');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (17, 'Black Metal');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (18, 'Bluegrass');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (19, 'Blues');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (20, 'Booty Bass');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (21, 'BritPop');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (22, 'Cabaret');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (23, 'Celtic');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (24, 'Chamber Music');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (25, 'Chanson');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (26, 'Chorus');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (27, 'Christian Gangsta Rap');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (28, 'Christian Rap');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (29, 'Christian Rock');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (30, 'Classic Rock');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (31, 'Classical');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (32, 'Club');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (33, 'Club-House');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (34, 'Comedy');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (35, 'Contemporary Christian');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (36, 'Country');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (37, 'Crossover');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (38, 'Cult');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (39, 'Dance');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (40, 'Dance Hall');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (41, 'Darkwave');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (42, 'Death Metal');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (43, 'Disco');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (44, 'Dream');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (45, 'Drum & Bass');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (46, 'Drum Solo');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (47, 'Duet');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (48, 'Easy Listening');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (49, 'Electronic');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (50, 'Ethnic');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (51, 'Eurodance');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (52, 'Euro-House');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (53, 'Euro-Techno');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (54, 'Fast-Fusion');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (55, 'Folk');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (56, 'Folk/Rock');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (57, 'Folklore');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (58, 'Freestyle');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (59, 'Funk');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (60, 'Fusion');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (61, 'Game');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (62, 'Gangsta Rap');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (63, 'Goa');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (64, 'Gospel');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (65, 'Gothic');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (66, 'Gothic Rock');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (67, 'Grunge');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (68, 'Hard Rock');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (69, 'Hardcore');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (70, 'Heavy Metal');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (71, 'Hip-Hop');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (72, 'House');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (73, 'Humour');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (74, 'Indie');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (75, 'Industrial');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (76, 'Instrumental');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (77, 'Instrumental Pop');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (78, 'Instrumental Rock');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (79, 'Jazz');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (80, 'Jazz+Funk');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (81, 'JPop');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (82, 'Jungle');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (83, 'Latin');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (84, 'Lo-Fi');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (85, 'Meditative');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (86, 'Merengue');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (87, 'Metal');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (88, 'Musical');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (89, 'National Folk');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (90, 'Native American');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (91, 'Negerpunk');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (92, 'New Age');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (93, 'New Wave');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (94, 'Noise');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (95, 'Oldies');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (96, 'Opera');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (97, 'Other');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (98, 'Polka');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (99, 'Polsk Punk');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (100, 'Pop');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (101, 'Pop/Funk');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (102, 'Pop-Folk');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (103, 'Porn Groove');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (104, 'Power Ballad');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (105, 'Pranks');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (106, 'Primus');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (107, 'Progressive Rock');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (108, 'Psychedelic');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (109, 'Psychedelic Rock');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (110, 'Punk');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (111, 'Punk Rock');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (112, 'R&B');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (113, 'Rap');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (114, 'Rave');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (115, 'Reggae');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (116, 'Retro');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (117, 'Revival');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (118, 'Rhythmic Soul');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (119, 'Rock & Roll');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (120, 'Salsa');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (121, 'Samba');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (122, 'Satire');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (123, 'Showtunes');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (124, 'Ska');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (125, 'Slow Jam');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (126, 'Slow Rock');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (127, 'Sonata');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (128, 'Soul');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (129, 'Sound Clip');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (130, 'Soundtrack');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (131, 'Southern Rock');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (132, 'Space');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (133, 'Speech');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (134, 'Swing');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (135, 'Symphonic Rock');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (136, 'Symphony');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (137, 'Synthpop');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (138, 'Tango');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (139, 'Techno');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (140, 'Techno-Industrial');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (141, 'Terror');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (142, 'Thrash Metal');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (143, 'Top 40');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (144, 'Trailer');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (145, 'Trance');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (146, 'Tribal');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (147, 'Trip-Hop');
INSERT INTO `genres` (`genre_id`, `name`) VALUES (148, 'Vocal');

-- 
-- Dumping data for table `groups`
-- 

INSERT INTO `groups` (`group_id`, `title`, `admin`, `nocredits`, `queue_skip`, `queue_remove`, `queue_add`) VALUES (1, 'anonymous', 0, 0, 0, 0, 0);
INSERT INTO `groups` (`group_id`, `title`, `admin`, `nocredits`, `queue_skip`, `queue_remove`, `queue_add`) VALUES (2, 'User', 0, 0, 0, 0, 1);
INSERT INTO `groups` (`group_id`, `title`, `admin`, `nocredits`, `queue_skip`, `queue_remove`, `queue_add`) VALUES (3, 'VIP', 0, 0, 1, 1, 1);
INSERT INTO `groups` (`group_id`, `title`, `admin`, `nocredits`, `queue_skip`, `queue_remove`, `queue_add`) VALUES (4, 'DJ', 0, 1, 1, 1, 1);
INSERT INTO `groups` (`group_id`, `title`, `admin`, `nocredits`, `queue_skip`, `queue_remove`, `queue_add`) VALUES (5, 'Admin', 1, 1, 1, 1, 1);

-- 
-- Dumping data for table `players`
-- 


-- 
-- Dumping data for table `users`
-- 

INSERT INTO `users` (`user_id`, `username`, `password`, `fullname`, `added`, `credits`, `group_id`, `cookie`, `downloads`, `votes`, `skips`, `selects`) VALUES (1, 'anonymous', '', 'anonymous', '2006-07-24 17:08:34', 0, 0, '', 0, 0, 0, 0);
INSERT INTO `users` (`user_id`, `username`, `password`, `fullname`, `added`, `credits`, `group_id`, `cookie`, `downloads`, `votes`, `skips`, `selects`) VALUES (2, 'demo', 'fe01ce2a7fbac8fafaed7c982a04e229', 'demo', '2006-07-28 19:45:49', 0, 2, 'e3c82cb3efdeb7f0ca1b8291320bacdf', 0, 0, 0, 28);


-- 
-- Dumping data for table `settings`
-- 

INSERT IGNORE INTO `settings` (`param`, `value`) VALUES ('mpd_host',         'localhost');
INSERT IGNORE INTO `settings` (`param`, `value`) VALUES ('mpd_port',         '6600');
INSERT IGNORE INTO `settings` (`param`, `value`) VALUES ('player',           'mpd');
INSERT IGNORE INTO `settings` (`param`, `value`) VALUES ('recognizedTypes',  'mp3 ogg flac');
INSERT IGNORE INTO `settings` (`param`, `value`) VALUES ('daemon_boundHost', 'localhost');
INSERT IGNORE INTO `settings` (`param`, `value`) VALUES ('daemon_port',      '64000');
INSERT IGNORE INTO `settings` (`param`, `value`) VALUES ('folders',          '/mnt/mp3s/Tagged');
INSERT IGNORE INTO `settings` (`param`, `value`) VALUES ('librarian_cycle',  '1');
INSERT IGNORE INTO `settings` (`param`, `value`) VALUES ('dj_cycle',         '1');
