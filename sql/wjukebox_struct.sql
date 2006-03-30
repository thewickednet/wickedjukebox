-- phpMyAdmin SQL Dump
-- version 2.6.4-pl2
-- http://www.phpmyadmin.net
-- 
-- Host: localhost
-- Generation Time: Mar 31, 2006 at 01:27 AM
-- Server version: 5.0.19
-- PHP Version: 5.1.2-gentoo
-- 
-- Database: `wjukebox`
-- 

-- --------------------------------------------------------

-- 
-- Table structure for table `album_song`
-- 

CREATE TABLE `album_song` (
  `album_id` int(11) unsigned NOT NULL,
  `song_id` int(11) unsigned NOT NULL,
  `track` smallint(3) unsigned NOT NULL,
  PRIMARY KEY  (`album_id`,`song_id`),
  KEY `track` (`track`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

-- 
-- Table structure for table `albums`
-- 

CREATE TABLE `albums` (
  `album_id` int(11) unsigned NOT NULL auto_increment,
  `title` varchar(128) NOT NULL,
  `added` datetime NOT NULL,
  `artist_id` int(11) unsigned NOT NULL,
  PRIMARY KEY  (`album_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

-- 
-- Table structure for table `artists`
-- 

CREATE TABLE `artists` (
  `artist_id` int(11) unsigned NOT NULL auto_increment,
  `name` varchar(128) NOT NULL,
  PRIMARY KEY  (`artist_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

-- 
-- Table structure for table `channels`
-- 

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
-- Table structure for table `playlist_song`
-- 

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

CREATE TABLE `playlists` (
  `playlist_id` int(11) unsigned NOT NULL,
  `title` varchar(64) NOT NULL,
  `user_id` int(11) NOT NULL,
  `public` tinyint(1) NOT NULL default '1',
  `added` datetime NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

-- 
-- Table structure for table `queue`
-- 

CREATE TABLE `queue` (
  `queue_id` int(11) unsigned NOT NULL,
  `song_id` int(11) unsigned NOT NULL,
  `playlist_id` int(11) unsigned default NULL,
  `user_id` int(11) default NULL,
  `channel_id` int(11) unsigned NOT NULL default '1',
  `position` smallint(3) unsigned NOT NULL default '0',
  `added` datetime NOT NULL,
  PRIMARY KEY  (`queue_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

-- 
-- Table structure for table `settings`
-- 

CREATE TABLE `settings` (
  `param` varchar(16) NOT NULL,
  `value` varchar(64) NOT NULL,
  PRIMARY KEY  (`param`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

-- 
-- Table structure for table `songs`
-- 

CREATE TABLE `songs` (
  `song_id` int(11) unsigned NOT NULL auto_increment,
  `artist_id` int(11) unsigned NOT NULL default '0',
  `title` varchar(128) NOT NULL,
  `duration` smallint(3) NOT NULL default '0',
  `genre_id` tinyint(2) unsigned NOT NULL default '0',
  `year` varchar(4) NOT NULL,
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
  KEY `filesize` (`filesize`,`checksum`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

-- 
-- Table structure for table `users`
-- 

CREATE TABLE `users` (
  `user_id` int(11) unsigned NOT NULL,
  `username` varchar(32) NOT NULL,
  `password` varchar(32) NOT NULL,
  `fullname` varchar(64) NOT NULL,
  `added` datetime NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
