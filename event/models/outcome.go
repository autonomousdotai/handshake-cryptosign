package models

// Outcome : model
type Outcome struct {
	OutcomeID int `gorm:"column:id;" json:"id"`
}

// TableName : outcome
func (u Outcome) TableName() string {
	return "outcome"
}
