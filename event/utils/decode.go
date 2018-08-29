package utils

import (
	"fmt"
    "strings"
    "io/ioutil"
    "reflect"
    "encoding/json"
    "encoding/hex"
    "github.com/ethereum/go-ethereum/accounts/abi"
    "github.com/ethereum/go-ethereum/core/types"
)

func DecodeTransactionInput(contractName string, encodeData string) (bool, string){
    status := true
    methods := make(map[string]abi.Method)

    raw, err := ioutil.ReadFile(fmt.Sprintf("./contracts/%s.json", contractName))
    if err != nil {
        return false, err.Error()
    }
    var buildData map[string]interface{}
    json.Unmarshal(raw, &buildData)
    
    abiDef, _ := json.Marshal(buildData["abi"])

    abiInst, _ := abi.JSON(strings.NewReader(string(abiDef[:])))
 
    for _, method := range abiInst.Methods {
        methods[fmt.Sprintf("0x%s", hex.EncodeToString(method.Id()))] = method
    }

    sign := encodeData[:10]
    data, _ := hex.DecodeString(encodeData[10:])

    method, hasMethod := methods[sign]
    if !hasMethod {
        return false, "invalid hash"
    }

    payloadSize := len(method.Inputs.NonIndexed()) * 32

    if len(data) < payloadSize {
        status = false
        dataSize := len(data)
        for i := 0; i < payloadSize - dataSize; i++ {
            data = append(data, 0)
        }
    }

    values, unpackErr := method.Inputs.UnpackValues(data) 

    result := map[string]interface{}{}
    result["contract"] = contractName
    result["methodName"] = method.Name

    if unpackErr == nil {
        inputs := map[string]interface{}{}
        for i, input := range method.Inputs {
            value := values[i]
            
            if strings.HasPrefix(fmt.Sprint(input.Type), "bytes") {
                value = reflect.ValueOf(value)
                valueStr := fmt.Sprintf("%s", value)
                valueStr = strings.TrimRight(valueStr, "\x00")
                value = valueStr
            }
            inputs[input.Name] = value          
        }
        result["inputs"] = inputs
    } else {
        status = false
        result["error"] = unpackErr.Error()
    }
 
    resultJson, _ := json.Marshal(result)
    return status, string(resultJson[:])
}

func DecodeTransactionLog(contractName string, log *types.Log) (bool, string) {
    status := true
    events := make(map[string]abi.Event)

    raw, err := ioutil.ReadFile(fmt.Sprintf("./contracts/%s.json", contractName))
    if err != nil {
        return false, err.Error()
    }
    var buildData map[string]interface{}
    json.Unmarshal(raw, &buildData)
    
    abiDef, _ := json.Marshal(buildData["abi"])

    abiInst, _ := abi.JSON(strings.NewReader(string(abiDef[:])))
 
    for _, event := range abiInst.Events {
        events[fmt.Sprint(event.Id().Hex())] = event
    }

    var event abi.Event
    var hasEvent bool

    for _, topic := range log.Topics {
        event, hasEvent = events[topic.Hex()]
        if hasEvent {
            break;
        }
    }

    if !hasEvent {
        return false, "invalid hash"
    }

    values, unpackErr := event.Inputs.UnpackValues(log.Data)

    result := map[string]interface{}{}
    result["contract"] = contractName
    result["eventName"] = event.Name

    if unpackErr == nil {
        inputs := map[string]interface{}{}
        for i, input := range event.Inputs {
            value := values[i]
            
            if strings.HasPrefix(fmt.Sprint(input.Type), "bytes") {
                value = reflect.ValueOf(value)
                valueStr := fmt.Sprintf("%s", value)
                valueStr = strings.TrimRight(valueStr, "\x00")
                value = valueStr
            }
            inputs[input.Name] = value          
        }

        result["inputs"] = inputs
    } else {
        status = false
        result["error"] = unpackErr.Error()
    }
 
    resultJson, _ := json.Marshal(result)
    return status, string(resultJson[:])
}
