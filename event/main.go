package main

import (
	"fmt"
	"log"
	"os"
	"time"

	"github.com/ninjadotorg/handshake-cryptosign/event/config"
	cp "github.com/ninjadotorg/handshake-cryptosign/event/cron"
	"github.com/robfig/cron"
)

func main() {
	// config Logger
	logFile, err := os.OpenFile("logs/log.txt", os.O_CREATE|os.O_APPEND|os.O_RDWR, 0666)
	if err != nil {
		panic(err)
	}
	defer logFile.Close()
	log.SetOutput(logFile) // You may need this
	log.SetFlags(log.Lshortfile | log.LstdFlags)

	// config
	config.Init()

	// parse contracts
	c := config.GetConfig()
	mapContracts := c.GetStringMapString("contracts")
	for key, value := range mapContracts {
		fmt.Printf("Start cron %s: %s \n", key, value)

		cr := cp.NewCron(value, key)
		appCron := cron.New()
		appCron.AddFunc("@every 15s", func() {
			fmt.Println("scan tx every 15s")
			if !cr.ScanRunning {
				cr.ScanRunning = true
				cr.ScanTx()
				cr.ScanRunning = false
			} else {
				fmt.Println("scan is running")
			}
		})
		appCron.AddFunc("@every 5m", func() {
			fmt.Println("sync tx every 5m")
			if !cr.SyncRunning {
				cr.SyncRunning = true
				cr.SyncTx()
				cr.SyncRunning = false
			} else {
				fmt.Println("sync is running")
			}
		})

		appCron.Start()
		time.Sleep(time.Second * 1)
	}

	appCron := cron.New()
	remind := cp.NewRemind(c.GetString("email"))
	appCron.AddFunc("@every 15m", func() {
		fmt.Println("remind user run every 15m")
		if !remind.IsRunning {
			remind.IsRunning = true
			remind.RemindUser()
			remind.IsRunning = false
		} else {
			fmt.Println("remind is running")
		}
	})
	appCron.Start()

	// Add algolia job
	algoliaCron := cron.New()
	algolia := cp.NewAlgoliaJob()
	algoliaCron.AddFunc("@every 15m", func() {
		fmt.Println("algolia run every 15m")
		if !algolia.IsRunning {
			algolia.IsRunning = true
			algolia.ScanAllMatches()
			algolia.IsRunning = false
		} else {
			fmt.Println("algolia is running")
		}
	})
	algoliaCron.Start()

	userTokenCron := cron.New()
	userToken := cp.NewUserToken()
	userTokenCron.AddFunc("@every 10s", func() {
		fmt.Println("user token run every 15m")
		if !userToken.IsRunning {
			userToken.IsRunning = true
			userToken.ScanUserToken()
			userToken.IsRunning = false
		} else {
			fmt.Println("user token is running")
		}
	})
	userTokenCron.Start()

	// loop forever
	select {}
}
