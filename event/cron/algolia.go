package cron

import (
	"fmt"

	"github.com/ninjadotorg/handshake-cryptosign/event/services"
)

var algoliaService = &services.AlgoliaService{}
var recombeeService = &services.RecombeeService{}

// Algolia : struct to handle pushing data
type Algolia struct {
	CurrentID int
	IsRunning bool
}

// NewAlgoliaJob : creates a new Algolia instance
func NewAlgoliaJob() (r Algolia) {
	r = Algolia{0, false}
	return
}

// ScanAllMatches : add to algolia host
func (al *Algolia) ScanAllMatches() {
	matches, err := matchDAO.GetAllMatchesExceedID(al.CurrentID)
	if err != nil {
		fmt.Println("Cannot get matches")
		return
	}

	// update current id for algolia
	m := matches[len(matches)-1]
	al.CurrentID = m.ID

	// push data to algolia
	algoliaService.ImportMatches(matches)
	recombeeService.ImportMatches(matches)
}
