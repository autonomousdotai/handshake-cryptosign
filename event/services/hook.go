package services

import (
    "log"
    "fmt"
    "bytes"
    "errors"
    "encoding/json"
    "io/ioutil"
    "net/http"
    "github.com/ninjadotorg/handshake-cryptosign/event/config"
)

type HookService struct{}

func (h HookService) Event(jsonData map[string]interface{}) (error) {
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
    message, _ := data["message"]
    
    if ok && status.(float64) > 0 {
        return nil
    } else {
        return errors.New(message.(string))
    }
}
