package services

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"

	"github.com/ninjadotorg/handshake-cryptosign/event/config"
)

// DispatcherService : struct
type DispatcherService struct{}

// UserInfo : payload
func (s DispatcherService) UserInfo(payload string) (bool, map[string]interface{}) {
	conf := config.GetConfig()
	endpoint := conf.GetString("dispatcher")
	endpoint = fmt.Sprintf("%s/user/profile", endpoint)

	request, _ := http.NewRequest("GET", endpoint, nil)
	request.Header.Set("Payload", payload)

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
	result, _ := data["data"]

	if ok && int(status.(float64)) == 1 {
		return true, result.(map[string]interface{})
	}

	return false, nil
}
