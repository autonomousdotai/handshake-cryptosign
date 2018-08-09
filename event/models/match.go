package models

// Match : model
type Match struct {
	MatchID     int    `gorm:"column:id;" json:"id"`
	CloseTime   int    `gorm:"column:date;" json:"date"`
	ReportTime  int    `gorm:"column:reportTime;" json:"reportTime"`
	DisputeTime int    `gorm:"column:disputeTime;" json:"disputeTime"`
	Name        string `gorm:"column:name;" json:"name"`
}

// TableName : match
func (u Match) TableName() string {
	return "match"
}
