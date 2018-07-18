package models

import (
	"time"
)

type BaseModel struct {
	ID           uint      `gorm:"primary_key" json:"id"`
	DateCreated  time.Time `gorm:"column:date_created" json:"date_created"`
	DateModified time.Time `gorm:"column:date_modified" json:"date_modified"`
	Deleted      int       `gorm:"column:deleted;default:0;" json:"deleted"`
}

func (m *BaseModel) BeforeCreate() (err error) {
	m.DateCreated = time.Now().UTC()
	m.DateModified = time.Now().UTC()
	return
}

func (m *BaseModel) BeforeUpdate() (err error) {
	m.DateModified = time.Now().UTC()
	return
}
