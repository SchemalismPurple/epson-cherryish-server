/*
  Warnings:

  - You are about to drop the column `filter_filepath` on the `photo_filter` table. All the data in the column will be lost.
  - You are about to drop the column `background_filepath` on the `photo_layout` table. All the data in the column will be lost.
  - You are about to drop the column `thumbnail_filepath` on the `photo_template` table. All the data in the column will be lost.
  - Added the required column `original_image_filepath` to the `photo_filter` table without a default value. This is not possible if the table is not empty.
  - Added the required column `thumbnail_image_filepath` to the `photo_filter` table without a default value. This is not possible if the table is not empty.
  - Added the required column `original_image_filepath` to the `photo_layout` table without a default value. This is not possible if the table is not empty.
  - Added the required column `thumbnail_image_filepath` to the `photo_layout` table without a default value. This is not possible if the table is not empty.
  - Added the required column `original_image_filepath` to the `photo_template` table without a default value. This is not possible if the table is not empty.
  - Added the required column `thumbnail_image_filepath` to the `photo_template` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE `photo_filter` DROP COLUMN `filter_filepath`,
    ADD COLUMN `original_image_filepath` VARCHAR(191) NOT NULL,
    ADD COLUMN `thumbnail_image_filepath` VARCHAR(191) NOT NULL;

-- AlterTable
ALTER TABLE `photo_layout` DROP COLUMN `background_filepath`,
    ADD COLUMN `original_image_filepath` VARCHAR(191) NOT NULL,
    ADD COLUMN `thumbnail_image_filepath` VARCHAR(191) NOT NULL;

-- AlterTable
ALTER TABLE `photo_template` DROP COLUMN `thumbnail_filepath`,
    ADD COLUMN `original_image_filepath` VARCHAR(191) NOT NULL,
    ADD COLUMN `thumbnail_image_filepath` VARCHAR(191) NOT NULL;

-- CreateTable
CREATE TABLE `photo_product` (
    `uid` VARCHAR(191) NOT NULL,
    `photo_template_uid` VARCHAR(191) NOT NULL,

    UNIQUE INDEX `photo_product_uid_key`(`uid`),
    PRIMARY KEY (`uid`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
