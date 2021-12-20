CREATE TABLE `output_publications` (
  `id` bigint(255) NOT NULL AUTO_INCREMENT,
  `timestamp` varchar(100) DEFAULT NULL,
  `title` varchar(3000) DEFAULT NULL,
  `authors` varchar(3072) DEFAULT NULL,
  `abstract` varchar(3072) DEFAULT NULL,
  `knowledge_base` varchar(3072) DEFAULT NULL,
  `doi` varchar(3072) DEFAULT NULL,
  `citations` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=197 DEFAULT CHARSET=latin1;
