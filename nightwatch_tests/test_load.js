const util = require('util');
const exec = util.promisify(require('child_process').exec);

var test = 123;
var proc;

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

        console.log(`during Test = ${test}`);
        test += 1;
    },

    'Globals test': () => {
        console.log(`during Test = ${test}`);
        test += 1;
    },

    beforeEach: async (_) => {
        // const { stdout, stderr } = await exec("ls -la");
        // console.log(stdout);
        console.log(`beforeEach test = ${test}`);
        test += 1;
    },

    after: (_) => {
        console.log(`after Test = ${test}`);
        test += 1;
        proc.kill();
    },

    afterEach: (_) => {
        console.log(`afterEach Test = ${test}`);
        test += 1;
    },

    before: (_) => {
        console.log(`first before Test = ${test}`);
        test += 1;

        proc = require('child_process').spawn('npm run dev');
    }
};
