const express = require('express')
const { json } = require('express')
const cors = require('cors')
const bodyParser = require('body-parser')
const app = express();
global.atob = require("atob"); // prisma 모듈에서 충돌나는 경우가 가끔 있어서 추가



app.use(bodyParser.json({ limit: '50mb' }));
app.use(bodyParser.urlencoded({ limit: '50mb', extended: true }));

app.use(cors());
app.use(json());

app.get('/test', (req, res) => {
    console.log("Tet")
    res.status(200).send('EC2 Express 서버 연결 성공!');
});



// Middleware ----- ----- ----- -----
const pubilcMiddleware = require('./api/middleware/public.middleware')
app.use("/public", pubilcMiddleware.authenticateToken)

const privateMiddleware = require('./api/middleware/private.middleware')
app.use("/private", privateMiddleware.authenticateToken)
// Middleware ----- ----- ----- -----



// Route ----- ----- ----- -----
const publicRoute = require('./api/route/public.route')
app.use("/public", publicRoute)

const privateRoute = require('./api/route/private.route')
app.use("/private", privateRoute)
// Route ----- ----- ----- -----







const deployPort = 8001
app.listen(deployPort, () => console.log(`Server Up and running at ${deployPort}`));