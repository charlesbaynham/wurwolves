const util = require('util');
const exec = util.promisify(require('child_process').exec);

async function resetDB() {
    const { stdout, stderr } = await exec("npm run resetdb");
    console.log(stdout);
}

module.exports = {


    'Demo test Ecosia.org': function (browser) {
        // browser
        //     .url('https://www.ecosia.org/')
        //     .waitForElementVisible('body')
        //     .assert.titleContains('Ecosia')
        //     .assert.visible('input[type=search]')
        //     .setValue('input[type=search]', 'nightwatch')
        //     .assert.visible('button[type=submit]')
        //     .click('button[type=submit]')
        //     .assert.containsText('.mainline-results', 'Nightwatch.js')
        //     .end();

        console.log("a test");
    },

    'Globals test': () => {
        console.log("Another test");
    },

    beforeEach: async (_) => {
        console.log(`beforeEach test`);
    },

    after: (_) => {
        console.log(`after test`);
    },

    afterEach: (_) => {
        console.log(`afterEach test`);
    },

    before: (_) => {
        console.log(`before test`);
    }
};
