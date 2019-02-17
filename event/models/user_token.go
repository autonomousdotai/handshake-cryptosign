package models

type UserToken struct {
	ID      int
	UserID  int    `gorm:"column:user_id;" json:"user_id"`
	TokenID int    `gorm:"column:token_id;" json:"token_id"`
	Status  int    `gorm:"column:status;default:-1;" json:"status"`
	Hash    string `gorm:"column:hash;" json:"hash"`
	Address string `gorm:"column:address;" json:"address"`
}

func (u Tx) TableName() string {
	return "user_token"
}
