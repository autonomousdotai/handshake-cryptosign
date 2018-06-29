package main

import (
    "os"
    "fmt"
    "log"
    "github.com/robfig/cron"
    cp "github.com/ninjadotorg/handshake-cryptosign/event/cron"
    "github.com/ninjadotorg/handshake-cryptosign/event/config"
)

type CronStatus struct {
    Scanning bool
    Syncing bool
}

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
    status := &CronStatus{false, false}
    appCron := cron.New()
    // 
    appCron.AddFunc("@every 15s", func() {
        fmt.Println("scan tx every 15s")
        if !status.Scanning {
            status.Scanning = true
            cp.ScanTx()
            status.Scanning = false
        } else {
            fmt.Println("scan is running")
        }
    })
    appCron.AddFunc("@every 5m", func() {
        fmt.Println("sync tx every 5m")
        if !status.Syncing {
            status.Syncing = true
            cp.SyncTx()
            status.Syncing = false
        } else {
            fmt.Println("sync is running")
        }
    })
    appCron.Start()
    // loop forever
    select {}

    // for debug alone
    //cp.ScanTx()
    //cp.SyncTx()
}
