-- phpMyAdmin SQL Dump
-- version 2.8.0.3-Debian-1
-- http://www.phpmyadmin.net
-- 
-- Host: localhost
-- Generation Time: Jul 28, 2006 at 09:09 PM
-- Server version: 5.0.22
-- PHP Version: 5.1.2
-- 
-- Database: `wickedjukebox`
-- 

-- 
-- Dumping data for table `channels`
-- 

INSERT INTO `channels` (`channel_id`, `name`, `public`, `backend`, `backend_params`) VALUES (1, 'Wicked Jukebox Soundcard 0', 1, 'playerd', '');

-- 
-- Dumping data for table `genres`
-- 

INSERT INTO `genres` (`genre_id`, `name`) VALUES (1, 'Rock'),
(2, 'A Cappella'),
(3, 'Acid'),
(4, 'Acid Jazz'),
(5, 'Acid Punk'),
(6, 'Acoustic'),
(7, 'Alt. Rock'),
(8, 'Alternative'),
(9, 'Ambient'),
(10, 'Anime'),
(11, 'Avantgarde'),
(12, 'Ballad'),
(13, 'Bass'),
(14, 'Beat'),
(15, 'Bebob'),
(16, 'Big Band'),
(17, 'Black Metal'),
(18, 'Bluegrass'),
(19, 'Blues'),
(20, 'Booty Bass'),
(21, 'BritPop'),
(22, 'Cabaret'),
(23, 'Celtic'),
(24, 'Chamber Music'),
(25, 'Chanson'),
(26, 'Chorus'),
(27, 'Christian Gangsta Rap'),
(28, 'Christian Rap'),
(29, 'Christian Rock'),
(30, 'Classic Rock'),
(31, 'Classical'),
(32, 'Club'),
(33, 'Club-House'),
(34, 'Comedy'),
(35, 'Contemporary Christian'),
(36, 'Country'),
(37, 'Crossover'),
(38, 'Cult'),
(39, 'Dance'),
(40, 'Dance Hall'),
(41, 'Darkwave'),
(42, 'Death Metal'),
(43, 'Disco'),
(44, 'Dream'),
(45, 'Drum & Bass'),
(46, 'Drum Solo'),
(47, 'Duet'),
(48, 'Easy Listening'),
(49, 'Electronic'),
(50, 'Ethnic'),
(51, 'Eurodance'),
(52, 'Euro-House'),
(53, 'Euro-Techno'),
(54, 'Fast-Fusion'),
(55, 'Folk'),
(56, 'Folk/Rock'),
(57, 'Folklore'),
(58, 'Freestyle'),
(59, 'Funk'),
(60, 'Fusion'),
(61, 'Game'),
(62, 'Gangsta Rap'),
(63, 'Goa'),
(64, 'Gospel'),
(65, 'Gothic'),
(66, 'Gothic Rock'),
(67, 'Grunge'),
(68, 'Hard Rock'),
(69, 'Hardcore'),
(70, 'Heavy Metal'),
(71, 'Hip-Hop'),
(72, 'House'),
(73, 'Humour'),
(74, 'Indie'),
(75, 'Industrial'),
(76, 'Instrumental'),
(77, 'Instrumental Pop'),
(78, 'Instrumental Rock'),
(79, 'Jazz'),
(80, 'Jazz+Funk'),
(81, 'JPop'),
(82, 'Jungle'),
(83, 'Latin'),
(84, 'Lo-Fi'),
(85, 'Meditative'),
(86, 'Merengue'),
(87, 'Metal'),
(88, 'Musical'),
(89, 'National Folk'),
(90, 'Native American'),
(91, 'Negerpunk'),
(92, 'New Age'),
(93, 'New Wave'),
(94, 'Noise'),
(95, 'Oldies'),
(96, 'Opera'),
(97, 'Other'),
(98, 'Polka'),
(99, 'Polsk Punk'),
(100, 'Pop'),
(101, 'Pop/Funk'),
(102, 'Pop-Folk'),
(103, 'Porn Groove'),
(104, 'Power Ballad'),
(105, 'Pranks'),
(106, 'Primus'),
(107, 'Progressive Rock'),
(108, 'Psychedelic'),
(109, 'Psychedelic Rock'),
(110, 'Punk'),
(111, 'Punk Rock'),
(112, 'R&B'),
(113, 'Rap'),
(114, 'Rave'),
(115, 'Reggae'),
(116, 'Retro'),
(117, 'Revival'),
(118, 'Rhythmic Soul'),
(119, 'Rock & Roll'),
(120, 'Salsa'),
(121, 'Samba'),
(122, 'Satire'),
(123, 'Showtunes'),
(124, 'Ska'),
(125, 'Slow Jam'),
(126, 'Slow Rock'),
(127, 'Sonata'),
(128, 'Soul'),
(129, 'Sound Clip'),
(130, 'Soundtrack'),
(131, 'Southern Rock'),
(132, 'Space'),
(133, 'Speech'),
(134, 'Swing'),
(135, 'Symphonic Rock'),
(136, 'Symphony'),
(137, 'Synthpop'),
(138, 'Tango'),
(139, 'Techno'),
(140, 'Techno-Industrial'),
(141, 'Terror'),
(142, 'Thrash Metal'),
(143, 'Top 40'),
(144, 'Trailer'),
(145, 'Trance'),
(146, 'Tribal'),
(147, 'Trip-Hop'),
(148, 'Vocal');

-- 
-- Dumping data for table `groups`
-- 

INSERT INTO `groups` (`group_id`, `title`, `admin`, `nocredits`, `queue_skip`, `queue_remove`, `queue_add`) VALUES (6, 'anonymous', 0, 0, 0, 0, 0),
(2, 'user', 0, 0, 0, 0, 1),
(3, 'VIP', 0, 0, 1, 1, 1),
(4, 'DJ', 0, 1, 1, 1, 1),
(5, 'Admin', 1, 1, 1, 1, 1);

-- 
-- Dumping data for table `users`
-- 

INSERT INTO `users` (`user_id`, `username`, `password`, `fullname`, `added`, `credits`, `group_id`, `cookie`) VALUES (0, 'anonymous', 'e4e7c378bbbb381e2baa0aed560ae381', 'anonymous', '2006-07-24 17:08:34', 0, 0, ''),
(1, 'demo', '6d98684b668859ca', 'demo', '2006-07-28 19:45:49', 0, 2, '3c38ba9930ca62139a9f9689fd4149dd');
