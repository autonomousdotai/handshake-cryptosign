package daos

import (
	"testing"

	"github.com/ninjadotorg/handshake-cryptosign/event/models"
)

func Test_GetAllIncomingMatches(t *testing.T) {
	models.Database().Update(&models.Match{MatchID: 1, CloseTime: 1000, Name: ""})
}
