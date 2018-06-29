package daos

import (
	"github.com/ninjadotorg/handshake-cryptosign/event/models"
)

type TxDAO struct{}

func (t TxDAO) GetAllPending() ([]models.Tx, error) {
	txs := []models.Tx{}
	err := models.Database().Where("hash != -1 and status = -1").Find(&txs).Error
	if err != nil {
		return nil, err
	}
	return txs, nil
}

func (t TxDAO) GetByHash(hash string) (models.Tx, error) {
	tx := models.Tx{}
	err := models.Database().Where("hash = ?", hash).First(&tx).Error
	return tx, err
}

func (t TxDAO) New(tx *models.Tx) error {
	err := models.Database().Create(tx).Error
	return err
}

func (t TxDAO) Update(tx *models.Tx) error {
	err := models.Database().Save(tx).Error
	return err
}
