package models

// Outcome : model
type Outcome struct {
	OutcomeID     int    `gorm:"column:id;" json:"id"`
	CreatedUserID int    `gorm:"column:created_user_id;" json:"created_user_id"`
	Result        int    `gorm:"column:result;" json:"result"`
	Name          string `gorm:"column:name;" json:"name"`
}

// TableName : outcome
func (u Outcome) TableName() string {
	return "outcome"
}
