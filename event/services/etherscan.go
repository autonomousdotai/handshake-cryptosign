package services

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"

	"github.com/ninjadotorg/handshake-cryptosign/event/config"
)

type EtherscanService struct{}

func (s EtherscanService) ListTransactions(address string, page int, offset int) (bool, []interface{}) {
	conf := config.GetConfig()
	endpoint := conf.GetString("etherScanEndpoint")
	apiKey := conf.GetString("etherScanKey")

	endpoint = fmt.Sprintf("%s?module=account&action=txlist&startblock=0&endblock=99999999&address=%s&page=%d&offset=%d&sort=asc&apikey=%s", endpoint, address, page, offset, apiKey)

	request, _ := http.NewRequest("GET", endpoint, nil)

	client := &http.Client{}
	response, err := client.Do(request)
	if err != nil {
		log.Println(err.Error())
		return false, nil
	}

	b, _ := ioutil.ReadAll(response.Body)

	var data map[string]interface{}
	json.Unmarshal(b, &data)

	status, ok := data["status"]
	message, _ := data["message"]
	result, _ := data["result"]

	if ok && status.(string) == "1" {
		return true, result.([]interface{})
	} else {
		log.Println(message)
		return false, nil
	}
}
