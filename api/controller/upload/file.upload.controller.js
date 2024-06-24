const { S3Client } = require('@aws-sdk/client-s3')
const fs = require('fs')
const { Upload } = require('@aws-sdk/lib-storage')
const sharp = require('sharp')
const { v4: uuidv4 } = require('uuid')
const s3Service = require('../../service/s3/s3.service')
const { successResponse } = require('../../response/success.response')
const { failResponse } = require('../../response/fail.response')

const s3Client = new S3Client({
    region: 'ap-northeast-2'
})

class FileUploadController {
    async uploadFile(req, res) {
        try {
            const file = req.files[0];
            const filename = uuidv4()
            const s3FilePath = `users/${filename}.png`
            const rotatedImage = await s3Service.rotateImage(file.path)
            await s3Service.uploadFileToS3(rotatedImage, s3FilePath, true)

            fs.unlink(file.path, (err) => {
                if (err) console.error('Error deleting file:', err);
            });

            return successResponse(
                req, res, 201, "success", { s3_filepath: s3FilePath }
            )
        }
        catch (error) {
            console.log(error)
            return failResponse(
                req, res, 500, "fail", error
            )
        }
    }
}

module.exports = new FileUploadController()
