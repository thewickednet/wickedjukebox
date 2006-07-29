-- phpMyAdmin SQL Dump
-- version 2.8.2
-- http://www.phpmyadmin.net
-- 
-- Host: localhost
-- Generation Time: Jul 29, 2006 at 02:28 AM
-- Server version: 5.0.22
-- PHP Version: 5.1.4-pl4-gentoo
-- 
-- Database: `wickedjukebox`
-- 

-- --------------------------------------------------------

-- 
-- Table structure for table `albums`
-- 

CREATE TABLE `albums` (
  `album_id` int(11) unsigned NOT NULL,
  `title` varchar(128) NOT NULL,
  `added` datetime NOT NULL,
  `artist_id` int(11) unsigned NOT NULL,
  `played` int(11) unsigned NOT NULL,
  `downloaded` int(11) unsigned NOT NULL,
  `type` enum('album','various','soundtrack') NOT NULL default 'album',
  PRIMARY KEY  (`album_id`)
) TYPE=MyISAM AUTO_INCREMENT=5 ;

-- --------------------------------------------------------

-- 
-- Table structure for table `artists`
-- 

CREATE TABLE `artists` (
  `artist_id` int(11) unsigned NOT NULL,
  `name` varchar(128) NOT NULL,
  PRIMARY KEY  (`artist_id`)
) TYPE=MyISAM AUTO_INCREMENT=5 ;

-- --------------------------------------------------------

-- 
-- Table structure for table `channels`
-- 

CREATE TABLE `channels` (
  `channel_id` int(11) unsigned NOT NULL,
  `name` varchar(32) NOT NULL,
  `public` tinyint(1) unsigned NOT NULL default '1',
  `backend` varchar(32) NOT NULL,
  `backend_params` text,
  PRIMARY KEY  (`channel_id`)
) TYPE=MyISAM AUTO_INCREMENT=2 ;

-- --------------------------------------------------------

-- 
-- Table structure for table `genres`
-- 

CREATE TABLE `genres` (
  `genre_id` int(11) unsigned NOT NULL,
  `name` varchar(64) NOT NULL,
  PRIMARY KEY  (`genre_id`)
) TYPE=MyISAM AUTO_INCREMENT=149 ;

-- --------------------------------------------------------

-- 
-- Table structure for table `groups`
-- 

CREATE TABLE `groups` (
  `group_id` smallint(2) unsigned NOT NULL,
  `title` varchar(32) NOT NULL,
  `admin` tinyint(1) NOT NULL default '0',
  `nocredits` tinyint(1) NOT NULL default '0',
  `queue_skip` tinyint(1) NOT NULL default '0',
  `queue_remove` tinyint(1) NOT NULL default '0',
  `queue_add` tinyint(1) NOT NULL default '0',
  PRIMARY KEY  (`group_id`)
) TYPE=MyISAM AUTO_INCREMENT=7 ;

-- --------------------------------------------------------

-- 
-- Table structure for table `players`
-- 

CREATE TABLE `players` (
  `player_id` int(11) unsigned NOT NULL,
  `channel_id` int(11) unsigned NOT NULL,
  `song_id` int(11) unsigned NOT NULL,
  `status` enum('playing','stopped','paused') NOT NULL default 'stopped',
  `updated` timestamp NOT NULL,
  PRIMARY KEY  (`player_id`),
  KEY `channel_id` (`channel_id`)
) TYPE=MyISAM AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

-- 
-- Table structure for table `playlist_song`
-- 

CREATE TABLE `playlist_song` (
  `playlist_id` int(11) unsigned NOT NULL,
  `song_id` int(11) unsigned NOT NULL,
  `position` int(11) unsigned NOT NULL,
  PRIMARY KEY  (`playlist_id`,`song_id`),
  KEY `position` (`position`)
) TYPE=MyISAM AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

-- 
-- Table structure for table `playlists`
-- 

CREATE TABLE `playlists` (
  `playlist_id` int(11) unsigned NOT NULL,
  `title` varchar(64) NOT NULL,
  `user_id` int(11) NOT NULL default '1',
  `public` tinyint(1) NOT NULL default '1',
  `added` datetime NOT NULL,
  PRIMARY KEY  (`playlist_id`)
) TYPE=MyISAM AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

-- 
-- Table structure for table `queue`
-- 

CREATE TABLE `queue` (
  `queue_id` int(11) unsigned NOT NULL,
  `song_id` int(11) unsigned NOT NULL,
  `user_id` int(11) default NULL,
  `channel_id` int(11) unsigned NOT NULL default '1',
  `position` smallint(3) unsigned NOT NULL default '0',
  `added` datetime NOT NULL,
  PRIMARY KEY  (`queue_id`)
) TYPE=MyISAM AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

-- 
-- Table structure for table `settings`
-- 

CREATE TABLE `settings` (
  `setting_id` mediumint(3) unsigned NOT NULL,
  `param` varchar(16) NOT NULL,
  `value` text NOT NULL,
  `user_id` int(11) unsigned NOT NULL default '0',
  PRIMARY KEY  (`setting_id`)
) TYPE=MyISAM AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

-- 
-- Table structure for table `songs`
-- 

CREATE TABLE `songs` (
  `song_id` int(11) unsigned NOT NULL,
  `artist_id` int(11) unsigned NOT NULL default '0',
  `album_id` int(11) unsigned NOT NULL,
  `track_no` smallint(2) NOT NULL default '0',
  `title` varchar(128) NOT NULL,
  `duration` time NOT NULL default '00:00:00',
  `genre_id` tinyint(2) unsigned NOT NULL default '0',
  `year` varchar(4) NOT NULL,
  `localpath` varchar(255) NOT NULL,
  `played` int(11) unsigned NOT NULL,
  `voted` int(11) unsigned NOT NULL,
  `skipped` int(11) unsigned NOT NULL,
  `downloaded` int(11) unsigned NOT NULL,
  `added` datetime NOT NULL,
  `bitrate` varchar(8) NOT NULL,
  `filesize` int(11) unsigned NOT NULL,
  `checksum` varchar(32) NOT NULL,
  `lyrics` longtext NOT NULL,
  `cost` smallint(2) NOT NULL default '5',
  PRIMARY KEY  (`song_id`),
  UNIQUE KEY `localpath` (`localpath`),
  KEY `artist_id` (`artist_id`),
  KEY `filesize` (`filesize`,`checksum`),
  KEY `title` (`title`),
  KEY `album_id` (`album_id`),
  KEY `track_no` (`track_no`)
) TYPE=MyISAM AUTO_INCREMENT=20 ;

-- --------------------------------------------------------

-- 
-- Table structure for table `users`
-- 

CREATE TABLE `users` (
  `user_id` int(11) unsigned NOT NULL,
  `username` varchar(32) NOT NULL,
  `password` varchar(32) NOT NULL,
  `fullname` varchar(64) NOT NULL,
  `added` datetime NOT NULL,
  `credits` mediumint(5) NOT NULL,
  `group_id` smallint(2) NOT NULL,
  `cookie` varchar(32) NOT NULL,
  `downloads` int(11) unsigned NOT NULL default '0',
  `votes` int(11) unsigned NOT NULL default '0',
  `skips` int(11) unsigned NOT NULL default '0',
  `selects` int(11) unsigned NOT NULL,
  PRIMARY KEY  (`user_id`),
  KEY `group_id` (`group_id`),
  KEY `cookie` (`cookie`)
) TYPE=MyISAM AUTO_INCREMENT=3 ;
