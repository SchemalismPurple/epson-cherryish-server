const { prisma } = require("../prisma/client/index")
const db = prisma.photo_template


const dummyData = [
    {
        uid: "uid1",
        title: "2024 Epson Innovation Challenge",
        sub_title: "Epson Connect Api를 활용한 스마트 IoT 프린터 '시야' 의 서비스를 체험해보세요",
        latitude: 37.512523,
        longitude: 127.102591,
        zoom: 1,
        address: "잠실 롯데타워 SKY31",
        thumbnail_image_filepath: "photo-template/thumbnail.png",
        original_image_filepath:  "photo-template/thumbnail.png",
        open_time: 1718960327,
        close_time: 1719799581,
        cost: 0,
        created_time: 1719043983,
        updated_time: 1719043983,
        like_count: 1,
        description: "1번의 재촬영의 기회가 주어집니다. 촬영을 마친 후 '확인' 버튼을 누르면 환불이 불가합니다. 출력이 되지 않았다면 현장 스태프에게 문의주세요.",
        enable: true
    }
]

async function deletes(){
    try {
        const a = await db.deleteMany()
        return a
    }
    catch (error){
        console.log(error)
    }
}
async function create(){
    try {
        const aaa = dummyData.map(dummy => {
            return db.create({
                data: dummy
            })
        })
        const bbb = await prisma.$transaction(aaa)
        console.log(bbb)
    }
    catch (error){
        console.log(error)
    }
}


async function readMany(){
    try {
        const a = await db.findMany()
        console.log(a)
    }
    catch (error){
        console.log(error)
    }
}



// deletes()
create()
// readMany()