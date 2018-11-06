package utils

import (
	"crypto/hmac"
	"crypto/sha1"
	"crypto/sha256"
	"encoding/base64"
	"encoding/hex"
)

// ComputeSHA1 :
func ComputeSHA1(message string, secret string) string {
	key := []byte(secret)
	signature := hmac.New(sha1.New, []byte(key))
	signature.Write([]byte(message))
	return hex.EncodeToString(signature.Sum(nil))
}

// ComputeHmac256 :
func ComputeHmac256(message string, secret string) string {
	key := []byte(secret)
	h := hmac.New(sha256.New, key)
	h.Write([]byte(message))
	return base64.StdEncoding.EncodeToString(h.Sum(nil))
}
