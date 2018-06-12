module.exports = {
    runBettingCron: require('./cronBetting').runBettingCron(),
    runCreateMarketCron: require('./cronMarket').runCreateMarketCron(),
    runOddsCron: require('./cronOdds').runOddsCron()
};