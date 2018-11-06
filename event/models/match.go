package models

// Source : model
type Source struct {
	ID   int
	Name string `gorm:"column:name;" json:"name"`
	URL  string `gorm:"column:url;" json:"url"`
}

// TableName : source
func (s Source) TableName() string {
	return "source"
}

// Match : model
type Match struct {
	ID          int
	CloseTime   int    `gorm:"column:date;" json:"date"`
	ReportTime  int    `gorm:"column:reportTime;" json:"reportTime"`
	DisputeTime int    `gorm:"column:disputeTime;" json:"disputeTime"`
	Name        string `gorm:"column:name;" json:"name"`
	Source      Source `gorm:"foreignkey:SourceID"`
	SourceID    int    `gorm:"column:source_id;" json:"source_id"`
	CategoryID  int    `gorm:"column:category_id;" json:"category_id"`
}

// TableName : match
func (m Match) TableName() string {
	return "match"
}
