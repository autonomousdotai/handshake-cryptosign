package daos

import (
	"github.com/ninjadotorg/handshake-cryptosign/event/models"
)

// UserDAO : DAO
type UserDAO struct{}

// FindUserByID : uid
func (m UserDAO) FindUserByID(uID int) (models.User, error) {
	user := models.User{}
	err := models.Database().Where("user.id = ?", uID).Find(&user).Error
	return user, err
}
