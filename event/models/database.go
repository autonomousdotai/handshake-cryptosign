package models

import (
	"log"

	"github.com/jinzhu/gorm"
	"github.com/ninjadotorg/handshake-cryptosign/event/config"
)

var dbInst *gorm.DB

func Database() *gorm.DB {
	if dbInst == nil {
		conf := config.GetConfig()
		d, err := gorm.Open("mysql", conf.GetString("db"))

		d.LogMode(false)

		if err != nil {
			log.Println(err)
			return nil
		}

		dbInst = d.Set("gorm.save_associations", false)
		dbInst.DB().SetMaxOpenConns(20)
		dbInst.DB().SetMaxIdleConns(10)
	}
	return dbInst
}
