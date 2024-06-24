const { prisma } = require("../prisma/client/index")
const db = prisma.photo_template

class PhotoTemplateModel {
    getEnables(){
        return db.findMany({
            where:{
                enable: true
            }
        })
    }

    getByUid({photoTemplateUid}){
        return db.findFirst({
            where:{
                uid: photoTemplateUid
            }
        })
    }
}

module.exports = new PhotoTemplateModel()