const mobileUserModel = require("../../../model/mobile.user.model");


class MobileUserService {
    async getUserBySocialLogin(req, res) {
        try {
            const { social_type, social_id } = req.body;
            
            const mobileUser = await mobileUserModel.getBySocialInformation({socialType: social_type, socialId: social_id})
            return mobileUser
        }
        catch (error) {
            throw error
        }
    }

    async createUser(req, res) {
        try {
            const userData = req.body;

            const newMobileUser = await mobileUserModel.createNew({data: userData})
            return newMobileUser
        }
        catch (error) {
            throw error
        }
    }
}


module.exports = new MobileUserService()