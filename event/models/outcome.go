package models

// Outcome : model
type Outcome struct {
	OutcomeID     int `gorm:"column:id;" json:"id"`
	CreatedUserID int `gorm:"column:created_user_id;" json:"created_user_id"`
}

// TableName : outcome
func (u Outcome) TableName() string {
	return "outcome"
}
