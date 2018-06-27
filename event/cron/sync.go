package cron

import (
    "log"
    "encoding/json"
    "github.com/ninjadotorg/handshake-cryptosign/event/config"
    "github.com/ninjadotorg/handshake-cryptosign/event/utils"
    "github.com/ninjadotorg/handshake-cryptosign/event/models"
)

func SyncTx() {
    // todo call etherscan.io to get all transactions
    conf := config.GetConfig()
    predictionHandshakeAddress := conf.GetString("predictionHandshakeAddress")
   
    page := 1
    recordPerPage := 10
    for ;; {
        status, transactions := etherscanService.ListTransactions(predictionHandshakeAddress, page, recordPerPage)
        if !status {
            log.Println("etherscan.io return error")
            break;
        }
        if len(transactions) == 0 {
            break;
        }
        page = page + 1
        for _, transaction := range transactions {
            transactionObj := transaction.(map[string]interface{})
            hash := transactionObj["hash"].(string)
            input := transactionObj["input"].(string)

            _, err := txDAO.GetByHash(hash)
            if err != nil {
                _, inputJson := utils.DecodeTransactionInput("PredictionHandshakeAddress", input)
                var jsonData map[string]interface{} 
                json.Unmarshal([]byte(inputJson), &jsonData)

                offchain, hasOffchain := jsonData["offchain"]
                tx := &models.Tx{
                    Hash: hash,
                    ContractAddress: predictionHandshakeAddress,
                    ContractMethod: jsonData["methodName"].(string),
                    Payload: input,
                    ChainID: 4,
                }

                if hasOffchain {
                    tx.Offchain = offchain.(string)
                }
                err := txDAO.New(tx)
                if err != nil {
                    log.Println("Sync new transaction error", err.Error())
                }
            }
        }
    } 
}
