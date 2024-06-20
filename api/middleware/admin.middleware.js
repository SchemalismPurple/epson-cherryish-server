const jwt = require('jsonwebtoken')

function authenticateToken(req, res, next) {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];
    

    if (!token) {
        next();
        return;
    }

    jwt.verify(token, process.env.TOKEN_SECRET_KEY, (err, decoded) => {
        if (err) {
            next();
            return;
        }

        req.user_uid = decoded.user_uid;
        next();
    });

}


module.exports = {
    authenticateToken
}
