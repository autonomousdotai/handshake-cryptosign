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
	err := models.Database().Where("match.date < ? and ? < match.date", sec+(60*100), sec).Find(&matches).Error
	if err != nil {
		fmt.Println(err)
		return nil, err
	}

	fmt.Println("Matches -> ", matches)
	return matches, nil
}
