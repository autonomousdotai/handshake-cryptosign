
const cron = require('./cron');
setTimeout( () => {
    // cron.bettingCron.runBettingCron();
    cron.oddsCron.runOddsCron();
    // cron.createMarketCron.runCreateMarketCron();
}, 1)

var logger = require('morgan');
var bodyParser = require('body-parser');
var responseEnhancer = require('./middlewares/response-enhancer');
var express = require('express');
var app = express();
var initialRoutes = require('./routes/index');

app.use(logger('dev'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));

app.use(responseEnhancer());
initialRoutes(app)

// log error
app.use(function(err, req, res, next) {
    console.log('response log error');
    console.log(err);
    next(err);
});
// response error
app.use(function(err, req, res, next) {
    console.log('response error');
    res.notok(err);
});

// catch 404 and forward to error handler
app.use(function(req, res, next) {
    res.notok(new Error('Not found'));
});

app.listen(3000);

