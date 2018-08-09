package cron

import (
	"fmt"
	"log"
	"reflect"

	"github.com/ninjadotorg/handshake-cryptosign/event/config"
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
	for index := 0; index < len(matches); index++ {
		outcomes, err := outcomeDAO.GetAllOutcomesWithNoResult(matches[index].MatchID)
		if err == nil {
			if len(outcomes) > 0 {
				r.fireNotification(outcomes)
			}
		}
	}
}

func (r *Remind) fireNotification(outcomes []models.Outcome) {
	var ids []int
	for index := 0; index < len(outcomes); index++ {
		o := outcomes[index]
		fmt.Println(o)
		exist, _ := inArray(o.CreatedUserID, ids)
		if !exist {
			ids = append(ids, o.CreatedUserID)
		}
	}

	var m services.MailService
	for index := 0; index < len(ids); index++ {
		if ids[index] == 0 {
			conf := config.GetConfig()
			go m.SendReminderEmail(conf.GetString("email"))
		}

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
