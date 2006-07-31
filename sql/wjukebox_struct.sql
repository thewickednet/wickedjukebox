-- MySQL dump 10.10
--
-- Host: localhost    Database: wickedjukebox
-- ------------------------------------------------------
-- Server version	5.0.22-Debian_0ubuntu6.06-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `albums`
--

DROP TABLE IF EXISTS `albums`;
CREATE TABLE `albums` (
  `album_id` int(11) unsigned NOT NULL auto_increment,
  `title` varchar(128) NOT NULL,
  `added` datetime NOT NULL,
  `artist_id` int(11) unsigned NOT NULL,
  `played` int(11) unsigned NOT NULL,
  `downloaded` int(11) unsigned NOT NULL,
  `type` enum('album','various','soundtrack') NOT NULL default 'album',
  PRIMARY KEY  (`album_id`),
  KEY `artist_id` (`artist_id`),
  KEY `type` (`type`),
  KEY `title` (`title`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Table structure for table `artists`
--

DROP TABLE IF EXISTS `artists`;
CREATE TABLE `artists` (
  `artist_id` int(11) unsigned NOT NULL auto_increment,
  `name` varchar(128) NOT NULL,
  PRIMARY KEY  (`artist_id`),
  KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Table structure for table `channels`
--

DROP TABLE IF EXISTS `channels`;
CREATE TABLE `channels` (
  `channel_id` tinyint(3) unsigned NOT NULL auto_increment,
  `name` varchar(32) NOT NULL,
  `public` tinyint(1) unsigned NOT NULL default '1',
  `backend` varchar(32) NOT NULL,
  `backend_params` text,
  PRIMARY KEY  (`channel_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Table structure for table `genres`
--

DROP TABLE IF EXISTS `genres`;
CREATE TABLE `genres` (
  `genre_id` tinyint(3) unsigned NOT NULL auto_increment,
  `name` varchar(64) NOT NULL,
  PRIMARY KEY  (`genre_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Table structure for table `groups`
--

DROP TABLE IF EXISTS `groups`;
CREATE TABLE `groups` (
  `group_id` tinyint(3) unsigned NOT NULL auto_increment,
  `title` varchar(32) NOT NULL,
  `admin` tinyint(1) NOT NULL default '0',
  `nocredits` tinyint(1) NOT NULL default '0',
  `queue_skip` tinyint(1) NOT NULL default '0',
  `queue_remove` tinyint(1) NOT NULL default '0',
  `queue_add` tinyint(1) NOT NULL default '0',
  PRIMARY KEY  (`group_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Table structure for table `players`
--

DROP TABLE IF EXISTS `players`;
CREATE TABLE `players` (
  `player_id` tinyint(3) unsigned NOT NULL auto_increment,
  `channel_id` tinyint(3) unsigned NOT NULL,
  `song_id` int(11) unsigned NOT NULL,
  `status` enum('playing','stopped','paused') NOT NULL default 'stopped',
  `updated` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  PRIMARY KEY  (`player_id`),
  KEY `channel_id` (`channel_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

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

--
-- Table structure for table `playlists`
--

DROP TABLE IF EXISTS `playlists`;
CREATE TABLE `playlists` (
  `playlist_id` int(11) unsigned NOT NULL,
  `title` varchar(64) NOT NULL,
  `user_id` int(11) NOT NULL default '1',
  `public` tinyint(1) NOT NULL default '1',
  `added` datetime NOT NULL,
  PRIMARY KEY  (`playlist_id`),
  KEY `user_id` (`user_id`),
  KEY `public` (`public`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Table structure for table `queue`
--

DROP TABLE IF EXISTS `queue`;
CREATE TABLE `queue` (
  `queue_id` int(11) unsigned NOT NULL,
  `song_id` int(11) unsigned NOT NULL,
  `user_id` int(11) default NULL,
  `channel_id` smallint(5) unsigned NOT NULL default '1',
  `position` smallint(5) unsigned NOT NULL default '0',
  `added` datetime NOT NULL,
  PRIMARY KEY  (`queue_id`),
  KEY `channel_id` (`channel_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Table structure for table `settings`
--

DROP TABLE IF EXISTS `settings`;
CREATE TABLE `settings` (
  `setting_id` tinyint(3) unsigned NOT NULL,
  `param` varchar(16) NOT NULL,
  `value` text NOT NULL,
  `user_id` int(11) unsigned NOT NULL default '0',
  PRIMARY KEY  (`setting_id`),
  KEY `param` (`param`),
  KEY `user_id` (`user_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Table structure for table `songs`
--

DROP TABLE IF EXISTS `songs`;
CREATE TABLE `songs` (
  `song_id` int(11) unsigned NOT NULL,
  `artist_id` int(11) unsigned NOT NULL default '0',
  `album_id` int(11) unsigned NOT NULL,
  `track_no` tinyint(2) NOT NULL default '0',
  `title` varchar(128) NOT NULL,
  `duration` time NOT NULL default '00:00:00',
  `genre_id` tinyint(3) unsigned NOT NULL default '0',
  `year` year(4) NOT NULL,
  `localpath` varchar(255) NOT NULL,
  `played` int(11) unsigned NOT NULL,
  `voted` int(11) unsigned NOT NULL,
  `skipped` int(11) unsigned NOT NULL,
  `downloaded` int(11) unsigned NOT NULL,
  `added` datetime NOT NULL,
  `lastPlayed` datetime NOT NULL,
  `bitrate` varchar(8) NOT NULL,
  `filesize` int(11) unsigned NOT NULL,
  `checksum` varchar(32) NOT NULL,
  `lyrics` longtext NOT NULL,
  `cost` tinyint(2) NOT NULL default '5',
  PRIMARY KEY  (`song_id`),
  UNIQUE KEY `localpath` (`localpath`),
  KEY `artist_id` (`artist_id`),
  KEY `filesize` (`filesize`,`checksum`),
  KEY `title` (`title`),
  KEY `album_id` (`album_id`),
  KEY `track_no` (`track_no`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `user_id` int(11) unsigned NOT NULL,
  `username` varchar(32) NOT NULL,
  `password` varchar(32) NOT NULL,
  `fullname` varchar(64) NOT NULL,
  `added` datetime NOT NULL,
  `credits` mediumint(5) NOT NULL,
  `group_id` tinyint(3) unsigned NOT NULL,
  `cookie` varchar(32) NOT NULL,
  `downloads` int(11) unsigned NOT NULL default '0',
  `votes` int(11) unsigned NOT NULL default '0',
  `skips` int(11) unsigned NOT NULL default '0',
  `selects` int(11) unsigned NOT NULL,
  PRIMARY KEY  (`user_id`),
  KEY `group_id` (`group_id`),
  KEY `cookie` (`cookie`),
  KEY `username` (`username`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

