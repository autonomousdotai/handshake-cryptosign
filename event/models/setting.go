package models

type Setting struct {
	Name   string `gorm:"column:name;" json:"name"`
	Value  string `gorm:"column:value;" json:"contravaluect_address"`
	Status int    `gorm:"column:status;default:-1;" json:"status"`
}

func (u Setting) TableName() string {
	return "setting"
}
