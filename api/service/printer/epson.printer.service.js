
const axios = require("axios");
const querystring = require("querystring");
const fs = require('fs')


const BASE_URL = "https://api.epsonconnect.com";
const DEVICE = "cherryish@print.epsonconnect.com";
const CLIENT_ID = "b102680703994db39bc174b84b4558e8";
const CLIENT_SECRET = "G8PbkXFKqYGb5rWrKEr6ZXNGKfiTAJw2NhLEvUIG18KY1gl7JqVQvlxYyIL8K0do";
let cachedToken = null;
let tokenExpiryTime = null;




class EpsonPrinterService {
    async getToken() {
        const url = `${BASE_URL}/api/1/printing/oauth2/auth/token?subject=printer`;

        const queryParam = {
            grant_type: "password",
            username: DEVICE,
            password: "",
        };

        const queryString = querystring.stringify(queryParam);
        const stringToEncode = `${CLIENT_ID}:${CLIENT_SECRET}`;
        const auth = Buffer.from(stringToEncode).toString('base64');

        const headers = {
            Authorization: "Basic " + auth,
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        };

        try {
            const response = await axios.post(url, queryString, {
                headers: headers,
            });



            if (response.data.access_token) {
                console.log(response.data)
                return response.data.access_token
            }
            else {
                return undefined
            }
        } catch (error) {
            console.error(
                "Error fetching token:",
                error.response ? error.response.data : error.message
            );
            throw error;
        }
    }



    async createPrintJob(subject_id, access_token) {
        const jobUri = `${BASE_URL}/api/1/printing/printers/${subject_id}/jobs`;

        const dataParam = {
            job_name: 'SampleJob1',
            print_mode: 'photo',
        };

        const headers = {
            Authorization: `Bearer ${access_token}`,
            'Content-Type': 'application/json;charset=utf-8',
        };

        try {
            const response = await axios.post(jobUri, dataParam, { headers });
            console.log('2. Create print job: -------------------------------');
            console.log(jobUri);
            console.log(dataParam);
            console.log(`${response.status}: ${response.statusText}`);
            console.log(response.data);
            return response.data;
        } catch (error) {
            console.error('Error creating print job:', error.response ? error.response.data : error.message);
            process.exit(1);
        }
    }

    // --------------------------------------------------------------------------------
    // 3. Upload print file
    async uploadPrintFile(uploadUri, localFilePath) {


        const headers = {
            'Content-Type': 'image/jpeg',
            'Content-Length': `${fs.statSync(localFilePath).size}`
        };

        try {
            const response = await axios.post(uploadUri, fs.createReadStream(localFilePath), { headers });
            console.log('3. Upload print file: ------------------------------');
            console.log(uploadUri);
            console.log(`${response.status}: ${response.statusText}`);
        } catch (error) {
            console.error('Error uploading print file:', error.response ? error.response.data : error.message);
            process.exit(1);
        }
    }

    // --------------------------------------------------------------------------------
    // 4. Execute print
    async executePrint(subject_id, job_id, access_token) {
        const printUri = `${BASE_URL}/api/1/printing/printers/${subject_id}/jobs/${job_id}/print`;

        const headers = {
            Authorization: `Bearer ${access_token}`,
            'Content-Type': 'application/json;charset=utf-8',
        };

        try {
            const response = await axios.post(printUri, {}, { headers });
            console.log('4. Execute print: ----------------------------------');
            console.log(printUri);
            console.log(`${response.status}: ${response.statusText}`);
            console.log(response.data);
        } catch (error) {
            console.error('Error executing print:', error.response ? error.response.data : error.message);
        }
    }

    async requestPrint() {
        try {
            const subject_id = "ebdd3da361d146c9bf6b791e1c916ad1"; 
            const access_token = 's817KoEUZYVJKXgdVnhWMAkfKuAZr17hEBdimUOudr1ax5DSrrl9AHps2mM0ttHi'; 
            const localFilePath = './fff.jpeg'; 
    
            const printJobData = await createPrintJob(subject_id, access_token);
            const job_id = printJobData.id;
            const base_uri = printJobData.upload_uri;
            console.log("------")
            console.log(printJobData)
            console.log(base_uri)
            console.log("------")
            const uploadUri = `${base_uri}&File=${encodeURIComponent('1.jpeg')}`;
            console.log(uploadUri)
            await uploadPrintFile(uploadUri, localFilePath);
            await executePrint(subject_id, job_id, access_token);
        }
        catch (error){
            throw error
        }

    }
}

module.exports = new EpsonPrinterService()

// (async () => {
//     const subject_id = "ebdd3da361d146c9bf6b791e1c916ad1"; // subject_id 설정
//     // const access_token = await getToken()
//     const access_token = 's817KoEUZYVJKXgdVnhWMAkfKuAZr17hEBdimUOudr1ax5DSrrl9AHps2mM0ttHi'; // access_token 설정
//     const localFilePath = './fff.jpeg'; // 업로드할 파일 경로

//     const printJobData = await createPrintJob(subject_id, access_token);
//     const job_id = printJobData.id;
//     const base_uri = printJobData.upload_uri;
//     console.log("------")
//     console.log(printJobData)
//     console.log(base_uri)
//     console.log("------")
//     const uploadUri = `${base_uri}&File=${encodeURIComponent('1.jpeg')}`;
//     console.log(uploadUri)


//     await uploadPrintFile(uploadUri, localFilePath);



//     await executePrint(subject_id, job_id, access_token);
// })();