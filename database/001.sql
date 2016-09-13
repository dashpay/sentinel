/*
  DATABASE TABLES

  TODO: drop a comment w/schema conventions in here
*/

DROP VIEW if exists vsuperblocks ;
DROP VIEW if exists vproposals ;

DROP TABLE if exists `votes` ;
DROP TABLE if exists `signals` ;
DROP TABLE if exists `outcomes` ;

DROP TABLE if exists `proposals` ;
DROP TABLE if exists `superblocks` ;
DROP TABLE if exists `events` ;
DROP TABLE if exists `settings` ;
DROP TABLE if exists `governance_objects` ;


CREATE TABLE `governance_objects` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `parent_id` int(10) unsigned NOT NULL DEFAULT '0',
  `object_creation_time` int(11) NOT NULL DEFAULT '0',
  `object_hash` varchar(255) NOT NULL DEFAULT '',
  `object_parent_hash` varchar(255) NOT NULL DEFAULT '0',
  `object_name` varchar(64) NOT NULL DEFAULT '',
  `object_type` int(20) NOT NULL DEFAULT '0',
  `object_revision` int(20) NOT NULL DEFAULT '1',
  `object_fee_tx` varchar(255) NOT NULL DEFAULT '',
  `yes_count` smallint(5) unsigned NOT NULL DEFAULT 0,
  `no_count` smallint(5) unsigned NOT NULL DEFAULT 0,
  `abstain_count` smallint(5) unsigned NOT NULL DEFAULT 0,
  `absolute_yes_count` smallint(6) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `proposals` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `governance_object_id` int(10) unsigned NOT NULL,
  `name` varchar(255) NOT NULL,
  `url` varchar(255) NOT NULL DEFAULT '',
  `start_epoch` int(11) NOT NULL DEFAULT 0,
  `end_epoch` int(11) NOT NULL DEFAULT 0,
  `payment_address` varchar(255) NOT NULL DEFAULT '',
  `payment_amount` decimal(16,8) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_proposals_governance_object_id` FOREIGN KEY (`governance_object_id`) REFERENCES governance_objects(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  UNIQUE KEY `index_proposals_governance_object_id` (`governance_object_id`),
  UNIQUE KEY `index_proposals_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `superblocks` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `governance_object_id` int(10) unsigned NOT NULL,
  `name` varchar(255) NOT NULL DEFAULT '',
  `event_block_height` int(10) unsigned NOT NULL,
  `payment_addresses` text,
  `payment_amounts` text,
  `sb_hash` char(64) not null default '',
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_superblocks_governance_object_id` FOREIGN KEY (`governance_object_id`) REFERENCES governance_objects(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  UNIQUE KEY `index_superblocks_governance_object_id` (`governance_object_id`),
  UNIQUE KEY `index_superblocks_sb_hash` (`sb_hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `events` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `governance_object_id` int(10) unsigned NOT NULL,
  `start_time` int(10) unsigned NOT NULL DEFAULT '0',
  `prepare_time` int(10) unsigned NOT NULL DEFAULT '0',
  `submit_time` int(10) unsigned NOT NULL DEFAULT '0',
  `error_time` int(10) unsigned NOT NULL DEFAULT '0',
  `error_message` text NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_events_governance_object_id` FOREIGN KEY (`governance_object_id`) REFERENCES governance_objects(`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `settings` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `value` text,
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `index_settings_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


-- votes

CREATE TABLE `signals` (
    `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
    `name` varchar(255) NOT NULL,
    `created_at` DATETIME NOT NULL,
    `updated_at` DATETIME NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `index_signals_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `outcomes` (
    `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
    `name` varchar(255) NOT NULL,
    `created_at` DATETIME NOT NULL,
    `updated_at` DATETIME NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `index_outcomes_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- would rather use govobj hash here... since votes must be done on hash anyway...
CREATE TABLE `votes` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `governance_object_id` int(10) unsigned NOT NULL,
  `signal_id` int(10) unsigned NOT NULL,
  `outcome_id` int(10) unsigned NOT NULL,
  `voted_at` DATETIME NOT NULL,
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_votes_governance_object_id` FOREIGN KEY (`governance_object_id`) REFERENCES governance_objects(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_votes_signal_id` FOREIGN KEY (`signal_id`) REFERENCES signals(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_votes_outcome_id` FOREIGN KEY (`outcome_id`) REFERENCES outcomes(`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


INSERT INTO signals ( name, created_at, updated_at )
VALUES ( 'funding', UTC_TIMESTAMP(), UTC_TIMESTAMP() )
     , ( 'valid', UTC_TIMESTAMP(), UTC_TIMESTAMP() )
     , ( 'delete', UTC_TIMESTAMP(), UTC_TIMESTAMP() )
     ;

INSERT INTO outcomes ( name, created_at, updated_at )
VALUES ( 'yes', UTC_TIMESTAMP(), UTC_TIMESTAMP() )
     , ( 'no', UTC_TIMESTAMP(), UTC_TIMESTAMP() )
     , ( 'abstain', UTC_TIMESTAMP(), UTC_TIMESTAMP() )
     ;

-- /votes


-- views

create view vproposals as
select p.name
     , p.url
     , p.start_epoch
     , p.end_epoch
     , p.payment_address
     , p.payment_amount
     , go.object_hash
     , go.object_fee_tx
     , go.yes_count
     , go.no_count
     , go.abstain_count
     , go.absolute_yes_count
     , go.id as `governance_object_id`
     , p.id as `proposal_id`
  from proposals p
  join governance_objects go on go.id = p.governance_object_id
;


create view vsuperblocks as
select sb.name
     , sb.event_block_height
     , sb.payment_addresses
     , sb.payment_amounts
     , go.object_hash
     , go.object_fee_tx
     , go.yes_count
     , go.no_count
     , go.abstain_count
     , go.absolute_yes_count
     , go.id as `governance_object_id`
     , sb.id as `superblock_id`
  from superblocks sb
  join governance_objects go on go.id = sb.governance_object_id
;
