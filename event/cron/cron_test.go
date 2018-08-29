package cron

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func Test_NewCron(t *testing.T) {
	cr := NewCron("predictionHandshake", "0x123")
	assert.Equal(t, cr.ContractJSON, "predictionHandshake")
	assert.Equal(t, cr.ContractAddress, "0x123")
}
