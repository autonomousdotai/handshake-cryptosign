package models

type Tx struct {
	Hash            string `gorm:"column:hash;" json:"hash"`
	ContractAddress string `gorm:"column:contract_address;" json:"contract_address"`
	ContractMethod  string `gorm:"column:contract_method;" json:"contract_method"`
	Payload         string `gorm:"column:payload;" json:"payload"`
	Status          int    `gorm:"column:status;default:-1;" json:"status"`
	ChainID         int    `gorm:"column:chain_id;default:4;" json:"chain_id"`
	Offchain        string `gorm:"column:offchain;" json:"offchain"`
}

func (u Tx) TableName() string {
	return "tx"
}
