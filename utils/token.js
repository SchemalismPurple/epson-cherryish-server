const jwt = require('jsonwebtoken');

function generateToken({ userUid }) {
    const token = jwt.sign(
        {
            user_uid: userUid
        },
        process.env.TOKEN_SECRET_KEY,
        {
            expiresIn: '1d'
        }
    );
    return token
}

function generateAdminToken({ adminId, password }) {
    const token = jwt.sign(
        {
            admin_id: adminId,
            password: password
        },
        process.env.ADMIN_TOKEN_SECRET_KEY,
        {
            expiresIn: '1d'
        }
    );
    return token
}

module.exports = {
    generateToken,
    generateAdminToken
}

