-- phpMyAdmin SQL Dump
-- version 2.8.1
-- http://www.phpmyadmin.net
-- 
-- Host: localhost
-- Generation Time: Jul 24, 2006 at 06:03 PM
-- Server version: 5.0.21
-- PHP Version: 5.1.4
-- 
-- Database: `wickedjukebox`
-- 

-- 
-- Dumping data for table `albums`
-- 

INSERT INTO `albums` (`album_id`, `title`, `added`, `artist_id`) VALUES (1, 'With Teeth', '2006-07-24 17:06:21', 1);
INSERT INTO `albums` (`album_id`, `title`, `added`, `artist_id`) VALUES (2, 'Silent Alarm', '2006-07-24 17:06:50', 3);
INSERT INTO `albums` (`album_id`, `title`, `added`, `artist_id`) VALUES (3, 'Lateralus', '2006-07-24 17:07:03', 2);

-- 
-- Dumping data for table `artists`
-- 

INSERT INTO `artists` (`artist_id`, `name`) VALUES (1, 'Nine Inch Nails');
INSERT INTO `artists` (`artist_id`, `name`) VALUES (2, 'TOOL');
INSERT INTO `artists` (`artist_id`, `name`) VALUES (3, 'Bloc Party');

-- 
-- Dumping data for table `songs`
-- 

INSERT INTO `songs` (`song_id`, `artist_id`, `album_id`, `track_no`, `title`, `duration`, `genre_id`, `year`, `localpath`, `played`, `voted`, `skipped`, `downloaded`, `added`, `bitrate`, `filesize`, `checksum`, `lyrics`) VALUES (1, 1, 1, 1, 'All the Love in the World', '00:05:15', 1, '2005', '', 0, 0, 0, 0, '2006-07-24 17:20:30', '128kbps', 5000000, '098f6bcd4621d373cade4e832627b4f6', '');
INSERT INTO `songs` (`song_id`, `artist_id`, `album_id`, `track_no`, `title`, `duration`, `genre_id`, `year`, `localpath`, `played`, `voted`, `skipped`, `downloaded`, `added`, `bitrate`, `filesize`, `checksum`, `lyrics`) VALUES (2, 1, 1, 2, 'You Know What You Are?', '00:03:41', 1, '2005', '', 0, 0, 0, 0, '2006-07-24 17:21:48', '128kbps', 5000000, '20838a8df7cc0babd745c7af4b7d94e2', '');
INSERT INTO `songs` (`song_id`, `artist_id`, `album_id`, `track_no`, `title`, `duration`, `genre_id`, `year`, `localpath`, `played`, `voted`, `skipped`, `downloaded`, `added`, `bitrate`, `filesize`, `checksum`, `lyrics`) VALUES (3, 1, 1, 3, 'The Collector', '00:03:07', 1, '2005', '', 0, 0, 0, 0, '2006-07-24 17:22:19', '128kbps', 5000000, 'bb8e5b0c654814f8e2c13c31b9366f61', '');
INSERT INTO `songs` (`song_id`, `artist_id`, `album_id`, `track_no`, `title`, `duration`, `genre_id`, `year`, `localpath`, `played`, `voted`, `skipped`, `downloaded`, `added`, `bitrate`, `filesize`, `checksum`, `lyrics`) VALUES (4, 1, 1, 4, 'The Hand That Feeds', '00:03:31', 1, '2005', '', 0, 0, 0, 0, '2006-07-24 17:22:54', '128kbps', 5000000, '84be45a33eae5006a8464ed0d4d50a0b', '');
INSERT INTO `songs` (`song_id`, `artist_id`, `album_id`, `track_no`, `title`, `duration`, `genre_id`, `year`, `localpath`, `played`, `voted`, `skipped`, `downloaded`, `added`, `bitrate`, `filesize`, `checksum`, `lyrics`) VALUES (5, 1, 1, 5, 'Love Is Not Enough', '00:03:41', 1, '2005', '', 0, 0, 0, 0, '2006-07-24 17:25:46', '128kbps', 5000000, '98de58819edc7d63d7a3f946870f04e2', '');
INSERT INTO `songs` (`song_id`, `artist_id`, `album_id`, `track_no`, `title`, `duration`, `genre_id`, `year`, `localpath`, `played`, `voted`, `skipped`, `downloaded`, `added`, `bitrate`, `filesize`, `checksum`, `lyrics`) VALUES (6, 1, 1, 6, 'Every Day Is Exactly The Same', '00:04:54', 1, '2005', '', 0, 0, 0, 0, '2006-07-24 17:26:43', '128kbps', 5555555, '0434a4e29902e47c0838f7c8fe8c8c52', '');
INSERT INTO `songs` (`song_id`, `artist_id`, `album_id`, `track_no`, `title`, `duration`, `genre_id`, `year`, `localpath`, `played`, `voted`, `skipped`, `downloaded`, `added`, `bitrate`, `filesize`, `checksum`, `lyrics`) VALUES (7, 1, 1, 7, 'With Teeth', '00:05:37', 1, '2005', '', 0, 0, 0, 0, '2006-07-24 17:28:59', '128kbps', 5555555, 'ced141265b96c037a3cab9dee0f3b4fa', '');
INSERT INTO `songs` (`song_id`, `artist_id`, `album_id`, `track_no`, `title`, `duration`, `genre_id`, `year`, `localpath`, `played`, `voted`, `skipped`, `downloaded`, `added`, `bitrate`, `filesize`, `checksum`, `lyrics`) VALUES (8, 1, 1, 8, 'Only', '00:04:23', 1, '2005', '', 0, 0, 0, 0, '2006-07-24 17:29:26', '128kbps', 5555555, '6ca63201862b0d39ddc992eecefc1b1a', '');
INSERT INTO `songs` (`song_id`, `artist_id`, `album_id`, `track_no`, `title`, `duration`, `genre_id`, `year`, `localpath`, `played`, `voted`, `skipped`, `downloaded`, `added`, `bitrate`, `filesize`, `checksum`, `lyrics`) VALUES (9, 1, 1, 9, 'Getting Smaller', '00:03:35', 1, '2005', '', 0, 0, 0, 0, '2006-07-24 17:30:09', '128kbps', 4634732, 'c5fbd2efdc97f807326c3ce40d933bc2', '');
INSERT INTO `songs` (`song_id`, `artist_id`, `album_id`, `track_no`, `title`, `duration`, `genre_id`, `year`, `localpath`, `played`, `voted`, `skipped`, `downloaded`, `added`, `bitrate`, `filesize`, `checksum`, `lyrics`) VALUES (10, 1, 1, 10, 'Sunspots', '00:04:03', 1, '2005', '', 0, 0, 0, 0, '2006-07-24 17:30:49', '128kbps', 4637225, 'f9fdc841568361030bc5143280c3b076', '');
INSERT INTO `songs` (`song_id`, `artist_id`, `album_id`, `track_no`, `title`, `duration`, `genre_id`, `year`, `localpath`, `played`, `voted`, `skipped`, `downloaded`, `added`, `bitrate`, `filesize`, `checksum`, `lyrics`) VALUES (11, 1, 1, 11, 'The Line Begins To Blur', '00:03:44', 1, '2005', '', 0, 0, 0, 0, '2006-07-24 17:31:58', '128kbps', 75845724, '76300192b3ddd1a6f0a704176aad8a76', '');
INSERT INTO `songs` (`song_id`, `artist_id`, `album_id`, `track_no`, `title`, `duration`, `genre_id`, `year`, `localpath`, `played`, `voted`, `skipped`, `downloaded`, `added`, `bitrate`, `filesize`, `checksum`, `lyrics`) VALUES (12, 1, 1, 12, 'Beside You In Time', '00:05:24', 1, '2005', '', 0, 0, 0, 0, '2006-07-24 17:34:55', '128kbps', 43743722, 'b7f88f5c9da87f43f13cb1d74e8bc34b', '');
INSERT INTO `songs` (`song_id`, `artist_id`, `album_id`, `track_no`, `title`, `duration`, `genre_id`, `year`, `localpath`, `played`, `voted`, `skipped`, `downloaded`, `added`, `bitrate`, `filesize`, `checksum`, `lyrics`) VALUES (13, 1, 1, 13, 'Right Where It Belongs', '00:05:04', 1, '2005', '', 0, 0, 0, 0, '2006-07-24 17:57:40', '128kbps', 475452782, '1c36114885954a676d00541ea7d66e64', '');
