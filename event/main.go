package main

import (
    "log"
    "github.com/robfig/cron"
    cp "github.com/ninjadotorg/handshake-cryptosign/event/cron"
)

func main() {
    // config Logger
    logFile, err := os.OpenFile("logs/log.txt", os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0600)
    if err != nil {
        panic(err)
    }
    gin.DefaultWriter = io.MultiWriter(logFile, os.Stdout)
    log.SetOutput(gin.DefaultWriter) // You may need this
    log.SetFlags(log.Lshortfile | log.LstdFlags)

    log.Println("Start cron")
    appCron := cron.New()
    // 
    appCron.AddFunc("@every 20s", func() {
        log.Println("scan tx every 20s")
        cp.ScanTx()
    })
    appCron.AddFunc("@every 1m", func() {
        log.Println("sync tx every 1m")
        cp.SyncTx()
    })
    appCron.Start()
    // loop forever
    select {}
}
