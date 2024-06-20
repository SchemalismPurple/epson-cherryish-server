/**
 * 
 * @param {import('express').Request} req - The Express request object.
 * @param {import('express').Response} res - The Express response object.
 * @param {number} code 
 * @param {string} reason 
 * @param {string} message 
 * @returns 
 */
function failResponse(req, res, code, reason, message) {
    return res
        .status(code)
        .send({
            url: req.url,
            reason: reason,
            message: message
        });
}


module.exports = failResponse