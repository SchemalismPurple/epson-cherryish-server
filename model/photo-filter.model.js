const { prisma } = require("../prisma/client/index")
const db = prisma.photo_filter

class PhotoFilter {
    getByLayoutUid({layoutUid}){
        return db.findFirst({
            where:{
                photo_layout_uid: layoutUid
            }
        })
    }

    getManyByTemplateUid({templateUid}){
        return db.findMany({
            where:{
                photo_template_uid: templateUid
            }
        })
    }
}

module.exports = new PhotoFilter()