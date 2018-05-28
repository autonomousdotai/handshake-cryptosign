const cron = require('node-cron');
const configs = require('./configs');
const constants = require('./constants');
const axios = require('axios');
// models
const models = require('./models');
// daos
const txDAO = require('./daos/tx');
// Add the web3 node module
const Web3 = require('web3');
// mark as running
let isRunning = false;

const allEvents = [
  'BasicHandshake.__init',
  'GroupHandshake.__init',
  'BasicHandshake.__shake',
  'GroupHandshake.__shake',
  'PayableHandshake.__init',
  'PayableHandshake.__shake',
  'PayableHandshake.__unshake',
  'PayableHandshake.__deliver',
  'PayableHandshake.__withdraw',
  'PayableHandshake.__reject',
  'PayableHandshake.__accept',
  'PayableHandshake.__cancel',
];
const topics = {};

function getCompilied(contractName) {
  return require('./contracts/' + contractName + '.json');
}

function checkEventLog(log, _contractName) {
  for (var event in topics) {
    const topicSha3 = topics[event];
    if (log.topics.indexOf(topicSha3) !== -1) {
      const [contractName, eventName] = event.split('.');
      if (contractName == _contractName) {
        const compiled = getCompilied(contractName);
        let abiObj = null;
        for (var j = 0; j < compiled.abi.length; j++) {
          if (compiled.abi[j].type === 'event' && compiled.abi[j].name === eventName) {
            abiObj = compiled.abi[j];
            break;
          }
        }
        if (abiObj) {
          return {event: event, abi: abiObj};
        }
      }
    }
  }
  return false;
}

function combineEvents(callback) {
  try {
    for (var i = 0; i < allEvents.length; i++) {
      const _event = allEvents[i];
      const [contractName, eventName] = _event.split('.');

      const compiled = getCompilied(contractName);
      const abi = compiled.abi;

      for (var j = 0; j < abi.length; j++) {
        if (abi[j].type === 'event' && abi[j].name === eventName) {
          const abiObj = abi[j];
          const inputs = [];
          if (abiObj.inputs.length) {
            for (var n = 0; n < abiObj.inputs.length; n++){
              inputs.push(abiObj.inputs[n].type);
            }
          }
          const combinedEvent = eventName + '(' + inputs.join(',') + ')';
          topics[_event] = Web3.utils.sha3(combinedEvent);
          break;
        }
      }
    }
    if (callback) {
      callback();
    }
  } catch (e) {
    console.log('combine events fail');
    console.error(e);
  }
}

function runCron() {
  cron.schedule('*/30 * * * * *', async function () {
    console.log('running a task every 30s at ' + new Date());
    try {
      if (!isRunning) {
        isRunning = true;
        const transactions = await txDAO.getAllPending();
		  console.log('transactions', transactions);
        for (var i = 0; i < transactions.length; i++) {
          const transaction = transactions[i];
            console.log('model', transaction.id);
			console.log('transaction.chain_id', transaction.chain_id);
			console.log('transaction.hash', transaction.hash);
          const web3 = new Web3(new Web3.providers.HttpProvider(configs.network[transaction.chain_id].blockchainNetwork));
		  const receipt = await web3.eth.getTransactionReceipt(transaction.hash);
		  console.log('receipt', receipt);
          if (receipt) {
            console.log('has receipt');
            const events = {};
            const block = await web3.eth.getBlock(receipt.blockNumber);
            const body = {
              'txId': transaction.id,
              'txStatus': web3.utils.hexToNumber(receipt.status),
              'blockNumber': receipt.blockNumber,
              'blockTimeStamp': block.timestamp,
            }
            try {
              if (body.txStatus === 1) {
                // todo success
                const eventData = {};
                console.log('receipt logs', receipt.logs.length);
                if (receipt.logs.length > 0) {
                  for (var j = 0; j < receipt.logs.length; j++) {
                    const result = checkEventLog(receipt.logs[j], transaction.contract_name);
                    if (result) {
                      const eventData = web3.eth.abi.decodeLog(result.abi.inputs, receipt.logs[j].data, receipt.logs[j].topics);
                      if (eventData.offchain) {
                        eventData.offchain = web3.utils.toAscii(eventData.offchain).replace(/\u0000/g,'');
                      }
                      events[result.event] = eventData;
                    }
                  }
                }
              }
              body['events'] = events;
              axios.post(configs.restApiEndpoint + '/event', body)
                .then(function (response) {
                  console.log('hook success');
                })
                .catch(function (error) {
                  console.log('hook failed');
                });
            } catch (err) {
              console.error(err);
            }
          }
        }
      }
      isRunning = false;
    } catch (e) {
      isRunning = false;
      console.log('cron error');
      console.error(e);
    }
  });
}

combineEvents(runCron);

