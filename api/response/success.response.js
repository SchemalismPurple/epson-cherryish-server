const UserModel = require('../../model/user.model');
const { timestamp } = require('../../utils/date.helper');
const { failResponse } = require('./fail.response');


/**
 * 
 * @param {import('express').Request} req - The Express request object.
 * @param {import('express').Response} res - The Express response object.
 * @param {number} code 
 * @param {string} result
 * @param {object} contents 
 * @returns 
 */
async function successResponse(req, res, code, result, contents) {
    try {
        const payload = {
            result: result,
            content: contents
        }

        if (req.service_type) {
            if (req.user_uid) {
                const user = await UserModel.update({userUid: req.user_uid, updateData: {updated_time: timestamp()}})
                payload["user"] = user
            }

            return res
                .status(code)
                .send(payload);
        }
        else {
            if (req.user_uid) {
                const user = await UserModel.update({userUid: req.user_uid, updateData: {updated_time: timestamp()}})
                payload["user"] = user
            }

            return res
                .status(code)
                .send(payload);
        }
    } catch (error) {
        return failResponse(req, res, 500, "unknown", error)
    }
}

module.exports = successResponse