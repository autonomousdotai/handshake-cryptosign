package services

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"mime/multipart"
	"net/http"

	"github.com/ninjadotorg/handshake-cryptosign/event/config"
	"github.com/ninjadotorg/handshake-cryptosign/event/models"
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
func (s MailService) SendEmailForReportingOutcome(email string, match models.Match, outcome string) {
	subject := fmt.Sprintf(`The event: %s need your reporting!`, match.Name)
	body := fmt.Sprintf(`It’s 15 min until the report window/time begins. Please report outcome: %s by using this link: <a href="www.ninja.org/report">www.ninja.org/report</a> on mobile.`, outcome)
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
func (s MailService) SendEmailForDisputeOutcome(email string, match models.Match, outcome string) {
	subject := fmt.Sprintf(`The event: %s need your resolving!`, match.Name)
	body := fmt.Sprintf(`Please report outcome: %s by using this link: <a href="www.ninja.org/resolve">www.ninja.org/resolve</a> on mobile.`, outcome)
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
