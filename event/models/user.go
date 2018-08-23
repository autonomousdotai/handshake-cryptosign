package models

// User : model
type User struct {
	UserID  int    `gorm:"column:id;" json:"id"`
	Email   int    `gorm:"column:email;" json:"email"`
	Payload string `gorm:"column:payload;" json:"payload"`
}

// TableName : user
func (u User) TableName() string {
	return "user"
}
