
/*
TODO: http://www.endswithsaurus.com/2009/07/lesson-in-address-storage.html


Street Number [Int]
Street Number Suffix [VarChar] - A~Z 1/3 1/2 2/3 3/4 etc
Street Name [VarChar]
Street Type [VarChar] - Street, Road, Place etc. (I've found 262 unique street types in the English speaking world so far... and still finding them)
Street Direction [VarChar] - N, NE, E, SE, S, SW, W, NW
Address Type [VarChar] - For example Apartment, Suite, Office, Floor, Building etc.
Address Type Identifier [VarChar] - For instance the apartment number, suite, office or floor number or building identifier.
Minor Municipality (Village/Hamlet) [VarChar]
Major Municipality (Town/City) [VarChar]
Governing District (Province, State, County) [VarChar]
Postal Area (Postal Code/Zip/Postcode)[VarChar]
Country [VarChar]

*/


CREATE TABLE `governance_object` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `parent_id` int(11) NOT NULL DEFAULT '0',
  `object_creation_time` int(11) NOT NULL DEFAULT '0',
  `object_hash` varchar(255) NOT NULL DEFAULT '',
  `object_parent_hash` varchar(255) NOT NULL DEFAULT '',
  `object_name` varchar(64) NOT NULL DEFAULT '',
  `object_type` int(20) NOT NULL DEFAULT '0',
  `object_revision` int(20) NOT NULL DEFAULT '0',
  `object_pubkey` varchar(255) NOT NULL DEFAULT '',
  `object_data` text NOT NULL,
  `object_fee_tx` varchar(255) NOT NULL DEFAULT '',
  `action_none_id` int(11) NOT NULL DEFAULT '0',
  `action_funding_id` int(11) NOT NULL DEFAULT '0',
  `action_valid_id` int(11) NOT NULL DEFAULT '0',
  `action_uptodate_id` int(11) NOT NULL DEFAULT '0',
  `action_delete_id` int(11) NOT NULL DEFAULT '0',
  `action_clear_registers` int(11) NOT NULL DEFAULT '0',
  `action_endorsed_id` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `user` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `subclass` varchar(255) DEFAULT NULL, /* employer / employee */
  `username` varchar(255) DEFAULT NULL,
  `managed_by` varchar(255) DEFAULT NULL,
  `project` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `payday` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `date` date DEFAULT NULL,
  `income` varchar(255) DEFAULT NULL,
  `expense` varchar(255) DEFAULT NULL,
  `signature_one` varchar(255) DEFAULT NULL,
  `signature_two` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `project` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL, /* name of the project */
  `description` varchar(255) DEFAULT NULL,
  `subclass` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `report` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` int(11) DEFAULT NULL,
  `url` int(11) DEFAULT NULL,
  `description` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `event` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `governance_object_id` int(11) DEFAULT NULL,
  `start_time` datetime DEFAULT NULL,
  `prepare_time` datetime DEFAULT NULL,
  `submit_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `setting` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `datetime` datetime DEFAULT NULL,
  `setting` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `value` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
