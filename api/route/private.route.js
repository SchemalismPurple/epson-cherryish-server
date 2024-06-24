const express = require('express');
const multer = require('multer');

const router = express.Router();


const photoTemplateController = require('../controller/photo-template/photo-template.controller');
router.get("/photo-template/all",photoTemplateController.getEnablePhotoTemplates)
router.get("/photo-template/:photo_template_uid",photoTemplateController.getPhotoTemplateDetailByUid)



const upload = multer({ dest: 'uploads/' });
const fileUploadController = require('../controller/upload/file.upload.controller');
router.post("/upload/file",upload.any(),fileUploadController.uploadFile)


module.exports = router

