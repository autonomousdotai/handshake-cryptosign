package daos

import (
	"fmt"
	"time"

	"github.com/ninjadotorg/handshake-cryptosign/event/models"
)

// MatchDAO : DAO
type MatchDAO struct{}

// GetAllIncomingMatches :
func (m MatchDAO) GetAllIncomingMatches() ([]models.Match, error) {
	matches := []models.Match{}
	sec := time.Now().Unix()
	err := models.Database().Where("match.date < ? and ? < match.date", sec+(60*15), sec).Find(&matches).Error
	if err != nil {
		fmt.Println(err)
		return nil, err
	}

	return matches, nil
}

// GetMatchByOutcomeID : outcomeID
func (m MatchDAO) GetMatchByOutcomeID(outcomeID int) (models.Match, error) {
	match := models.Match{}
	err := models.Database().Where("match.outcome_id = ?", outcomeID).Find(&match).Error
	if err != nil {
		fmt.Println(err)
		return match, err
	}

	return match, nil
}

// GetAllMatchesExceedID : matchID
func (m MatchDAO) GetAllMatchesExceedID(matchID int) ([]models.Match, error) {
	result := []models.Match{}
	err := models.Database().Preload("Source").Where("match.id > ?", matchID).Find(&result).Error
	if err != nil {
		fmt.Println(err)
		return nil, err
	}

	return result, nil
}
