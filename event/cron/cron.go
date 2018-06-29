package cron

import (
    "github.com/ninjadotorg/handshake-cryptosign/event/services"
    "github.com/ninjadotorg/handshake-cryptosign/event/daos"
)

var txDAO = &daos.TxDAO{}
var hookService = &services.HookService{}
var etherscanService = &services.EtherscanService{}
