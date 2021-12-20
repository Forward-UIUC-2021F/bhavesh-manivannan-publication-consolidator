CREATE TABLE `publication_data` (
  `id` varchar(500) NOT NULL,
  `title` varchar(500) DEFAULT NULL,
  `abstract` varchar(500) DEFAULT NULL,
  `doi` varchar(500) DEFAULT NULL,
  `citations` int(11) DEFAULT NULL,
  `authors` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `title_UNIQUE` (`title`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
