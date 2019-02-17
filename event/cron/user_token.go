package cron

import (
	"context"
	"encoding/json"
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

	if len(userTokens) == 0 {
		log.Println("User token: empty")
	} else {
		for index := 0; index < len(userTokens); index++ {
			pending, status, err := ut.getTransacionReceipt(userTokens[index].Hash, etherClient)
			if err != nil || pending {
				return
			}

			var jsonData map[string]interface{}
			json.Unmarshal([]byte(`{}`), &jsonData)
			jsonData["eventName"] = "user_token"
			jsonData["id"] = userTokens[index].ID
			jsonData["status"] = int(status)

			err = hookService.Event(jsonData)
			if err != nil {
				log.Println("Hook User Token event success error: ", err.Error())
			}
		}
	}
}

func (ut *UserToken) getTransacionReceipt(hash string, etherClient *ethclient.Client) (bool, uint64, error) {
	log.Printf("start scan tnxHash: %s\n", hash)
	txHash := common.HexToHash(hash)
	_, pending, err := etherClient.TransactionByHash(context.Background(), txHash)

	if pending {
		return false, 0, nil
	}

	if err == nil {
		receipt, err := etherClient.TransactionReceipt(context.Background(), txHash)
		if err != nil {
			log.Println("Scan Tx User Token: get receipt error", err.Error())
			return false, receipt.Status, err
		}

		log.Printf("Tx User Token %s has receipt, status %d\n", hash, receipt.Status)
		return false, receipt.Status, nil
	}

	log.Printf("Tx User Token %s is pending or error occured\n", hash)
	return false, 0, err
}
