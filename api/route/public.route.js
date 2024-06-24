const express = require('express');
const router = express.Router();



const mobileLoginController = require('../controller/login/mobile.login.controller');
const mobileLoginValidator = require('../controller/login/mobile.login.validator')
router.post('/login/mobile',mobileLoginValidator.mobileLoginValidationRules(),mobileLoginController.login)







module.exports = router