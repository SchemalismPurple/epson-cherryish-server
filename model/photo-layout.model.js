const { prisma } = require("../prisma/client/index")
const db = prisma.photo_layout

class PhotoLayoutModel {
    getManyByTemplateUid({templateUid}){
        return db.findMany({
            where:{
                photo_template_uid: templateUid
            }
        })
    }
}

module.exports = new PhotoLayoutModel()