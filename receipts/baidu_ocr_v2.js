const fs = require('fs');
const https = require('https');
const http = require('http');

const API_KEY = '***';
const SECRET_KEY = 'AFIZpr…sscP';

function getAccessToken() {
    return new Promise((resolve, reject) => {
        const postData = `grant_type=client_credentials&client_id=${API_KEY}&client_secret=***}`;
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

function recognizeImage(token, imagePath, endpoint) {
    return new Promise((resolve, reject) => {
        const imageData = fs.readFileSync(imagePath);
        const base64 = imageData.toString('base64');
        const postData = `image=${encodeURIComponent(base64)}&language_type=CHN_ENG`;
        
        const req = https.request({
            hostname: 'aip.baidubce.com',
            path: `/rest/2.0/ocr/v1/${endpoint}?access_token=***}`,
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
                    reject(new Error(data.substring(0, 500)));
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

        // Focus on the problematic receipt
        const target = '2407f78f6c62d1d0a522f9e2e9a90aa2.jpg';
        
        console.log(`=== ${target} (accurate_basic) ===`);
        try {
            const r1 = await recognizeImage(token, target, 'accurate_basic');
            if (r1.words_result) {
                console.log(r1.words_result.map(w => w.words).join('\n'));
            } else {
                console.log(JSON.stringify(r1));
            }
        } catch(e) { console.error('Error:', e.message); }
        
        await new Promise(r => setTimeout(r, 1000));
        
        console.log(`\n=== ${target} (general) ===`);
        try {
            const r2 = await recognizeImage(token, target, 'general_basic');
            if (r2.words_result) {
                console.log(r2.words_result.map(w => w.words).join('\n'));
            } else {
                console.log(JSON.stringify(r2));
            }
        } catch(e) { console.error('Error:', e.message); }
        
        await new Promise(r => setTimeout(r, 1000));
        
        // Also try the 3bdcd9 receipt which had 1122
        const target2 = '3bdcd943a8f4d279aeb0e7adf430f733.jpg';
        console.log(`\n=== ${target2} (accurate_basic) ===`);
        try {
            const r3 = await recognizeImage(token, target2, 'accurate_basic');
            if (r3.words_result) {
                console.log(r3.words_result.map(w => w.words).join('\n'));
            } else {
                console.log(JSON.stringify(r3));
            }
        } catch(e) { console.error('Error:', e.message); }
        
    } catch (err) {
        console.error('Fatal:', err.message);
    }
})();
