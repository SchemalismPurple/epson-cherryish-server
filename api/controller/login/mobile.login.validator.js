const {body} = require('express-validator')

const mobileLoginValidationRules = () => {
    return [
        body('social_type').notEmpty().withMessage('social_type is required'),
        body('social_id').notEmpty().withMessage('social_id is required'),
        body('name').notEmpty().withMessage('name is required'),
        body('email').isEmail().withMessage('invalid email'),
        body('device').notEmpty().withMessage('device is required'),
        body('os').isIn(['ios', 'aos']).withMessage('os must be either ios or aos'),
        body('os_version').notEmpty().withMessage('os_version is required')
    ];
};

module.exports = {
    mobileLoginValidationRules
}