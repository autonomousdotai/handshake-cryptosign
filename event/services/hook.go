package services

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"net/url"
	"strings"

	"github.com/ninjadotorg/handshake-cryptosign/event/config"
)

// HookService : struct
type HookService struct{}

// Event : send data to logic server
func (h HookService) Event(jsonData map[string]interface{}) error {
	conf := config.GetConfig()

	endpoint := conf.GetString("hookEndpoint")
	endpoint = fmt.Sprintf("%s/event", endpoint)
	jsonValue, _ := json.Marshal(jsonData)

	request, _ := http.NewRequest("POST", endpoint, bytes.NewBuffer(jsonValue))
	request.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	response, err := client.Do(request)
	if err != nil {
		log.Println(err.Error())
		return err
	}

	b, _ := ioutil.ReadAll(response.Body)

	var data map[string]interface{}
	json.Unmarshal(b, &data)

	status, ok := data["status"]
	message, hasMessage := data["message"]

	if ok && status.(float64) > 0 {
		return nil
	} else {
		errStr := "Unknown"
		if hasMessage {
			errStr = message.(string)
		}
		return errors.New(errStr)
	}
}

// PostSlack : remind me to report outcome
func (h HookService) PostSlack(msg string) {
	conf := config.GetConfig()
	endpoint := "https://slack.com/api/chat.postMessage"
	channel := conf.GetString("slack_channel")
	token := conf.GetString("slack_token")

	data := url.Values{}
	data.Set("channel", channel)
	data.Set("text", msg)
	data.Set("token", token)

	req, _ := http.NewRequest("POST", endpoint, strings.NewReader(data.Encode()))
	req.Header.Add("Content-Type", "application/x-www-form-urlencoded")

	client := &http.Client{}
	resp, _ := client.Do(req)
	fmt.Println(resp.Status)
}

// Event : send UserToken data
func (h HookService) UserTokenEvent(jsonData map[string]interface{}) error {
	conf := config.GetConfig()

	endpoint := conf.GetString("hookEndpoint")
	endpoint = fmt.Sprintf("%s/hook/user-token", endpoint)
	jsonValue, _ := json.Marshal(jsonData)

	request, _ := http.NewRequest("POST", endpoint, bytes.NewBuffer(jsonValue))
	request.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	response, err := client.Do(request)
	if err != nil {
		log.Println(err.Error())
		return err
	}

	b, _ := ioutil.ReadAll(response.Body)

	var data map[string]interface{}
	json.Unmarshal(b, &data)

	status, ok := data["status"]
	message, hasMessage := data["message"]

	if ok && status.(float64) > 0 {
		return nil
	} else {
		errStr := "Unknown"
		if hasMessage {
			errStr = message.(string)
		}
		return errors.New(errStr)
	}
}
