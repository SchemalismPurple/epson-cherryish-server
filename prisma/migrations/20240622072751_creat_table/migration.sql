-- CreateTable
CREATE TABLE `partner_user` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `name` INTEGER NOT NULL,
    `social_type` VARCHAR(191) NOT NULL,
    `social_id` VARCHAR(191) NOT NULL,
    `fcm_token` VARCHAR(191) NULL,
    `birth` VARCHAR(191) NULL,
    `phone` VARCHAR(191) NULL,
    `email` VARCHAR(191) NOT NULL,

    UNIQUE INDEX `partner_user_phone_key`(`phone`),
    UNIQUE INDEX `partner_user_email_key`(`email`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `mobile_user` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(191) NOT NULL,
    `social_type` VARCHAR(191) NOT NULL,
    `social_id` VARCHAR(191) NOT NULL,
    `fcm_token` VARCHAR(191) NULL,
    `birth` VARCHAR(191) NULL,
    `phone` VARCHAR(191) NULL,
    `email` VARCHAR(191) NOT NULL,
    `device` VARCHAR(191) NOT NULL,
    `os` VARCHAR(191) NOT NULL,
    `os_version` VARCHAR(191) NOT NULL,

    UNIQUE INDEX `mobile_user_phone_key`(`phone`),
    UNIQUE INDEX `mobile_user_email_key`(`email`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `photo_template` (
    `uid` VARCHAR(191) NOT NULL,
    `title` VARCHAR(191) NOT NULL,
    `sub_title` VARCHAR(191) NOT NULL,
    `latitude` DOUBLE NOT NULL,
    `longitude` DOUBLE NOT NULL,
    `zoom` DOUBLE NOT NULL,
    `address` VARCHAR(191) NOT NULL,
    `thumbnail_filepath` VARCHAR(191) NOT NULL,
    `open_time` INTEGER NOT NULL,
    `close_time` INTEGER NOT NULL,
    `cost` INTEGER NULL,
    `created_time` INTEGER NOT NULL,
    `updated_time` INTEGER NOT NULL,
    `like_count` INTEGER NOT NULL,
    `description` VARCHAR(191) NOT NULL,
    `enable` BOOLEAN NOT NULL,

    UNIQUE INDEX `photo_template_uid_key`(`uid`),
    PRIMARY KEY (`uid`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `photo_layout` (
    `uid` VARCHAR(191) NOT NULL,
    `photo_template_uid` VARCHAR(191) NOT NULL,
    `width` INTEGER NOT NULL,
    `height` INTEGER NOT NULL,
    `background_color` VARCHAR(191) NOT NULL,
    `background_filepath` VARCHAR(191) NOT NULL,

    UNIQUE INDEX `photo_layout_uid_key`(`uid`),
    PRIMARY KEY (`uid`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `photo_filter` (
    `uid` VARCHAR(191) NOT NULL,
    `photo_layout_uid` VARCHAR(191) NOT NULL,
    `x` INTEGER NOT NULL,
    `y` INTEGER NOT NULL,
    `width` INTEGER NOT NULL,
    `height` INTEGER NOT NULL,
    `filter_filepath` VARCHAR(191) NULL,

    UNIQUE INDEX `photo_filter_uid_key`(`uid`),
    PRIMARY KEY (`uid`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
