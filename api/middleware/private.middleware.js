

const jwt = require('jsonwebtoken')
const failResponse = require('../response/fail.response');


function authenticateToken(req, res, next) {

    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (token === null) {
        return failResponse(req, res, 401, "empty_token", "token is null")
    }

    jwt.verify(token, process.env.TOKEN_SECRET_KEY, (err, decoded) => {
        if (err) {
            return failResponse(req, res, 401, "expired_token", "token is expired")
        }

        const userUid = decoded.user_uid;

        if (!userUid) {
            return failResponse(req, res, 401, "bad_access", "user is not defined on system")
        }

        req.user_uid = userUid

        next();
    });
}

module.exports = {
    authenticateToken
}