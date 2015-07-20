-- MySQL dump 10.13  Distrib 5.5.23, for Linux (x86_64)
--
-- Host: localhost    Database: cloud
-- ------------------------------------------------------
-- Server version	5.5.23
--
-- Table structure for table `virtual_machine_action`
--

DROP TABLE IF EXISTS `virtual_machine_action`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `virtual_machine_action` (
  `oid` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `_username` varchar(255) DEFAULT NULL,
  `_action` varchar(255) DEFAULT NULL,
  `_vmid` varchar(255) DEFAULT NULL,
  `_finished` int(11) DEFAULT NULL,
  `_succeeded` int(11) DEFAULT NULL,
  PRIMARY KEY (`oid`)
) ;

-- Dump completed on 2012-06-08  9:56:16
