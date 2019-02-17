package cron

import (
	"context"
	"log"

	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/ethclient"
	"github.com/ninjadotorg/handshake-cryptosign/event/config"
)

// UserToken :
type UserToken struct {
	IsRunning bool
}

// NewUserToken :
func NewUserToken() (u UserToken) {
	u = UserToken{false}
	return
}

// ScanUserToken :
func (ut *UserToken) ScanUserToken() {
	conf := config.GetConfig()
	networkURL := conf.GetString("blockchainNetwork")

	etherClient, err := ethclient.Dial(networkURL)

	userTokens, err := userTokenDAO.GetAllPending()
	if err != nil {
		log.Println("User token error", err.Error())
		return
	}

	if len(uts) == 0 {
		log.Println("User token: empty")
	} else {
		for index := 0; index < len(userTokens); index++ {
			userTokens[index]
		}
	}
}

func (ut *UserToken) getTransacionReceipt(hash string, etherClient *ethclient.Client) (status int, error) {
	log.Printf("start scan tnxHash: %s\n", hash)
	txHash := common.HexToHash(hash)
	tx, pending, err := etherClient.TransactionByHash(context.Background(), txHash)
	if err == nil {
		if !pending {
			return -1, nil
		}
		receipt, err := etherClient.TransactionReceipt(context.Background(), txHash)
		if err != nil {
			log.Println("Scan Tx User Token: get receipt error", err.Error())
		} else {
			log.Printf("Tx User Token %s has receipt, status %d\n", transaction.Hash, receipt.Status)
			return receipt.Status, nil
		}
	} else {
		log.Printf("Tx User Token %s is pending or error occured\n", transaction.Hash)
	}
	results <- true
}
