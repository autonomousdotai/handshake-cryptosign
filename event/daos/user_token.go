package daos

import (
	"github.com/ninjadotorg/handshake-cryptosign/event/models"
)

type UserTokenDAO struct{}

func (u UserTokenDAO) GetAllPending() ([]models.UserToken, error) {
	uts := []models.UserToken{}
	err := models.Database().Where("hash != -1 and status = -1").Find(&uts).Error
	if err != nil {
		return nil, err
	}
	return uts, nil
}

func (u UserTokenDAO) GetByHash(hash string) (models.UserToken, error) {
	ut := models.UserToken{}
	err := models.Database().Where("hash = ?", hash).First(&ut).Error
	return ut, err
}

func (u UserTokenDAO) New(ut *models.UserToken) error {
	err := models.Database().Create(ut).Error
	return err
}

func (u UserTokenDAO) Update(ut *models.UserToken) error {
	err := models.Database().Save(ut).Error
	return err
}
