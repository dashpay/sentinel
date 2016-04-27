
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
  `hash` varchar(255) NOT NULL DEFAULT '',
  `parent_hash` varchar(255) NOT NULL DEFAULT '',
  `time` int(11) NOT NULL DEFAULT '0',
  `name` varchar(64) NOT NULL DEFAULT '',
  `govobj_type` int(20) NOT NULL DEFAULT '0',
  `revision` int(20) NOT NULL DEFAULT '0',
  `pubkey` varchar(255) NOT NULL DEFAULT '',
  `fee_tx` varchar(255) NOT NULL DEFAULT '',
  `registers` text NOT NULL,
  `action_none_id` int(11) NOT NULL DEFAULT '0',
  `action_funding_id` int(11) NOT NULL DEFAULT '0',
  `action_valid_id` int(11) NOT NULL DEFAULT '0',
  `action_uptodate_id` int(11) NOT NULL DEFAULT '0',
  `action_delete_id` int(11) NOT NULL DEFAULT '0',
  `action_clear_registers` int(11) NOT NULL DEFAULT '0',
  `action_endorsed_id` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


/* public address, like a pobox or something */
CREATE TABLE `user` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `subclass` varchar(255) DEFAULT NULL, /* employer / employee */
  `address1` varchar(255) DEFAULT NULL,
  `address2` varchar(255) DEFAULT NULL,
  `city` varchar(255) DEFAULT NULL,
  `state` varchar(255) DEFAULT NULL,
  `country` varchar(255) DEFAULT NULL,
  `dash_monthly` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/* projects */
CREATE TABLE `project` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL, /* name of the project */
  `description` varchar(255) DEFAULT NULL,
  `bounty1` int(11) DEFAULT NULL, /* bounty 1 - dash amount */
  `bounty2` int(11) DEFAULT NULL, /* bounty 2 - dash amount */
  `bounty3` int(11) DEFAULT NULL, /* bounty 3 - dash amount */
  `assigned_party` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


/* party */
CREATE TABLE `party` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL, /* name of the project */
  `description` varchar(255) DEFAULT NULL,
  /* seven users max per party */
  `manager1` int(11) DEFAULT NULL, /* primary */
  `manager2` int(11) DEFAULT NULL, /* secondary */
  `employee1` int(11) DEFAULT NULL,
  `employee2` int(11) DEFAULT NULL,
  `employee3` int(11) DEFAULT NULL,
  `employee4` int(11) DEFAULT NULL,
  `employee5` int(11) DEFAULT NULL,
  /* salaries */
  `salary_manager1` int(11) DEFAULT NULL,
  `salary_manager2` int(11) DEFAULT NULL,
  `salary_employee1` int(11) DEFAULT NULL,
  `salary_employee2` int(11) DEFAULT NULL,
  `salary_employee3` int(11) DEFAULT NULL,
  `salary_employee4` int(11) DEFAULT NULL,
  `salary_employee5` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `expense` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `governance_object_id` int(11) DEFAULT NULL,
  `parent_id` int(11) DEFAULT NULL,
  `description` text DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `action` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `action_type` int(11) DEFAULT NULL,
  `yes_count` int(11) DEFAULT NULL,
  `no_count` int(11) DEFAULT NULL,
  `abstain_count` int(11) DEFAULT NULL,
  `none_count` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/* 
  payment types: expense, salary, bounty
*/

CREATE TABLE `payment` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `payment_type` varchar(255) DEFAULT NULL,
  `parent_id` int DEFAULT NULL,
  `start_time` datetime DEFAULT NULL,
  `amount` decimal(7, 11) DEFAULT NULL,
  `pubkey` varchar(255) DEFAULT NULL,
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
