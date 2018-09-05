package cron

import (
	"fmt"
	"log"
	"reflect"

	"github.com/ninjadotorg/handshake-cryptosign/event/config"
	"github.com/ninjadotorg/handshake-cryptosign/event/daos"
	"github.com/ninjadotorg/handshake-cryptosign/event/models"
	"github.com/ninjadotorg/handshake-cryptosign/event/services"
)

// RemindUser : loop for 15 minutes
func (r *Remind) RemindUser() {
	matches, err := matchDAO.GetAllIncomingMatches()
	if err != nil {
		log.Println("Remind user error", err.Error())
		return
	}
	if len(matches) == 0 {
		log.Println("Remind user: don't have any matches")
		return
	}

	log.Println("matches: ", len(matches))
	for index := 0; index < len(matches); index++ {
		log.Println("-- Match: ", matches[index].MatchID)
		outcomes, _ := outcomeDAO.GetAllOutcomesWithNoResult(matches[index].MatchID)
		fmt.Println(outcomes)
		if err == nil {
			for i := 0; i < len(outcomes); i++ {
				o := outcomes[i]
				go r.fireNotification(o)
			}
		}
	}
}

func (r *Remind) fireNotification(outcome models.Outcome) {
	var m services.MailService
	var h services.HookService

	conf := config.GetConfig()
	var email string
	if outcome.CreatedUserID == 0 {
		email = conf.GetString("email")
	} else {
		var d services.DispatcherService
		var u daos.UserDAO
		user, err := u.FindUserByID(outcome.CreatedUserID)
		if err != nil {
			fmt.Println("cannot find user")
			return
		}
		result, data := d.UserInfo(user.Payload)
		if result {
			email = data["email"].(string)
		} else {
			fmt.Println("cannot get user info")
			return
		}
	}

	if outcome.Result == -3 {
		m.SendEmailForDisputeOutcome(email, outcome.Name)
	} else {
		m.SendEmailForReportingOutcome(email, outcome.Name)
	}

	chain := conf.GetInt("blockchainId")
	if chain == 4 {
		h.PostSlack("[Stag] Outcome: \"" + outcome.Name + "\" need your attention!")
	} else {
		h.PostSlack("[Production] Outcome: \"" + outcome.Name + "\" need your attention!")
	}

}

func inArray(val interface{}, array interface{}) (exists bool, index int) {
	exists = false
	index = -1

	switch reflect.TypeOf(array).Kind() {
	case reflect.Slice:
		s := reflect.ValueOf(array)

		for i := 0; i < s.Len(); i++ {
			if reflect.DeepEqual(val, s.Index(i).Interface()) == true {
				index = i
				exists = true
				return
			}
		}
	}

	return
}
