const photoFilterModel = require("../../../model/photo-filter.model")
const photoLayoutModel = require("../../../model/photo-layout.model")
const photoTemplateModel = require("../../../model/photo-template.model")
const { prisma } = require("../../../prisma/client")




class PhotoTemplateService {
    async getEnablePhotoTemplates(req,res){
        try {
            return await photoTemplateModel.getEnables()
        }
        catch (error){
            throw error
        }
    }

    async getPhotoTemplateByUid(req,res){
        try {
            const photoTemplateUid = req.params.photo_template_uid
            return await photoTemplateModel.getByUid({photoTemplateUid: photoTemplateUid})
        }
        catch (error){
            throw error
        }
    }

    async getPhotoTemplateDetailByUid(req,res){
        try {
            const photoTemplateUid = req.params.photo_template_uid
            return prisma.$transaction([
                photoTemplateModel.getByUid({photoTemplateUid: photoTemplateUid}),
                photoLayoutModel.getManyByTemplateUid({templateUid: photoTemplateUid}),
                photoFilterModel.getManyByTemplateUid({templateUid: photoTemplateUid})
            ])
        }
        catch (error){
            throw error
        }
    }

    async createPhotoProduct(req,res){
        try {
            const photoTemplateUid = req.body.photo_template_uid
            const photoLayoutUid = req.body.photo_layout_uid
            const filepaths = req.body.filepaths
            
            
            
               
        }
        catch (error){
            throw error
        }
    }
}

module.exports = new PhotoTemplateService()