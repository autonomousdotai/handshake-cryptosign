

var http = require('http');
var https = require('https');
// import { request as httpRequest, IncomingMessage } from 'http';
// import { request as httpsRequest } from 'https';

const request = (params) => {
    console.log(params);
    return new Promise((resolve, reject) => {
        const postData = JSON.stringify(params.data) || '';
        let headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Content-Length': Buffer.byteLength(postData, 'utf8')
        };

        if (params.headers) {
        headers = Object.assign(headers, params.headers);
        }

        let options = {
        hostname: params.hostname,
        path: params.path,
        method: params.method,
        rejectUnauthorized: params.rejectUnauthorized || false,
        headers: headers
        };

        if (params.port !== undefined) {
            options = { ...options, port: params.port };
            options.hostname = options.hostname.replace(/:.*$/, '');
        }

        const r = (params.isHttps ? https : http).request(options, (response) => {
        response.setEncoding('utf-8');
        let responseString = '';

        response.on('data', function (data) {
            responseString += data;
        });

        response.on('end', function () {
            if (response.statusCode !== 200) {
                return resolve({
                    status_code: response.statusCode
                });
            }
            let resultObject;
            try {
                resultObject = JSON.parse(responseString) || {};
            } catch (ex) {
                resultObject = {};
            }
            resultObject.status_code = response.statusCode;

            if (!resultObject || (!Array.isArray(resultObject.error) ? resultObject.error : resultObject.error.length)) {
                console.error('Result response error');
                return reject(resultObject.error);
            } else {
                return resolve(resultObject);
            }
        });
        });
        r.on('error', function (e) {
            return reject(e);
        });

        r.write(postData);
        r.end();
    });
};

module.exports = { request };
