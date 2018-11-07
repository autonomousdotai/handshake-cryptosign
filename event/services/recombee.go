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
type RecombeeService struct{}

// Item : struct
type Item struct {
	MatchID    int
	Name       string
	Tags       []string
	SourceID   int
	CategoryID int
}

// ImportMatches : matches
func (s RecombeeService) ImportMatches(matches []models.Match) (err error) {
	conf := config.GetConfig()

	recombeeData := conf.GetStringMapString("recombee")
	var recombeeDB, recombeeKey, recombeeHost string
	for key, value := range recombeeData {
		if key == "db_name" {
			recombeeDB = value
		} else if key == "key" {
			recombeeKey = value
		} else if key == "endpoint" {
			recombeeHost = value
		}
	}

	for index := 0; index < len(matches); index++ {
		m := matches[index]
		jsonData := make(map[string]interface{})
		jsonData["name"] = m.Name
		jsonData["sourceID"] = m.SourceID
		jsonData["categoryID"] = m.CategoryID
		jsonData["closeTime"] = m.CloseTime
		jsonData["!cascadeCreate"] = true
		jsonValue, _ := json.Marshal(jsonData)

		// Request to Recombee
		hmacTimestamp := time.Now().UnixNano() / int64(time.Second) // time.Millisecond
		url := fmt.Sprintf("/%s/items/%d?%s", recombeeDB, m.ID, fmt.Sprintf("%s%d", "hmac_timestamp=", hmacTimestamp))
		hmacSign := utils.ComputeSHA1(url, recombeeKey)
		url = fmt.Sprintf("%s&hmac_sign=%s", url, hmacSign)
		endpoint := fmt.Sprintf("%s%s", recombeeHost, url)

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
