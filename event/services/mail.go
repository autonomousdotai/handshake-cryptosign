package services

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"mime/multipart"
	"net/http"

	"github.com/ninjadotorg/handshake-cryptosign/event/config"
)

// MailService : struct
type MailService struct{}

func (s MailService) send(from string, to string, subject string, content string) (success bool, err error) {
	conf := config.GetConfig()
	endpoint := conf.GetString("mail")

	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)
	part, _ := writer.CreateFormField("from")
	part.Write([]byte(from))
	part, _ = writer.CreateFormField("to[]")
	part.Write([]byte(to))
	part, _ = writer.CreateFormField("subject")
	part.Write([]byte(subject))
	part, _ = writer.CreateFormField("body")
	part.Write([]byte(content))
	writer.Close()

	request, _ := http.NewRequest("POST", endpoint, body)
	request.Header.Set("Content-Type", writer.FormDataContentType())

	client := &http.Client{}
	response, err := client.Do(request)
	if err != nil {
		fmt.Println(err.Error())
		return
	}

	b, _ := ioutil.ReadAll(response.Body)

	var data map[string]interface{}
	json.Unmarshal(b, &data)

	fmt.Println(data)
	status, _ := data["status"].(float64)
	success = status >= 1

	return
}

// SendEmailForReportingOutcome : email, outcome
func (s MailService) SendEmailForReportingOutcome(email string, outcome string) {
	subject := `There is an outcome need your reporting!`
	body := `Go to this link <a href="www.ninja.org/prediction">www.ninja.org/prediction</a> on mobile to report your outcome.`
	status, err := s.send("dojo@ninja.org", email, subject, body)

	if err != nil {
		fmt.Println(err.Error())
	}

	if !status {
		fmt.Println("Cannot send email")
	} else {
		fmt.Printf("Send email to %s successfully", email)
	}
}

// SendEmailForDisputeOutcome : email, outcome
func (s MailService) SendEmailForDisputeOutcome(email string, outcome string) {
	subject := `There is an outcome need your resolving!`
	body := `Go to this link <a href="www.ninja.org/prediction">www.ninja.org/prediction</a> on mobile to report your outcome.`
	status, err := s.send("dojo@ninja.org", email, subject, body)

	if err != nil {
		fmt.Println(err.Error())
	}

	if !status {
		fmt.Println("Cannot send email")
	} else {
		fmt.Printf("Send email to %s successfully", email)
	}
}
