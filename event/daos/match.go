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
	err := models.Database().Preload("Outcomes").Where("match.date < ? and ? < match.date and id in ?", sec+(60*15), sec, models.Database().Table("outcome").Select("match_id").Where("outcome.hid >= 0").SubQuery()).Find(&matches).Error
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
	sec := time.Now().Unix()
	err := models.Database().Preload("Source").Where("match.id > ? and match.date > ?", matchID, sec).Find(&result).Error
	if err != nil {
		fmt.Println(err)
		return nil, err
	}

	return result, nil
}
