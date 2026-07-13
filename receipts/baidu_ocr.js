const fs = require('fs');
const path = require('path');
const https = require('https');

const API_KEY = 'qVi0Ux3koMk5xRhRCInL018r';
const SECRET_KEY = 'AFIZprSQxNLR6LdbtLa5BSuYYyWPsscP';

// Get access token
function getAccessToken() {
    return new Promise((resolve, reject) => {
        const postData = `grant_type=client_credentials&client_id=${API_KEY}&client_secret=${SECRET_KEY}`;
        const req = https.request({
            hostname: 'aip.baidubce.com',
            path: '/oauth/2.0/token',
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        }, res => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                const json = JSON.parse(data);
                if (json.access_token) resolve(json.access_token);
                else reject(new Error(JSON.stringify(json)));
            });
        });
        req.on('error', reject);
        req.write(postData);
        req.end();
    });
}

// Recognize text using Baidu OCR
function recognizeImage(token, imagePath) {
    return new Promise((resolve, reject) => {
        const imageData = fs.readFileSync(imagePath);
        const base64 = imageData.toString('base64');
        const postData = `image=${encodeURIComponent(base64)}&language_type=CHN_ENG`;
        
        const req = https.request({
            hostname: 'aip.baidubce.com',
            path: `/rest/2.0/ocr/v1/accurate_basic?access_token=${token}`,
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        }, res => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const json = JSON.parse(data);
                    resolve(json);
                } catch(e) {
                    reject(new Error(data));
                }
            });
        });
        req.on('error', reject);
        req.write(postData);
        req.end();
    });
}

(async () => {
    try {
        console.log('Getting access token...');
        const token = await getAccessToken();
        console.log('Token obtained.\n');
        
        const files = fs.readdirSync('.').filter(f => f.endsWith('.jpg')).sort();
        
        for (const file of files) {
            console.log(`\n========== ${file} ==========`);
            try {
                const result = await recognizeImage(token, file);
                if (result.words_result) {
                    const lines = result.words_result.map(w => w.words);
                    console.log(lines.join('\n'));
                    fs.writeFileSync(file + '.baidu.txt', lines.join('\n'));
                } else {
                    console.log('No text found. Full result:', JSON.stringify(result));
                }
            } catch (err) {
                console.error(`Error: ${err.message}`);
            }
            // Small delay to avoid rate limiting
            await new Promise(r => setTimeout(r, 500));
        }
        console.log('\nDone! All results saved.');
    } catch (err) {
        console.error('Fatal:', err.message);
    }
})();
