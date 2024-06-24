/*
  Warnings:

  - Added the required column `original_image_filepath` to the `photo_product` table without a default value. This is not possible if the table is not empty.
  - Added the required column `thumbnail_image_filepath` to the `photo_product` table without a default value. This is not possible if the table is not empty.
  - Added the required column `user_uid` to the `photo_product` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE `photo_product` ADD COLUMN `original_image_filepath` VARCHAR(191) NOT NULL,
    ADD COLUMN `thumbnail_image_filepath` VARCHAR(191) NOT NULL,
    ADD COLUMN `user_uid` INTEGER NOT NULL;
