package main

import (
    "os"
    "fmt"
    "log"
    "github.com/robfig/cron"
    cp "github.com/ninjadotorg/handshake-cryptosign/event/cron"
    "github.com/ninjadotorg/handshake-cryptosign/event/config"
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
 
    fmt.Println("Start cron")
    appCron := cron.New()
    // 
    appCron.AddFunc("@every 20s", func() {
        fmt.Println("scan tx every 20s")
        go cp.ScanTx()
    })
    appCron.AddFunc("@every 1m", func() {
        fmt.Println("sync tx every 1m")
        go cp.SyncTx()
    })
    appCron.Start()
    // loop forever
    select {}

    // for debug alone
    //cp.ScanTx()
    //cp.SyncTx()
}
