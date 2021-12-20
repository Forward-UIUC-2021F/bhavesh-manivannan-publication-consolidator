CREATE TABLE `author_data` (
  `id` varchar(3000) CHARACTER SET latin1 NOT NULL,
  `name` varchar(500) NOT NULL,
  `org` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
