const sandbox = require('sinon').createSandbox();
const myAPI = { hello: function () {} };

describe('myAPI.hello method', function () {

    before(function () { console.log("BEFORE"); });

    beforeEach(function () {
        console.log("BEFORE EACH");
        // stub out the `hello` method
        sandbox.stub(myAPI, 'hello');
    });

    afterEach(function () {
        console.log("AFTER EACH");
        // completely restore all fakes created through the sandbox
        sandbox.restore();
    });

    after(function () { console.log("AFTER"); });


    it('should be called once', function () {
        myAPI.hello();
        sandbox.assert.calledOnce(myAPI.hello);
    });

    it('should be called twice', function () {
        myAPI.hello();
        myAPI.hello();
        sandbox.assert.calledTwice(myAPI.hello);
    });
});
