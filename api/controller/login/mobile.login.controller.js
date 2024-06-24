const { generateToken } = require("../../../utils/token");
const { failResponse } = require("../../response/fail.response");
const { successResponse } = require("../../response/success.response");
const mobileUserService = require("../../service/user/mobile.user.service");
const { mobileLoginValidationRules } = require("./mobile.login.validator")
const {validationResult} = require('express-validator')



class MobileLoginController {
    getValidationRules(){
        return mobileLoginValidationRules();
    }

    async login(req,res){
        // request body check
        // const errors = validationResult(req)
        // if (!errors.isEmpty()){
        //     return failResponse(
        //         req,res,400,"error",errors.array()
        //     )
        // }

        try {
            const existedMobileUser = await mobileUserService.getUserBySocialLogin(req,res)
            if (existedMobileUser){
                return successResponse(
                    req,res,201,"success",{user: existedMobileUser, access_token: generateToken({userUid: existedMobileUser.uid})}
                )
            }

            const newMobileUser = await mobileUserService.createUser(req,res)
            return successResponse(
                req,res,201,"success",{user: newMobileUser, access_token: generateToken({userUid: newMobileUser.uid})}
            )
        }
        catch (error){
            console.log(error)
            return failResponse(
                req,res,500,"internal_error",error
            )
        }
    }
}


module.exports = new MobileLoginController()