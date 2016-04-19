

CREATE TABLE `governance_object` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `parent_id` int(11) DEFAULT NULL,
  `hash` varchar(255) DEFAULT NULL,
  `parent_hash` varchar(255) DEFAULT NULL,
  `name` varchar(64) DEFAULT NULL,
  `start_time` bigint(11) DEFAULT NULL,
  `end_time` bigint(11) DEFAULT NULL,
  `priority` int(20) DEFAULT NULL,
  `type_version` int(20) DEFAULT NULL,
  `revision` int(20) DEFAULT NULL,
  `owner_address` varchar(255) DEFAULT NULL,
  `fee_tx` varchar(255) DEFAULT NULL,
  `registers` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

budget
  name
  amount
  type
  up_to_date_milestones
  voted_status

companies
  name
  from_id
  to_id
  yes_votes
  no_votes
  abstain_votes

company_contracts
  name
  from_id
  to_id
  yes_votes
  no_votes
  abstain_votes

company_employees
  name
  user_id
  from_id
  to_id

company_proposals
create
create_event
groups
group_member
users
user_member
transaction
