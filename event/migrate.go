package main

import (
	"github.com/jinzhu/gorm"
	"github.com/ninjadotorg/handshake-cryptosign/event/config"
	"github.com/ninjadotorg/handshake-cryptosign/event/models"
)

func main() {
	config.Init()

	//
	var db *gorm.DB = models.Database()
	defer db.Close()

	db.AutoMigrate(&models.Tx{})
	db.AutoMigrate(&models.Setting{})
}
