CREATE TABLE `publication_author` (
  `publication_id` varchar(1000) NOT NULL,
  `author_id` varchar(1000) NOT NULL,
  PRIMARY KEY (`publication_id`,`author_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
