package models

// Outcome : model
type Outcome struct {
	ID            int
	CreatedUserID int    `gorm:"column:created_user_id;" json:"created_user_id"`
	Result        int    `gorm:"column:result;" json:"result"`
	Name          string `gorm:"column:name;" json:"name"`
}

// TableName : outcome
func (u Outcome) TableName() string {
	return "outcome"
}
