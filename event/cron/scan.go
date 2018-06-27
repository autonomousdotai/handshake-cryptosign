package cron

import (
    "log"
    "fmt"
    "context"
    "encoding/json"
    "github.com/ethereum/go-ethereum/common"
    "github.com/ethereum/go-ethereum/ethclient"
    "github.com/ninjadotorg/handshake-cryptosign/event/config"
    "github.com/ninjadotorg/handshake-cryptosign/event/utils"
)

func ScanTx() {
    // todo get list transaction pending 
    txs, err := txDAO.GetAllPending()
    if err != nil {
        log.Println("Scan Tx error", err.Error())
        return; 
    }
    if len(txs) == 0 {
        log.Println("Scan Tx: don't have any pending tx")
        return;
    }

    conf := config.GetConfig()
    networkUrl := conf.GetString("blockchainNetwork")

    etherClient, err := ethclient.Dial(networkUrl)
    if err != nil {
        log.Printf("Scan Tx: connect to network %s fail!\n", networkUrl)
        return;
    }

    // todo loop & parse transaction
    for _, tx := range txs {
        txHash := common.HexToHash(tx.Hash)
        tx, pending, err := etherClient.TransactionByHash(context.Background(), txHash)
        if err == nil && !pending {
            receipt, err := etherClient.TransactionReceipt(context.Background(), txHash)
            if err != nil {
                log.Println("Scan Tx: get receipt error", err.Error())
                continue;
            }
            if receipt.Status == 0 {
                // case fail
                _, methodJson := utils.DecodeTransactionInput("PredictionHandshake", common.ToHex(tx.Data()))
                // call REST fail
                var jsonData map[string]interface{}
                json.Unmarshal([]byte(methodJson), &methodJson)
                jsonData["status"] = 0
                err := hookService.Event(jsonData)
                if err != nil {
                    log.Println("Hook event fail error: ", err.Error())
                    log.Println(methodJson)
                }
                fmt.Println("input", methodJson)
            } else if receipt.Status == 1 {
                // case success
                if err != nil {
                    if len(receipt.Logs) > 0 {
                        for _, l := range receipt.Logs {
                            _, eventJson := utils.DecodeTransactionLog("PredictionHandshake", l)
                            fmt.Println("event", eventJson)
                            var jsonData map[string]interface{}
                            json.Unmarshal([]byte(eventJson), &jsonData)
                            jsonData["status"] = 1
                            // call REST API SUCCESS with event
                            err := hookService.Event(jsonData)
                            if err != nil {
                                log.Println("Hook event failed: ", err.Error())
                                log.Println(eventJson)
                            }
                        }
                    }
                }
            } else {
                log.Println("Unknown case", tx.Hash)
            }
        }
    }
}
