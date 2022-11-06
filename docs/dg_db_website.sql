/*
 Navicat Premium Data Transfer

 Source Server         : root
 Source Server Type    : MySQL
 Source Server Version : 80025
 Source Host           : localhost:3306
 Source Schema         : dg_db_website

 Target Server Type    : MySQL
 Target Server Version : 80025
 File Encoding         : 65001

 Date: 11/12/2021 14:48:33
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for html
-- ----------------------------
DROP TABLE IF EXISTS `html`;
CREATE TABLE `html`  (
  `md5` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT 'html的md5编码，8-24 bit',
  `html` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT 'html源文本',
  `create_time` datetime NOT NULL COMMENT '存入的时间',
  PRIMARY KEY (`md5`) USING BTREE,
  INDEX `md5`(`md5`) USING BTREE,
  CONSTRAINT `html_ibfk_1` FOREIGN KEY (`md5`) REFERENCES `news` (`md5`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for news
-- ----------------------------
DROP TABLE IF EXISTS `news`;
CREATE TABLE `news`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '新闻自身的id，自增',
  `website_id` int NOT NULL COMMENT '外键：新闻表网站地址id',
  `request_url` mediumtext CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '新闻的请求链接',
  `response_url` mediumtext CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '新闻网站的响应链接',
  `category1` mediumtext CHARACTER SET utf8 COLLATE utf8_general_ci NULL COMMENT '一级类别',
  `category2` mediumtext CHARACTER SET utf8 COLLATE utf8_general_ci NULL COMMENT '二级类别',
  `title` mediumtext CHARACTER SET utf8 COLLATE utf8_general_ci NULL COMMENT '标题',
  `abstract` mediumtext CHARACTER SET utf8 COLLATE utf8_general_ci NULL COMMENT '摘要',
  `body` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '正文',
  `pub_time` datetime NOT NULL COMMENT '发布时间例2017-01-01 00:00:00,\n没有发布时间的则为0000-00-00 00:00:00',
  `cole_time` datetime NOT NULL COMMENT '爬虫时间  年-月-日 时:分:秒',
  `images` mediumtext CHARACTER SET utf8 COLLATE utf8_general_ci NULL COMMENT '新闻图片列表，使用json的[]列表，没有则为NULL',
  `language_id` int NOT NULL COMMENT '外键：语音表的ID',
  `md5` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '8-24 bit',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `fk_news_1`(`website_id`) USING BTREE,
  INDEX `md5`(`md5`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '网站的新闻' ROW_FORMAT = DYNAMIC;

SET FOREIGN_KEY_CHECKS = 1;
