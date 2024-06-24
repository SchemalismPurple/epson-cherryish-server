/*
  Warnings:

  - Added the required column `photo_template_uid` to the `photo_filter` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE `photo_filter` ADD COLUMN `photo_template_uid` VARCHAR(191) NOT NULL;
