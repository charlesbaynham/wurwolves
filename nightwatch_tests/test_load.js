const { assert } = require('console');
const util = require('util');
const exec = util.promisify(require('child_process').exec);

async function resetDB() {
    const { stdout, stderr } = await exec("npm run resetdb");
    console.log(stdout);
}

const TEST_URL = "http://localhost:3000";
const TEST_GAME = "james-doesnt-understand-prostitute"

module.exports = {
    'Basic launch': function (browser) {
        browser
            .url(TEST_URL)
            .waitForElementVisible('body')
            .assert.titleContains('Wurwolves')
    },

    'Start game': async (browser) => {
        await resetDB();

        await browser.url(TEST_URL)
        await browser.waitForElementVisible('#home-content-box button')
        await browser.click('#home-content-box button')
        const url = (await browser.url()).value

        const regex = /(\w+-\w+-\w+-\w+)/g;
        const found = url.match(regex);

        assert(found)
        console.log(`Game name: ${found}`);

    },

    'Set name': async (browser) => {

        const SAMPLE_NAME = "My name";

        await browser.url(`${TEST_URL}/${TEST_GAME}`)
        await browser.setValue('nav input', SAMPLE_NAME)
        await browser.click('body')
        await browser.assert.containsText('#playerGrid figcaption', SAMPLE_NAME)
    },
};
