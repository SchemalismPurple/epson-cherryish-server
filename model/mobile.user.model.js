const { prisma } = require("../prisma/client/index")
const db = prisma.mobile_user

class MobileUserModel {
    getBySocialInformation({socialType, socialId}){
        return db.findFirst({
            where:{
                social_type: socialType,
                social_id: socialId
            }
        })
    }

    createNew({data}){
        return db.create({
            data: data
        })
    }
}

module.exports = new MobileUserModel()