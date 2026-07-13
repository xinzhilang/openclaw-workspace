const Tesseract = require('tesseract.js');
const fs = require('fs');
const path = require('path');

const files = fs.readdirSync('.').filter(f => f.endsWith('.jpg')).sort();

async function ocrFile(file) {
    try {
        const { data } = await Tesseract.recognize(file, 'eng', {
            logger: m => {}
        });
        console.log(`\n=== ${file} ===`);
        console.log(data.text.substring(0, 2000));
        fs.writeFileSync(file + '.ocr.txt', data.text);
    } catch (err) {
        console.error(`\n${file}: ERROR - ${err.message}`);
    }
}

(async () => {
    for (const f of files) {
        await ocrFile(f);
    }
    console.log('\nDone!');
})();
