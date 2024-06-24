
const { failResponse } = require("../../response/fail.response")
const { successResponse } = require("../../response/success.response")
const photoTemplateService = require("../../service/photo-template/photo-template.service")






class PhotoTemplateController {
    async getEnablePhotoTemplates(req, res) {
        try {
            const enablePhotoTemplates = await photoTemplateService.getEnablePhotoTemplates(req, res)
            return successResponse(
                req, res, 201, "success", { photo_templates: enablePhotoTemplates }
            )
        }
        catch (error) {
            console.log("[ERROR - getEnablePhotoTemplates] ", error)
            return failResponse(
                req, res, 500, "internal_error", error
            )
        }
    }

    async getPhotoTemplateDetailByUid(req, res) {
        try {
            const [photoTemplate, photoLayouts, photoFilters] = await photoTemplateService.getPhotoTemplateDetailByUid(req, res)
            return successResponse(
                req, res, 201, "success", {
                photo_template: photoTemplate,
                photo_layouts: photoLayouts,
                photo_filters: photoFilters
            }
            )
        }
        catch (error) {
            console.log("[ERROR - getPhotoTemplateDetailByUid] ", error)
            return failResponse(
                req, res, 500, "internal_error", error
            )
        }
    }

    async requestCreatePhotoProduct(req, res) {
        try {

        }
        catch (error) {

        }
    }
}


module.exports = new PhotoTemplateController()