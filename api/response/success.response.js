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
        console.log("TTT")
        const payload = {
            result: result,
            content: contents
        }
        console.log("YYY, ",payload)
        console.log("@@@,",code)

        return res
            .status(code)
            .send(payload);

    } catch (error) {
        console.log(error)
        return failResponse(req, res, 500, "unknown", error)
    }
}

module.exports = {successResponse}