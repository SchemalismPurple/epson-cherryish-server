const { prisma } = require("../prisma/client/index")
const db = prisma.photo_layout


const dummyData = [
    {
        uid: "layout1-1",
        photo_template_uid: "uid1",
        width: 4000,
        height: 6000,
        background_color: "#ff7286ff",
        original_image_filepath: "photo-layout/layout01.png",
        thumbnail_image_filepath: "photo-layout/layout01.png"
    },
    {
        uid: "layout1-2",
        photo_template_uid: "uid1",
        width: 4000,
        height: 6000,
        background_color: "#ff7286ff",
        original_image_filepath: "photo-layout/layout02.png",
        thumbnail_image_filepath: "photo-layout/layout02.png"
    },
    {
        uid: "layout1-3",
        photo_template_uid: "uid1",
        width: 4000,
        height: 6000,
        background_color: "#ff7286ff",
        original_image_filepath: "photo-layout/layout03.png",
        thumbnail_image_filepath: "photo-layout/layout03.png"
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