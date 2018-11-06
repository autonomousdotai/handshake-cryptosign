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

// Remind : struct to handle remind user
type Remind struct {
	Email     string
	IsRunning bool
}

// NewRemind : creates a new Remind instance
func NewRemind(email string) (r Remind) {
	r = Remind{email, false}
	return
}

// RemindUser : loop for 15 minutes
func (r *Remind) RemindUser() {
	matches, err := matchDAO.GetAllIncomingMatches()
	if err != nil {
		log.Println("Remind user error", err.Error())
		return
	}

	fmt.Println("---->", matches)
	// if len(matches) == 0 {
	// 	log.Println("Remind user: don't have any matches")
	// } else {
	// 	for index := 0; index < len(matches); index++ {
	// 		log.Println("-- Match: ", matches[index].ID)
	// 		outcomes, err := outcomeDAO.GetAllOutcomesWithNoResult(matches[index].ID)
	// 		if err == nil {
	// 			m := make(map[int]bool)
	// 			for i := 0; i < len(outcomes); i++ {
	// 				o := outcomes[i]
	// 				if m[o.CreatedUserID] == false {
	// 					go r.fireNotification(o, matches[index])
	// 					m[o.CreatedUserID] = true
	// 				}
	// 			}
	// 		}
	// 	}
	// }

	// disputedOutcomes, err := outcomeDAO.GetAllOutcomesWithDisputeResult()
	// log.Println("disputedOutcomes: ", len(disputedOutcomes))
	// if err == nil {
	// 	for i := 0; i < len(disputedOutcomes); i++ {
	// 		o := disputedOutcomes[i]
	// 		match, err := matchDAO.GetMatchByOutcomeID(o.ID)
	// 		if err == nil {
	// 			go r.fireNotification(o, match)
	// 		}
	// 	}
	// }
}

func (r *Remind) fireNotification(outcome models.Outcome, match models.Match) {
	var m services.MailService
	var h services.HookService

	conf := config.GetConfig()
	var email string
	if outcome.CreatedUserID == 0 || outcome.Result == -3 {
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
		m.SendEmailForDisputeOutcome(email, match, outcome.Name)
	} else {
		m.SendEmailForReportingOutcome(email, match, outcome.Name)
	}

	chain := conf.GetInt("blockchainId")
	if chain != 1 /* mainnet */ {
		h.PostSlack("[Stag] Match: " + match.Name + ", Outcome: \"" + outcome.Name + "\" need your attention!")
	} else {
		h.PostSlack("[Production] Match: " + match.Name + ", Outcome: \"" + outcome.Name + "\" need your attention!")
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
