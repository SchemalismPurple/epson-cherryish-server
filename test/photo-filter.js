const { prisma } = require("../prisma/client/index")
const db = prisma.photo_filter


const dummyData = [
    {
        uid: "filter1-1",
        photo_template_uid: "uid1",
        photo_layout_uid: "layout1-1",
        x:280,
        y:472,
        width: 1650,
        height: 2200,
        original_image_filepath: "filter1-1.png",
        thumbnail_image_filepath: "filter1-1.png"
    },
    {
        uid: "filter1-2",
        photo_template_uid: "uid1",
        photo_layout_uid: "layout1-1",
        x:2070,
        y:924,
        width: 1650,
        height: 2200,
        original_image_filepath: "filter1-2.png",
        thumbnail_image_filepath: "filter1-2.png"
    },
    {
        uid: "filter1-3",
        photo_template_uid: "uid1",
        photo_layout_uid: "layout1-1",
        x:280,
        y:2876,
        width: 1650,
        height: 2200,
        original_image_filepath: "filter1-3.png",
        thumbnail_image_filepath: "filter1-3.png"
    },
    {
        uid: "filter1-4",
        photo_template_uid: "uid1",
        photo_layout_uid: "layout1-1",
        x:2070,
        y:3328,
        width: 1650,
        height: 2200,
        original_image_filepath: "filter1-4.png",
        thumbnail_image_filepath: "filter1-4.png"
    },




    {
        uid: "filter2-1",
        photo_template_uid: "uid1",
        photo_layout_uid: "layout1-2",
        x:280,
        y:472,
        width: 1650,
        height: 2200,
        original_image_filepath: "filter2-1.png",
        thumbnail_image_filepath: "filter2-1.png"
    },
    {
        uid: "filter2-2",
        photo_template_uid: "uid1",
        photo_layout_uid: "layout1-2",
        x:2070,
        y:924,
        width: 1650,
        height: 2200,
        original_image_filepath: "filter2-2.png",
        thumbnail_image_filepath: "filter2-2.png"
    },
    {
        uid: "filter2-3",
        photo_template_uid: "uid1",
        photo_layout_uid: "layout1-2",
        x:280,
        y:2876,
        width: 1650,
        height: 2200,
        original_image_filepath: "filter2-3.png",
        thumbnail_image_filepath: "filter2-3.png"
    },
    {
        uid: "filter2-4",
        photo_template_uid: "uid1",
        photo_layout_uid: "layout1-2",
        x:2070,
        y:3328,
        width: 1650,
        height: 2200,
        original_image_filepath: "filter2-4.png",
        thumbnail_image_filepath: "filter2-4.png"
    },




    {
        uid: "filter3-1",
        photo_template_uid: "uid1",
        photo_layout_uid: "layout1-3",
        x:280,
        y:472,
        width: 1650,
        height: 2200,
        original_image_filepath: "filter3-1.png",
        thumbnail_image_filepath: "filter3-1.png"
    },
    {
        uid: "filter3-2",
        photo_template_uid: "uid1",
        photo_layout_uid: "layout1-3",
        x:2070,
        y:924,
        width: 1650,
        height: 2200,
        original_image_filepath: "filter3-2.png",
        thumbnail_image_filepath: "filter3-2.png"
    },
    {
        uid: "filter3-3",
        photo_template_uid: "uid1",
        photo_layout_uid: "layout1-3",
        x:280,
        y:2876,
        width: 1650,
        height: 2200,
        original_image_filepath: "filter3-3.png",
        thumbnail_image_filepath: "filter3-3.png"
    },
    {
        uid: "filter3-4",
        photo_template_uid: "uid1",
        photo_layout_uid: "layout1-3",
        x:2070,
        y:3328,
        width: 1650,
        height: 2200,
        original_image_filepath: "filter3-4.png",
        thumbnail_image_filepath: "filter3-4.png"
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