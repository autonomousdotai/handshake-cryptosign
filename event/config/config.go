package config

import (
	"log"

	"github.com/spf13/viper"
)

var config *viper.Viper

func Init() {
	var err error
	v := viper.New()
	v.SetConfigType("yaml")
	v.SetConfigName("conf")
	v.AddConfigPath("../config/")
	v.AddConfigPath("config/")
	err = v.ReadInConfig()
	if err != nil {
		log.Fatal("Error on parsing configuration file.")
	}
	config = v
}

func GetConfig() *viper.Viper {
	return config
}
