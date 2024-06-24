
const axios = require("axios");
const querystring = require("querystring");
const fs = require('fs')


const BASE_URL = process.env.EPSON_BASE_URL;
const DEVICE = process.env.EPSON_DEVICE;
const CLIENT_ID = process.env.EPSON_CLIENT_ID;
const CLIENT_SECRET = process.env.EPSON_CLIENT_SECRET;
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
                return response.data
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
            job_name: 'JOB13',
            print_mode: 'photo',
            print_setting: {
                "media_size": "ms_kg",
                "media_type": "mt_photopaper",
                "source": "rear",
                "color_mode": "color",
                "print_quality": "high",
                "borderless": true
            }
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
    
    async getPrinter(subject_id, access_token){
        const printUri = `${BASE_URL}/api/1/printing/printers/${subject_id}/capability/photo`;

        const headers = {
            Authorization: `Bearer ${access_token}`,
            'Content-Type': 'application/json;charset=utf-8',
        };

        try {
            const response = await axios.get(printUri, { headers });
            // console.log(response.data.media_sizes)
            response.data.media_sizes.forEach(size =>{
                console.log("------------")
                console.log(size)
                
                size.media_types.forEach(type => {
                    type.forEach(ele => {
                        
                    })
                    console.log(type)
                })
            })
        } catch (error) {
            console.error('Error executing print:', error.response ? error.response.data : error.message);
        }
    }

    async requestPrint() {
        try 
        {const token = await new EpsonPrinterService().getToken()
            const subject_id = token.subject_id
            const access_token = token.access_token
            const localFilePath = './a.jpeg'; 
    
            const printJobData = await this.createPrintJob(subject_id, access_token);
            const job_id = printJobData.id;
            const base_uri = printJobData.upload_uri;
            const uploadUri = `${base_uri}&File=${encodeURIComponent('a.jpeg')}`;
            await this.uploadPrintFile(uploadUri, localFilePath);
            await this.executePrint(subject_id, job_id, access_token);
        }
        catch (error){
            throw error
        }
    }
}

module.exports = new EpsonPrinterService()
