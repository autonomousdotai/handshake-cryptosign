var express = require('express');
var cryptosignRoutes = require('./cryptosign');

module.exports = function (app) {
    app.use(function (req, res, next) {
        console.log('Time:', new Date());
        console.log('path', req.path);
        console.log('query', req.query);
        console.log('body', req.body);
        next();
    });
    var router = express.Router();
    router.get('/', (req, res) => {
        res.ok('ok!!!');
    });    

    app.use('/', router);
    app.use('/cryptosign', cryptosignRoutes);
}