-- phpMyAdmin SQL Dump
-- version 2.8.2
-- http://www.phpmyadmin.net
-- 
-- Host: localhost
-- Generation Time: Jul 26, 2006 at 02:08 AM
-- Server version: 5.0.22
-- PHP Version: 5.1.4-pl4-gentoo
-- 
-- Database: `wickedjukebox`
-- 

-- --------------------------------------------------------

-- 
-- Table structure for table `albums`
-- 

DROP TABLE IF EXISTS `albums`;
CREATE TABLE `albums` (
  `album_id` int(11) unsigned NOT NULL auto_increment,
  `title` varchar(128) NOT NULL,
  `added` datetime NOT NULL,
  `artist_id` int(11) unsigned NOT NULL,
  PRIMARY KEY  (`album_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=5 ;

-- --------------------------------------------------------

-- 
-- Table structure for table `artists`
-- 

DROP TABLE IF EXISTS `artists`;
CREATE TABLE `artists` (
  `artist_id` int(11) unsigned NOT NULL auto_increment,
  `name` varchar(128) NOT NULL,
  PRIMARY KEY  (`artist_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=5 ;

-- --------------------------------------------------------

-- 
-- Table structure for table `channels`
-- 

DROP TABLE IF EXISTS `channels`;
CREATE TABLE `channels` (
  `channel_id` int(11) unsigned NOT NULL auto_increment,
  `name` varchar(32) NOT NULL,
  `public` tinyint(1) unsigned NOT NULL default '1',
  `backend` varchar(32) NOT NULL,
  `backend_params` text,
  PRIMARY KEY  (`channel_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=2 ;

-- --------------------------------------------------------

-- 
-- Table structure for table `genres`
-- 

DROP TABLE IF EXISTS `genres`;
CREATE TABLE `genres` (
  `genre_id` int(11) unsigned NOT NULL auto_increment,
  `name` varchar(64) NOT NULL,
  PRIMARY KEY  (`genre_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=149 ;

-- --------------------------------------------------------

-- 
-- Table structure for table `groups`
-- 

DROP TABLE IF EXISTS `groups`;
CREATE TABLE `groups` (
  `group_id` smallint(2) unsigned NOT NULL auto_increment,
  `title` varchar(32) NOT NULL,
  `admin` tinyint(1) NOT NULL default '0',
  `nocredits` tinyint(1) NOT NULL default '0',
  `queue_skip` tinyint(1) NOT NULL default '0',
  `queue_remove` tinyint(1) NOT NULL default '0',
  `queue_add` tinyint(1) NOT NULL default '0',
  PRIMARY KEY  (`group_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=7 ;

-- --------------------------------------------------------

-- 
-- Table structure for table `playlist_song`
-- 

DROP TABLE IF EXISTS `playlist_song`;
CREATE TABLE `playlist_song` (
  `playlist_id` int(11) unsigned NOT NULL,
  `song_id` int(11) unsigned NOT NULL,
  `position` int(11) unsigned NOT NULL,
  PRIMARY KEY  (`playlist_id`,`song_id`),
  KEY `position` (`position`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

-- 
-- Table structure for table `playlists`
-- 

DROP TABLE IF EXISTS `playlists`;
CREATE TABLE `playlists` (
  `playlist_id` int(11) unsigned NOT NULL auto_increment,
  `title` varchar(64) NOT NULL,
  `user_id` int(11) NOT NULL,
  `public` tinyint(1) NOT NULL default '1',
  `added` datetime NOT NULL,
  PRIMARY KEY  (`playlist_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

-- 
-- Table structure for table `queue`
-- 

DROP TABLE IF EXISTS `queue`;
CREATE TABLE `queue` (
  `queue_id` int(11) unsigned NOT NULL auto_increment,
  `song_id` int(11) unsigned NOT NULL,
  `user_id` int(11) default NULL,
  `channel_id` int(11) unsigned NOT NULL default '1',
  `position` smallint(3) unsigned NOT NULL default '0',
  `added` datetime NOT NULL,
  PRIMARY KEY  (`queue_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=83 ;

-- --------------------------------------------------------

-- 
-- Table structure for table `settings`
-- 

DROP TABLE IF EXISTS `settings`;
CREATE TABLE `settings` (
  `param` varchar(16) NOT NULL,
  `value` text NOT NULL,
  PRIMARY KEY  (`param`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

-- 
-- Table structure for table `songs`
-- 

DROP TABLE IF EXISTS `songs`;
CREATE TABLE `songs` (
  `song_id` int(11) unsigned NOT NULL auto_increment,
  `artist_id` int(11) unsigned NOT NULL default '0',
  `album_id` int(11) unsigned NOT NULL,
  `track_no` smallint(2) NOT NULL default '0',
  `title` varchar(128) NOT NULL,
  `duration` time NOT NULL default '00:00:00',
  `genre_id` tinyint(2) unsigned NOT NULL default '0',
  `year` varchar(4) NOT NULL,
  `localpath` text NOT NULL,
  `played` int(11) unsigned NOT NULL,
  `voted` int(11) unsigned NOT NULL,
  `skipped` int(11) unsigned NOT NULL,
  `downloaded` int(11) unsigned NOT NULL,
  `added` datetime NOT NULL,
  `bitrate` varchar(8) NOT NULL,
  `filesize` int(11) unsigned NOT NULL,
  `checksum` varchar(32) NOT NULL,
  `lyrics` longtext NOT NULL,
  PRIMARY KEY  (`song_id`),
  KEY `artist_id` (`artist_id`),
  KEY `filesize` (`filesize`,`checksum`),
  KEY `title` (`title`),
  KEY `album_id` (`album_id`),
  KEY `track_no` (`track_no`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=20 ;

-- --------------------------------------------------------

-- 
-- Table structure for table `users`
-- 

DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `user_id` int(11) unsigned NOT NULL auto_increment,
  `username` varchar(32) NOT NULL,
  `password` varchar(32) NOT NULL,
  `fullname` varchar(64) NOT NULL,
  `added` datetime NOT NULL,
  `credits` mediumint(5) NOT NULL,
  `group_id` smallint(2) NOT NULL,
  PRIMARY KEY  (`user_id`),
  KEY `group_id` (`group_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=3 ;
