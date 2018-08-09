package cron

import (
	"log"
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

			}
		}
	}
}

func (r *Remind) fireNotification(emails []string) {

}
