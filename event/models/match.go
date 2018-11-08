package models

// Source : model
type Source struct {
	ID   int
	Name string `gorm:"column:name;" json:"name"`
	URL  string `gorm:"column:url;" json:"url"`
}

type Category struct {
	ID   int
	Name string `gorm:"column:name;" json:"name"`
}

// TableName : source
func (s Source) TableName() string {
	return "source"
}

// Match : model
type Match struct {
	ID          int
	CloseTime   int       `gorm:"column:date;" json:"date"`
	ReportTime  int       `gorm:"column:reportTime;" json:"reportTime"`
	DisputeTime int       `gorm:"column:disputeTime;" json:"disputeTime"`
	Name        string    `gorm:"column:name;" json:"name"`
	Source      Source    `gorm:"foreignkey:SourceID"`
	SourceID    int       `gorm:"column:source_id;" json:"source_id"`
	Category    Category  `gorm:"foreignkey:CategoryID"`
	CategoryID  int       `gorm:"column:category_id;" json:"category_id"`
	OutcomeName string    `gorm:"column:name;" json:"outcome_name"`
	EventName   string    `gorm:"column:name;" json:"event_name"`
	Outcomes    []Outcome `gorm:"foreignkey:MatchID"`
}

// TableName : match
func (m Match) TableName() string {
	return "match"
}
