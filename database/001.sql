
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
  `action_funding_id` int(11) NOT NULL DEFAULT '0',
  `action_valid_id` int(11) NOT NULL DEFAULT '0',
  `action_uptodate_id` int(11) NOT NULL DEFAULT '0',
  `action_delete_id` int(11) NOT NULL DEFAULT '0',
  `action_clear_registers` int(11) NOT NULL DEFAULT '0',
  `action_endorsed_id` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `contract` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `governance_object_id` int(11) DEFAULT NULL,
  `contract_name` varchar(255) DEFAULT NULL, /* name of the contract */
  `start_date` int(11) DEFAULT NULL,
  `end_date` int(11) DEFAULT NULL,
  `payment_address` varchar(255) DEFAULT NULL,
  `payment_amount` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `event` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `governance_object_id` int(11) DEFAULT NULL,
  `start_time` int(11) NOT NULL DEFAULT '0',
  `prepare_time` int(11) NOT NULL DEFAULT '0',
  `submit_time` int(11) NOT NULL DEFAULT '0',
  `error_time` int(11) NOT NULL DEFAULT '0',
  `error_message` varchar(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  UNIQUE KEY `governance_object_id` (`governance_object_id`)
) ENGINE=InnoDB AUTO_INCREMENT=70 DEFAULT CHARSET=utf8;

CREATE TABLE `action` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `governance_object_id` int(11) DEFAULT NULL,
  `absolute_yes_count` int DEFAULT NULL,
  `yes_count` int DEFAULT NULL,
  `no_count` int DEFAULT NULL,
  `abstain_count` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `setting` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `datetime` int(11) DEFAULT '0',
  `setting` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `value` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
