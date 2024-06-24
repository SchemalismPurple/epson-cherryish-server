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
    if (res.headersSent) {
        // 응답이 이미 보내진 경우에는 로그만 남기고 함수 종료
        console.log("Headers already sent.");
        return;
    }

    return res
        .status(code)
        .send({
            url: req.url,
            reason: reason,
            message: message
        });
}


module.exports = {failResponse}