package main

import (
    "context"
    "os"
    "fmt"
    "github.com/ninjadotorg/handshake-cryptosign/event/utils"
    "github.com/ethereum/go-ethereum/ethclient"
    "github.com/ethereum/go-ethereum/common"
)

func main() {
	fmt.Println("Parse hash!!!")
    
    if len(os.Args) <= 1 {
        panic("invalid hash")
    }
    
    etherClient, err := ethclient.Dial("https://mainnet.infura.io/")
    if err != nil {
        panic(err)
    }
 
    hash := os.Args[1]
    txHash := common.HexToHash(hash)

    tx, pending, err := etherClient.TransactionByHash(context.Background(), txHash)
    fmt.Println("tx", tx)
    if err == nil && !pending {
        _, inputJson := utils.DecodeTransactionInput("PredictionHandshake", common.ToHex(tx.Data()))
        fmt.Println("input", inputJson)

        receipt, _ := etherClient.TransactionReceipt(context.Background(), txHash)
        if len(receipt.Logs) > 0 {
            for _, log := range receipt.Logs {
                _, eventJson := utils.DecodeTransactionLog("PredictionHandshake_v1_1", log)
                fmt.Println("event", eventJson)
            }
        }
    } 
}
