package services

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"github.com/ninjadotorg/handshake-cryptosign/event/config"
	"github.com/ninjadotorg/handshake-cryptosign/event/models"
	"github.com/ninjadotorg/handshake-cryptosign/event/utils"
)

// RecombeeService : struct
type RecombeeService struct {
	dbName     string
	dbKey      string
	dbEndpoint string
}

// ImportMatches : matches
func (recombee RecombeeService) ImportMatches(matches []models.Match) (err error) {

	if recombee.dbName == "" || recombee.dbKey == "" || recombee.dbEndpoint == "" {
		recombee.loadConfigs()
	}

	for index := 0; index < len(matches); index++ {
		m := matches[index]
		jsonData := make(map[string]interface{})
		jsonData["name"] = m.Name
		jsonData["sourceID"] = m.SourceID
		jsonData["sourceName"] = m.Source.Name
		jsonData["categoryID"] = m.CategoryID
		jsonData["categoryName"] = m.Category.Name
		jsonData["closeTime"] = m.CloseTime
		jsonData["OutcomeName"] = m.OutcomeName
		jsonData["EventName"] = m.Category.Name
		jsonData["!cascadeCreate"] = true
		jsonValue, _ := json.Marshal(jsonData)

		// Request to Recombee
		hmacTimestamp := time.Now().UnixNano() / int64(time.Second) // time.Millisecond
		url := fmt.Sprintf("/%s/items/%d?%s", recombee.dbName, m.ID, fmt.Sprintf("%s%d", "hmac_timestamp=", hmacTimestamp))
		hmacSign := utils.ComputeSHA1(url, recombee.dbKey)
		url = fmt.Sprintf("%s&hmac_sign=%s", url, hmacSign)
		endpoint := fmt.Sprintf("%s%s", recombee.dbEndpoint, url)

		request, _ := http.NewRequest("POST", endpoint, bytes.NewBuffer(jsonValue))
		request.Header.Set("Content-Type", "application/json")

		client := &http.Client{}
		_, err := client.Do(request)
		if err != nil {
			fmt.Println(err.Error())
		} else {
			fmt.Println("POST to Recombee success.")
		}
	}
	return nil
}

func (recombee *RecombeeService) loadConfigs() {
	conf := config.GetConfig()

	recombeeData := conf.GetStringMapString("recombee")
	for key, value := range recombeeData {
		if key == "db_name" {
			recombee.dbName = value
		} else if key == "key" {
			recombee.dbKey = value
		} else if key == "endpoint" {
			recombee.dbEndpoint = value
		}
	}
}
