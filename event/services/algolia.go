package services

import (
	"fmt"

	"github.com/algolia/algoliasearch-client-go/algoliasearch"
	"github.com/ninjadotorg/handshake-cryptosign/event/config"
	"github.com/ninjadotorg/handshake-cryptosign/event/models"
)

// AlgoliaService : struct
type AlgoliaService struct{}

// Result : struct
type Result struct {
	ObjectID     int
	MatchName    string
	SourceName   string
	SourceURL    string
	CategoryName string
}

// ImportMatches : matches
func (s AlgoliaService) ImportMatches(matches []models.Match) (err error) {
	conf := config.GetConfig()

	algoliaData := conf.GetStringMapString("algolia")
	var algoliaApplicationID, algoliaAPIKey, indexName string
	for key, value := range algoliaData {
		if key == "application_id" {
			algoliaApplicationID = value
		} else if key == "api_key" {
			algoliaAPIKey = value
		} else if key == "index_name" {
			indexName = value
		}
	}

	client := algoliasearch.NewClient(algoliaApplicationID, algoliaAPIKey)
	var objects []algoliasearch.Object

	for index := 0; index < len(matches); index++ {
		m := matches[index]
		data := make(map[string]interface{})
		data["objectID"] = m.ID
		data["eventName"] = m.Name
		data["sourceName"] = m.Source.Name
		data["sourceURL"] = m.Source.URL
		objects = append(objects, data)
	}

	index := client.InitIndex(indexName)
	settings := algoliasearch.Map{
		"searchableAttributes": []string{
			"eventName",
			"sourceURL",
			"sourceName",
		},
	}
	index.SetSettings(settings)
	res, err := index.AddObjects(objects)
	fmt.Println(res)
	return err
}
