package cron

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func Test_ContractJSON(t *testing.T) {
	cr := NewCron("predictionHandshake", "0x123")
	actual := cr.contractJSON()
	expected := ""

	assert.Equal(t, actual, expected)

	cr = NewCron("predictionhandshakeaddress", "0x123")
	actual = cr.contractJSON()
	expected = "PredictionHandshake"

	assert.Equal(t, actual, expected)

	cr = NewCron("tokenregistryaddress", "0x123")
	actual = cr.contractJSON()
	expected = "TokenRegistry"

	assert.Equal(t, actual, expected)

	cr = NewCron("predictionhandshakewithtokenaddress", "0x123")
	actual = cr.contractJSON()
	expected = "PredictionHandshakeWithToken"

	assert.Equal(t, actual, expected)
}

func Test_NewCron(t *testing.T) {
	cr := NewCron("predictionHandshake", "0x123")
	assert.Equal(t, cr.ContractName, "predictionHandshake")
	assert.Equal(t, cr.ContractAddress, "0x123")
}
