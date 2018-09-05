package daos

import (
	"fmt"

	"github.com/ninjadotorg/handshake-cryptosign/event/models"
)

// OutcomeDAO : DAO
type OutcomeDAO struct{}

// GetAllOutcomesWithNoResult : matchID
func (m OutcomeDAO) GetAllOutcomesWithNoResult(matchID int) ([]models.Outcome, error) {
	outcomes := []models.Outcome{}
	err := models.Database().Where("outcome.hid >= 0 and outcome.result = -1 and outcome.match_id = ?", matchID).Find(&outcomes).Error
	if err != nil {
		fmt.Println(err)
		return nil, err
	}

	return outcomes, nil
}

// GetAllOutcomesWithDisputeResult : result = -3
func (m OutcomeDAO) GetAllOutcomesWithDisputeResult() ([]models.Outcome, error) {
	outcomes := []models.Outcome{}
	err := models.Database().Where("outcome.hid >= 0 and outcome.result = -3").Find(&outcomes).Error
	if err != nil {
		fmt.Println(err)
		return nil, err
	}

	return outcomes, nil
}
