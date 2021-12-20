CREATE TABLE `final_publications` (
  `id` bigint(255) NOT NULL AUTO_INCREMENT,
  `timestamp` varchar(100) CHARACTER SET latin1 DEFAULT NULL,
  `title` varchar(500) NOT NULL,
  `authors` varchar(500) DEFAULT NULL,
  `abstract` varchar(3072) DEFAULT NULL,
  `knowledge_base` varchar(500) DEFAULT NULL,
  `doi` varchar(500) DEFAULT NULL,
  `citations` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `title_UNIQUE` (`title`)
) ENGINE=InnoDB AUTO_INCREMENT=412 DEFAULT CHARSET=utf8mb4;
