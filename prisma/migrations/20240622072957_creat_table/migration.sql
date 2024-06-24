/*
  Warnings:

  - The primary key for the `mobile_user` table will be changed. If it partially fails, the table could be left without primary key constraint.
  - You are about to drop the column `id` on the `mobile_user` table. All the data in the column will be lost.
  - The primary key for the `partner_user` table will be changed. If it partially fails, the table could be left without primary key constraint.
  - You are about to drop the column `id` on the `partner_user` table. All the data in the column will be lost.
  - Added the required column `uid` to the `mobile_user` table without a default value. This is not possible if the table is not empty.
  - Added the required column `uid` to the `partner_user` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE `mobile_user` DROP PRIMARY KEY,
    DROP COLUMN `id`,
    ADD COLUMN `uid` INTEGER NOT NULL AUTO_INCREMENT,
    ADD PRIMARY KEY (`uid`);

-- AlterTable
ALTER TABLE `partner_user` DROP PRIMARY KEY,
    DROP COLUMN `id`,
    ADD COLUMN `uid` INTEGER NOT NULL AUTO_INCREMENT,
    ADD PRIMARY KEY (`uid`);
