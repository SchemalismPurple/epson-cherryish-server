const { S3Client,GetObjectCommand } = require("@aws-sdk/client-s3");
const fs = require('fs')
const { Upload } = require('@aws-sdk/lib-storage')
const sharp = require('sharp')
const path = require('path');
const { spawn } = require('child_process');

const s3Client = new S3Client({
    region: 'ap-northeast-2'
})




class S3Service {
    async uploadFileToS3(filePath, key, isBuffer = false) {
        const fileStream = isBuffer ? filePath : fs.createReadStream(filePath);
        const uploader = new Upload({
            client: s3Client,
            params: {
                Bucket: 'seeya-bucket',
                Key: key,
                Body: fileStream,
            },
        });
        await uploader.done();
    }


    async downloadFileFromS3({ fileKey }) {
        const params = {
            Bucket: "seeya-bucket",
            Key: fileKey
        };

        try {
            const localFilePath = path.join(`/home/ubuntu/MainServer/image-encoder/assets`, path.basename(fileKey));

            const data = await s3Client.send(new GetObjectCommand({ Bucket: params.Bucket, Key: params.Key }));

            const stream = data.Body;
            const buffer = await streamToBuffer(stream);
            ensureDirectoryExistence(localFilePath)
            fs.writeFileSync(localFilePath, buffer);
            console.log(`Downloaded '${fileKey}' to '${localFilePath}'`);
            return localFilePath
        } catch (error) {
            console.log('Download Fail', fileKey)
            throw error
        }
    }


    ensureDirectoryExistence(filePath) {
        const dirname = path.dirname(filePath);
        if (fs.existsSync(dirname)) {
            return true;
        }
        ensureDirectoryExistence(dirname);
        fs.mkdirSync(dirname);
    }

    streamToBuffer(stream) {
        return new Promise((resolve, reject) => {
            const chunks = [];
            stream.on('data', (chunk) => chunks.push(chunk));
            stream.on('end', () => resolve(Buffer.concat(chunks)));
            stream.on('error', reject);
        });
    }



    async rotateImage(filePath) {
        return await sharp(filePath)
            .rotate()
            .toBuffer();
    }
}


module.exports = new S3Service()