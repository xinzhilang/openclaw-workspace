const Tesseract = require('tesseract.js');
const fs = require('fs');
const path = require('path');

const files = fs.readdirSync('.').filter(f => f.endsWith('.jpg')).sort();
console.log(`Found ${files.length} image files`);

async function ocrFile(file) {
    try {
        const { data } = await Tesseract.recognize(file, 'chi_sim+eng', {
            logger: m => { if (m.status === 'recognizing text') process.stdout.write(`\r${file}: ${Math.round(m.progress * 100)}%`); }
        });
        console.log(`\n=== ${file} ===`);
        console.log(data.text);
        // Save OCR text to a file
        fs.writeFileSync(file + '.txt', data.text);
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
