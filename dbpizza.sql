/*
Navicat MySQL Data Transfer

Source Server         : 10.127.64.248
Source Server Version : 50515
Source Host           : 10.127.64.248:3306
Source Database       : dbpizza

Target Server Type    : MYSQL
Target Server Version : 50515
File Encoding         : 65001

Date: 2013-12-10 15:27:19
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `auth_group`
-- ----------------------------
DROP TABLE IF EXISTS `auth_group`;
CREATE TABLE `auth_group` (
`id`  int(11) NOT NULL AUTO_INCREMENT ,
`name`  varchar(80) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL ,
PRIMARY KEY (`id`),
UNIQUE INDEX `name` (`name`) USING BTREE 
)
ENGINE=InnoDB
DEFAULT CHARACTER SET=latin1 COLLATE=latin1_swedish_ci
AUTO_INCREMENT=1

;

-- ----------------------------
-- Table structure for `auth_group_permissions`
-- ----------------------------
DROP TABLE IF EXISTS `auth_group_permissions`;
CREATE TABLE `auth_group_permissions` (
`id`  int(11) NOT NULL AUTO_INCREMENT ,
`group_id`  int(11) NOT NULL ,
`permission_id`  int(11) NOT NULL ,
PRIMARY KEY (`id`),
UNIQUE INDEX `group_id` (`group_id`, `permission_id`) USING BTREE 
)
ENGINE=InnoDB
DEFAULT CHARACTER SET=latin1 COLLATE=latin1_swedish_ci
AUTO_INCREMENT=1

;

-- ----------------------------
-- Table structure for `auth_permission`
-- ----------------------------
DROP TABLE IF EXISTS `auth_permission`;
CREATE TABLE `auth_permission` (
`id`  int(11) NOT NULL AUTO_INCREMENT ,
`name`  varchar(50) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL ,
`content_type_id`  int(11) NOT NULL ,
`codename`  varchar(100) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL ,
PRIMARY KEY (`id`),
UNIQUE INDEX `content_type_id` (`content_type_id`, `codename`) USING BTREE 
)
ENGINE=InnoDB
DEFAULT CHARACTER SET=latin1 COLLATE=latin1_swedish_ci
AUTO_INCREMENT=25

;

-- ----------------------------
-- Table structure for `auth_user`
-- ----------------------------
DROP TABLE IF EXISTS `auth_user`;
CREATE TABLE `auth_user` (
`id`  int(11) NOT NULL AUTO_INCREMENT ,
`password`  varchar(128) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL ,
`last_login`  datetime NOT NULL ,
`is_superuser`  tinyint(1) NOT NULL ,
`username`  varchar(30) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL ,
`first_name`  varchar(30) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL ,
`last_name`  varchar(30) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL ,
`email`  varchar(75) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL ,
`is_staff`  tinyint(1) NOT NULL ,
`is_active`  tinyint(1) NOT NULL ,
`date_joined`  datetime NOT NULL ,
PRIMARY KEY (`id`),
UNIQUE INDEX `username` (`username`) USING BTREE 
)
ENGINE=InnoDB
DEFAULT CHARACTER SET=latin1 COLLATE=latin1_swedish_ci
AUTO_INCREMENT=3

;

-- ----------------------------
-- Table structure for `auth_user_groups`
-- ----------------------------
DROP TABLE IF EXISTS `auth_user_groups`;
CREATE TABLE `auth_user_groups` (
`id`  int(11) NOT NULL AUTO_INCREMENT ,
`user_id`  int(11) NOT NULL ,
`group_id`  int(11) NOT NULL ,
PRIMARY KEY (`id`),
FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
UNIQUE INDEX `user_id` (`user_id`, `group_id`) USING BTREE ,
INDEX `group_id_refs_id_274b862c` (`group_id`) USING BTREE 
)
ENGINE=InnoDB
DEFAULT CHARACTER SET=latin1 COLLATE=latin1_swedish_ci
AUTO_INCREMENT=1

;

-- ----------------------------
-- Table structure for `auth_user_user_permissions`
-- ----------------------------
DROP TABLE IF EXISTS `auth_user_user_permissions`;
CREATE TABLE `auth_user_user_permissions` (
`id`  int(11) NOT NULL AUTO_INCREMENT ,
`user_id`  int(11) NOT NULL ,
`permission_id`  int(11) NOT NULL ,
PRIMARY KEY (`id`),
FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
UNIQUE INDEX `user_id` (`user_id`, `permission_id`) USING BTREE ,
INDEX `permission_id_refs_id_35d9ac25` (`permission_id`) USING BTREE 
)
ENGINE=InnoDB
DEFAULT CHARACTER SET=latin1 COLLATE=latin1_swedish_ci
AUTO_INCREMENT=4

;

-- ----------------------------
-- Table structure for `check_server_list`
-- ----------------------------
DROP TABLE IF EXISTS `check_server_list`;
CREATE TABLE `check_server_list` (
`id`  int(11) NOT NULL AUTO_INCREMENT ,
`pid`  int(11) NULL DEFAULT NULL COMMENT '依赖ID' ,
`need_pvalue`  varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`check_name`  varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`check_command`  varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`filter_command`  varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`fix_command`  varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`result_table`  varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '指定信息存储表名' ,
`result_field`  varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '指定信息存储表的字段名' ,
PRIMARY KEY (`id`)
)
ENGINE=InnoDB
DEFAULT CHARACTER SET=utf8 COLLATE=utf8_general_ci
AUTO_INCREMENT=39

;

-- ----------------------------
-- Table structure for `checklist_entry`
-- ----------------------------
DROP TABLE IF EXISTS `checklist_entry`;
CREATE TABLE `checklist_entry` (
`id`  int(11) UNSIGNED NOT NULL AUTO_INCREMENT ,
`target`  varchar(50) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT '¼ì²é¶ÔÏó' ,
`item`  varchar(200) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT '¼ì²éÏî' ,
`mothed`  varchar(200) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT '¼ì²é·½·¨' ,
`require`  varchar(200) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT 'Í¨¹ýÌõ¼þ' ,
PRIMARY KEY (`id`)
)
ENGINE=InnoDB
DEFAULT CHARACTER SET=latin1 COLLATE=latin1_swedish_ci
AUTO_INCREMENT=1

;

-- ----------------------------
-- Table structure for `checklist_event`
-- ----------------------------
DROP TABLE IF EXISTS `checklist_event`;
CREATE TABLE `checklist_event` (
`id`  int(11) UNSIGNED NOT NULL AUTO_INCREMENT ,
`job_id`  varchar(50) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL COMMENT 'ÒµÎñ²Ù×÷' ,
`checkorder`  int(11) NOT NULL COMMENT '¼ì²éÐòÁÐ' ,
`entry_id`  int(11) NOT NULL ,
PRIMARY KEY (`id`)
)
ENGINE=InnoDB
DEFAULT CHARACTER SET=latin1 COLLATE=latin1_swedish_ci
AUTO_INCREMENT=1

;

-- ----------------------------
-- Table structure for `checklist_event_history`
-- ----------------------------
DROP TABLE IF EXISTS `checklist_event_history`;
CREATE TABLE `checklist_event_history` (
`id`  int(11) UNSIGNED NOT NULL AUTO_INCREMENT ,
PRIMARY KEY (`id`)
)
ENGINE=InnoDB
DEFAULT CHARACTER SET=latin1 COLLATE=latin1_swedish_ci
AUTO_INCREMENT=1

;

-- ----------------------------
-- Table structure for `checklist_job`
-- ----------------------------
DROP TABLE IF EXISTS `checklist_job`;
CREATE TABLE `checklist_job` (
`id`  int(11) UNSIGNED NOT NULL AUTO_INCREMENT ,
`name`  varchar(50) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT 'ÒµÎñ²Ù×÷' ,
PRIMARY KEY (`id`)
)
ENGINE=InnoDB
DEFAULT CHARACTER SET=latin1 COLLATE=latin1_swedish_ci
AUTO_INCREMENT=1

;

-- ----------------------------
-- Table structure for `checklist_job_history`
-- ----------------------------
DROP TABLE IF EXISTS `checklist_job_history`;
CREATE TABLE `checklist_job_history` (
`id`  int(11) UNSIGNED NOT NULL AUTO_INCREMENT ,
PRIMARY KEY (`id`)
)
ENGINE=InnoDB
DEFAULT CHARACTER SET=latin1 COLLATE=latin1_swedish_ci
AUTO_INCREMENT=1

;

-- ----------------------------
-- Table structure for `db_schemas`
-- ----------------------------
DROP TABLE IF EXISTS `db_schemas`;
CREATE TABLE `db_schemas` (
`id`  int(10) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '×ÔÔöID' ,
`update_time`  timestamp NOT NULL DEFAULT '0000-00-00 00:00:00' ON UPDATE CURRENT_TIMESTAMP COMMENT 'ÐÞ¸ÄÊ±¼ä' ,
`create_time`  timestamp NOT NULL DEFAULT '0000-00-00 00:00:00' COMMENT '´´½¨Ê±¼ä' ,
`is_deleted`  tinyint(1) NULL DEFAULT 0 COMMENT 'É¾³ý±ê¼Ç' ,
`server_id`  int(10) UNSIGNED NOT NULL COMMENT 'ËùÊô·þÎñÆ÷ID' ,
`instance_port`  smallint(5) UNSIGNED NULL DEFAULT NULL COMMENT 'ËùÊôÊµÀý¶Ë¿ÚºÅ' ,
`schema_name`  varchar(50) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT 'schemaÃû' ,
`schema_role`  enum('usercenter','gamecenter','recharge','stat','log','sns','gmdb','gamedb') CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT 'schema½ÇÉ«' ,
`schema_desc`  varchar(250) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT '¹¦ÄÜÃèÊö' ,
`gamedb_group`  varchar(50) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT 'ÓÎÏ·DB×éºÅ' ,
`all_db_users`  varchar(250) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT '·ÃÎÊÁÐ±í' ,
`is_gamedb`  tinyint(1) NULL DEFAULT 1 COMMENT 'ÊÇ·ñÓÎÏ·DB' ,
`is_slave`  tinyint(1) NULL DEFAULT 0 COMMENT 'ÊÇ·ñÎªslave' ,
`is_online`  tinyint(1) NULL DEFAULT 1 COMMENT 'ÊÇ·ñÏßÉÏ' ,
`nation`  enum('hk','vn','id','in','tw','th','us','my') CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT 'µØÇø' ,
`product`  enum('tlbb','ldj','taoyuan','guyu','totem','specialforce','gamefuse','oppaplay','gamiction','cuaban','davinci','swordgirls','common') CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT '²úÆ·' ,
PRIMARY KEY (`id`)
)
ENGINE=InnoDB
DEFAULT CHARACTER SET=latin1 COLLATE=latin1_swedish_ci
AUTO_INCREMENT=1

;

-- ----------------------------
-- Table structure for `django_admin_log`
-- ----------------------------
DROP TABLE IF EXISTS `django_admin_log`;
CREATE TABLE `django_admin_log` (
`id`  int(11) NOT NULL AUTO_INCREMENT ,
`action_time`  datetime NOT NULL ,
`user_id`  int(11) NOT NULL ,
`content_type_id`  int(11) NULL DEFAULT NULL ,
`object_id`  longtext CHARACTER SET utf8 COLLATE utf8_general_ci NULL ,
`object_repr`  varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
`action_flag`  smallint(5) UNSIGNED NOT NULL ,
`change_message`  longtext CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
PRIMARY KEY (`id`),
FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
INDEX `django_admin_log_6340c63c` (`user_id`) USING BTREE ,
INDEX `django_admin_log_37ef4eb4` (`content_type_id`) USING BTREE 
)
ENGINE=InnoDB
DEFAULT CHARACTER SET=utf8 COLLATE=utf8_general_ci
AUTO_INCREMENT=369

;

-- ----------------------------
-- Table structure for `django_content_type`
-- ----------------------------
DROP TABLE IF EXISTS `django_content_type`;
CREATE TABLE `django_content_type` (
`id`  int(11) NOT NULL AUTO_INCREMENT ,
`name`  varchar(100) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL ,
`app_label`  varchar(100) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL ,
`model`  varchar(100) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL ,
PRIMARY KEY (`id`),
UNIQUE INDEX `app_label` (`app_label`, `model`) USING BTREE 
)
ENGINE=InnoDB
DEFAULT CHARACTER SET=latin1 COLLATE=latin1_swedish_ci
AUTO_INCREMENT=9

;

-- ----------------------------
-- Table structure for `django_session`
-- ----------------------------
DROP TABLE IF EXISTS `django_session`;
CREATE TABLE `django_session` (
`session_key`  varchar(40) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL ,
`session_data`  longtext CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL ,
`expire_date`  datetime NOT NULL ,
PRIMARY KEY (`session_key`)
)
ENGINE=InnoDB
DEFAULT CHARACTER SET=latin1 COLLATE=latin1_swedish_ci

;

-- ----------------------------
-- Table structure for `django_site`
-- ----------------------------
DROP TABLE IF EXISTS `django_site`;
CREATE TABLE `django_site` (
`id`  int(11) NOT NULL AUTO_INCREMENT ,
`domain`  varchar(100) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL ,
`name`  varchar(50) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL ,
PRIMARY KEY (`id`)
)
ENGINE=InnoDB
DEFAULT CHARACTER SET=latin1 COLLATE=latin1_swedish_ci
AUTO_INCREMENT=2

;

-- ----------------------------
-- Table structure for `t_backup_info`
-- ----------------------------
DROP TABLE IF EXISTS `t_backup_info`;
CREATE TABLE `t_backup_info` (
`ID`  bigint(10) NOT NULL AUTO_INCREMENT ,
`locale`  varchar(5) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`product`  varchar(15) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`db_type`  varchar(5) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`backup_type1`  varchar(5) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`backup_type2`  varchar(5) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`save_time`  int(4) NULL DEFAULT NULL ,
`ip`  varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`status`  char(8) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`people`  varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`zone`  varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`port`  int(6) NULL DEFAULT NULL ,
`db_name`  varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`bak_type`  char(5) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`character_set`  char(6) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
PRIMARY KEY (`ID`)
)
ENGINE=InnoDB
DEFAULT CHARACTER SET=utf8 COLLATE=utf8_general_ci
AUTO_INCREMENT=2294

;

-- ----------------------------
-- Table structure for `t_backup_server`
-- ----------------------------
DROP TABLE IF EXISTS `t_backup_server`;
CREATE TABLE `t_backup_server` (
`ID`  bigint(10) NOT NULL AUTO_INCREMENT ,
`locale`  varchar(5) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`product`  varchar(5) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`IP`  varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`db_type`  varchar(5) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`backup_type1`  varchar(5) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`backup_type2`  varchar(5) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`save_time`  int(4) NULL DEFAULT NULL ,
`people`  varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
PRIMARY KEY (`ID`)
)
ENGINE=InnoDB
DEFAULT CHARACTER SET=utf8 COLLATE=utf8_general_ci
AUTO_INCREMENT=1

;

-- ----------------------------
-- Table structure for `t_crontab`
-- ----------------------------
DROP TABLE IF EXISTS `t_crontab`;
CREATE TABLE `t_crontab` (
`id`  int(11) UNSIGNED NOT NULL AUTO_INCREMENT ,
`server_id`  int(11) UNSIGNED NULL DEFAULT NULL ,
`pminute`  varchar(20) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL ,
`phour`  varchar(20) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL ,
`pday`  varchar(20) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL ,
`pmonth`  varchar(20) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL ,
`pweek`  varchar(20) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL ,
`process`  varchar(400) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL ,
`status`  int(5) NULL DEFAULT NULL COMMENT '1 run 0 not use' ,
`user`  varchar(20) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL ,
`group`  varchar(20) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL ,
`operator`  varchar(30) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL ,
`description`  varchar(100) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL ,
`create_time`  timestamp NULL DEFAULT NULL ,
`update_time`  timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP ,
PRIMARY KEY (`id`)
)
ENGINE=InnoDB
DEFAULT CHARACTER SET=latin1 COLLATE=latin1_swedish_ci
AUTO_INCREMENT=1620

;

-- ----------------------------
-- Table structure for `t_feature`
-- ----------------------------
DROP TABLE IF EXISTS `t_feature`;
CREATE TABLE `t_feature` (
`id`  int(11) UNSIGNED NOT NULL AUTO_INCREMENT ,
`pid`  int(11) NULL DEFAULT NULL ,
`feature`  varchar(50) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL ,
`detail`  varchar(100) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL ,
`server_id`  int(11) UNSIGNED NULL DEFAULT NULL ,
`fabric`  varchar(50) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL ,
`exec_info`  varchar(200) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL ,
PRIMARY KEY (`id`)
)
ENGINE=InnoDB
DEFAULT CHARACTER SET=latin1 COLLATE=latin1_swedish_ci
AUTO_INCREMENT=11

;

-- ----------------------------
-- Table structure for `t_ipsec`
-- ----------------------------
DROP TABLE IF EXISTS `t_ipsec`;
CREATE TABLE `t_ipsec` (
`id`  int(11) UNSIGNED NOT NULL AUTO_INCREMENT ,
`server_id`  int(11) NULL DEFAULT NULL ,
`chain`  enum('FORWARD','OUTPUT','INPUT') CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`source_addr`  varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`dest_addr`  varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`protocal`  enum('all','icmp','udp','tcp') CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`dport`  varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`status`  tinyint(4) NULL DEFAULT NULL ,
`description`  varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`createdate`  datetime NULL DEFAULT NULL ,
`modifydate`  timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP ,
PRIMARY KEY (`id`),
INDEX `t_ipsec_server_id` (`server_id`) USING BTREE 
)
ENGINE=InnoDB
DEFAULT CHARACTER SET=utf8 COLLATE=utf8_general_ci
AUTO_INCREMENT=93

;

-- ----------------------------
-- Table structure for `t_server`
-- ----------------------------
DROP TABLE IF EXISTS `t_server`;
CREATE TABLE `t_server` (
`id`  int(10) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'è‡ªå¢žID' ,
`pid`  int(10) UNSIGNED NULL DEFAULT NULL COMMENT 'çˆ¶ID' ,
`region`  varchar(4) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT 'åœ°åŒº' ,
`product`  varchar(40) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT 'äº§å“' ,
`role`  varchar(15) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT 'æœåŠ¡å™¨è§’è‰²' ,
`loginuser`  varchar(40) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT 'root' ,
`description`  varchar(250) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`ip_oper`  varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT 'è¿ç»´æ“ä½œIP' ,
`ip_private`  varchar(16) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT 'ç§ç½‘IP' ,
`ip_public`  varchar(16) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT 'å…¬ç½‘IP' ,
`ip_ilo`  varchar(16) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT 'ILO IP' ,
`ip_monitor`  varchar(16) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`ip_ntp_server`  varchar(16) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`is_reserve`  tinyint(1) NULL DEFAULT 0 COMMENT 'æ˜¯å¦ä¸ºå¤‡æœº' ,
`is_online`  tinyint(1) NULL DEFAULT 0 ,
`dbms`  varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT 'å…³ç³»æ•°æ®åº“' ,
`vender`  varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT 'æœåŠ¡å™¨åŽ‚å•†' ,
`model`  varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT 'æœåŠ¡å™¨äº§å“å' ,
`serial`  varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`os_type`  varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT 'æ“ä½œç³»ç»Ÿç±»åž‹' ,
`os_release`  varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT 'æ“ä½œç³»ç»Ÿç‰ˆæœ¬' ,
`os_arch`  varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '32/64ä½' ,
`update_time`  timestamp NOT NULL DEFAULT '0000-00-00 00:00:00' ON UPDATE CURRENT_TIMESTAMP COMMENT 'ä¿®æ”¹æ—¶é—´' ,
`create_time`  timestamp NOT NULL DEFAULT '0000-00-00 00:00:00' COMMENT 'åˆ›å»ºæ—¶é—´' ,
`is_deleted`  tinyint(1) NULL DEFAULT 0 COMMENT 'åˆ é™¤æ ‡è®°' ,
PRIMARY KEY (`id`)
)
ENGINE=InnoDB
DEFAULT CHARACTER SET=utf8 COLLATE=utf8_general_ci
AUTO_INCREMENT=337

;

-- ----------------------------
-- Table structure for `t_server_backup`
-- ----------------------------
DROP TABLE IF EXISTS `t_server_backup`;
CREATE TABLE `t_server_backup` (
`id`  int(10) UNSIGNED NOT NULL DEFAULT 0 COMMENT '×ÔÔöID' ,
`pid`  int(10) UNSIGNED NULL DEFAULT NULL COMMENT '¸¸ID' ,
`region`  varchar(4) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT 'µØÇø' ,
`product`  varchar(40) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT '²úÆ·' ,
`role`  varchar(15) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT '·þÎñÆ÷½ÇÉ«' ,
`loginuser`  varchar(40) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT 'root' ,
`description`  varchar(250) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT '·þÎñÆ÷ÃèÊö' ,
`ip_oper`  varchar(16) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT 'ÔËÎ¬²Ù×÷IP' ,
`ip_private`  varchar(16) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT 'Ë½ÍøIP' ,
`ip_public`  varchar(16) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT '¹«ÍøIP' ,
`ip_ilo`  varchar(16) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT 'ILO IP' ,
`is_reserve`  tinyint(1) NULL DEFAULT 0 COMMENT 'ÊÇ·ñÎª±¸»ú' ,
`dbms`  varchar(20) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT '¹ØÏµÊý¾Ý¿â' ,
`vender`  varchar(20) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT '·þÎñÆ÷³§ÉÌ' ,
`model`  varchar(100) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT '·þÎñÆ÷²úÆ·Ãû' ,
`os_type`  varchar(20) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT '²Ù×÷ÏµÍ³ÀàÐÍ' ,
`os_release`  varchar(20) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT '²Ù×÷ÏµÍ³°æ±¾' ,
`os_arch`  varchar(20) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT '32/64Î»' ,
`update_time`  timestamp NOT NULL DEFAULT '0000-00-00 00:00:00' COMMENT 'ÐÞ¸ÄÊ±¼ä' ,
`create_time`  timestamp NOT NULL DEFAULT '0000-00-00 00:00:00' COMMENT '´´½¨Ê±¼ä' ,
`is_deleted`  tinyint(1) NULL DEFAULT 0 COMMENT 'É¾³ý±ê¼Ç' 
)
ENGINE=InnoDB
DEFAULT CHARACTER SET=utf8 COLLATE=utf8_general_ci

;

-- ----------------------------
-- Table structure for `t_sysinfo`
-- ----------------------------
DROP TABLE IF EXISTS `t_sysinfo`;
CREATE TABLE `t_sysinfo` (
`id`  int(11) UNSIGNED NOT NULL AUTO_INCREMENT ,
`need_id`  int(11) UNSIGNED NULL DEFAULT NULL ,
`need_value`  varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`check_name`  varchar(40) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`check_cmd`  varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`sys_type`  enum('Windows','Linux') CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`result_reg`  varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`record_table`  varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
`record_field`  varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
PRIMARY KEY (`id`),
INDEX `idx_t_sysinfo_systype` (`sys_type`) USING BTREE 
)
ENGINE=InnoDB
DEFAULT CHARACTER SET=utf8 COLLATE=utf8_general_ci
AUTO_INCREMENT=39

;

-- ----------------------------
-- Table structure for `test`
-- ----------------------------
DROP TABLE IF EXISTS `test`;
CREATE TABLE `test` (
`col1`  int(10) NOT NULL AUTO_INCREMENT ,
`col2`  varchar(12) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL ,
PRIMARY KEY (`col1`)
)
ENGINE=InnoDB
DEFAULT CHARACTER SET=latin1 COLLATE=latin1_swedish_ci
AUTO_INCREMENT=1

;

-- ----------------------------
-- Auto increment value for `auth_group`
-- ----------------------------
ALTER TABLE `auth_group` AUTO_INCREMENT=1;

-- ----------------------------
-- Auto increment value for `auth_group_permissions`
-- ----------------------------
ALTER TABLE `auth_group_permissions` AUTO_INCREMENT=1;

-- ----------------------------
-- Auto increment value for `auth_permission`
-- ----------------------------
ALTER TABLE `auth_permission` AUTO_INCREMENT=25;

-- ----------------------------
-- Auto increment value for `auth_user`
-- ----------------------------
ALTER TABLE `auth_user` AUTO_INCREMENT=3;

-- ----------------------------
-- Auto increment value for `auth_user_groups`
-- ----------------------------
ALTER TABLE `auth_user_groups` AUTO_INCREMENT=1;

-- ----------------------------
-- Auto increment value for `auth_user_user_permissions`
-- ----------------------------
ALTER TABLE `auth_user_user_permissions` AUTO_INCREMENT=4;

-- ----------------------------
-- Auto increment value for `check_server_list`
-- ----------------------------
ALTER TABLE `check_server_list` AUTO_INCREMENT=39;

-- ----------------------------
-- Auto increment value for `checklist_entry`
-- ----------------------------
ALTER TABLE `checklist_entry` AUTO_INCREMENT=1;

-- ----------------------------
-- Auto increment value for `checklist_event`
-- ----------------------------
ALTER TABLE `checklist_event` AUTO_INCREMENT=1;

-- ----------------------------
-- Auto increment value for `checklist_event_history`
-- ----------------------------
ALTER TABLE `checklist_event_history` AUTO_INCREMENT=1;

-- ----------------------------
-- Auto increment value for `checklist_job`
-- ----------------------------
ALTER TABLE `checklist_job` AUTO_INCREMENT=1;

-- ----------------------------
-- Auto increment value for `checklist_job_history`
-- ----------------------------
ALTER TABLE `checklist_job_history` AUTO_INCREMENT=1;

-- ----------------------------
-- Auto increment value for `db_schemas`
-- ----------------------------
ALTER TABLE `db_schemas` AUTO_INCREMENT=1;

-- ----------------------------
-- Auto increment value for `django_admin_log`
-- ----------------------------
ALTER TABLE `django_admin_log` AUTO_INCREMENT=369;

-- ----------------------------
-- Auto increment value for `django_content_type`
-- ----------------------------
ALTER TABLE `django_content_type` AUTO_INCREMENT=9;

-- ----------------------------
-- Auto increment value for `django_site`
-- ----------------------------
ALTER TABLE `django_site` AUTO_INCREMENT=2;

-- ----------------------------
-- Auto increment value for `t_backup_info`
-- ----------------------------
ALTER TABLE `t_backup_info` AUTO_INCREMENT=2294;

-- ----------------------------
-- Auto increment value for `t_backup_server`
-- ----------------------------
ALTER TABLE `t_backup_server` AUTO_INCREMENT=1;

-- ----------------------------
-- Auto increment value for `t_crontab`
-- ----------------------------
ALTER TABLE `t_crontab` AUTO_INCREMENT=1620;

-- ----------------------------
-- Auto increment value for `t_feature`
-- ----------------------------
ALTER TABLE `t_feature` AUTO_INCREMENT=11;

-- ----------------------------
-- Auto increment value for `t_ipsec`
-- ----------------------------
ALTER TABLE `t_ipsec` AUTO_INCREMENT=93;

-- ----------------------------
-- Auto increment value for `t_server`
-- ----------------------------
ALTER TABLE `t_server` AUTO_INCREMENT=337;

-- ----------------------------
-- Auto increment value for `t_sysinfo`
-- ----------------------------
ALTER TABLE `t_sysinfo` AUTO_INCREMENT=39;

-- ----------------------------
-- Auto increment value for `test`
-- ----------------------------
ALTER TABLE `test` AUTO_INCREMENT=1;
