
/*
  DATABASE TABLES

*/

DROP TABLE if exists `proposal` ;
DROP TABLE if exists `superblock` ;
DROP TABLE if exists `event` ;
DROP TABLE if exists `action` ;
DROP TABLE if exists `setting` ;
DROP TABLE if exists `governance_object` ;


CREATE TABLE `governance_object` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `parent_id` int(11) unsigned NOT NULL DEFAULT '0',
  `object_creation_time` int(11) NOT NULL DEFAULT '0',
  `object_hash` varchar(255) NOT NULL DEFAULT '0',
  `object_parent_hash` varchar(255) NOT NULL DEFAULT '0',
  `object_name` varchar(64) NOT NULL DEFAULT '',
  `object_type` int(20) NOT NULL DEFAULT '0',
  `object_revision` int(20) NOT NULL DEFAULT '1',
  `object_fee_tx` varchar(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  UNIQUE KEY `index_governance_object_object_name` (`object_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `proposal` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `governance_object_id` int(11) unsigned NOT NULL,
  `proposal_name` varchar(255) NOT NULL,
  `start_epoch` int(11) DEFAULT NULL,
  `end_epoch` int(11) DEFAULT NULL,
  `payment_address` varchar(255) DEFAULT NULL,
  `payment_amount` decimal(16,8) DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_proposal_governance_object_id` FOREIGN KEY (`governance_object_id`) REFERENCES governance_object(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  UNIQUE KEY `index_proposal_proposal_name` (`proposal_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE superblock (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `governance_object_id` int(11) unsigned NOT NULL,
  `superblock_name` varchar(255) DEFAULT NULL,
  `event_block_height` int(11) DEFAULT NULL,
  `payment_addresses` text,
  `payment_amounts` text,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_superblock_governance_object_id` FOREIGN KEY (`governance_object_id`) REFERENCES governance_object(`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `event` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `governance_object_id` int(11) unsigned NOT NULL,
  `start_time` int(11) NOT NULL DEFAULT '0',
  `prepare_time` int(11) NOT NULL DEFAULT '0',
  `submit_time` int(11) NOT NULL DEFAULT '0',
  `error_time` int(11) NOT NULL DEFAULT '0',
  `error_message` varchar(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_event_governance_object_id` FOREIGN KEY (`governance_object_id`) REFERENCES governance_object(`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



CREATE TABLE `action` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `governance_object_id` int(11) unsigned NOT NULL,
  `absolute_yes_count` int DEFAULT NULL,
  `yes_count` int DEFAULT NULL,
  `no_count` int DEFAULT NULL,
  `abstain_count` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_action_governance_object_id` FOREIGN KEY (`governance_object_id`) REFERENCES governance_object(`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `setting` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `value` text,
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `index_setting_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
