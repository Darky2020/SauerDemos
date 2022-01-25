// Source: https://github.com/sauerbraten/discordauth/blob/master/pkg/auth/auth.go

package main

import (
	"C"
	"log"
	"crypto/elliptic"
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"math/big"
)

type PrivateKey []byte

func ParsePrivateKey(s string) (PrivateKey, error) {
	return hex.DecodeString(s)
}

func (k PrivateKey) String() string {
	return hex.EncodeToString(k)
}

type PublicKey struct {
	x *big.Int
	y *big.Int
}

func ParsePublicKey(s string) (PublicKey, error) {
	x, y, err := parsePoint(s)
	return PublicKey{
		x: x,
		y: y,
	}, err
}

func (k PublicKey) String() string {
	return encodePoint(k.x, k.y)
}

func (k PublicKey) MarshalJSON() ([]byte, error) {
	return json.Marshal(k.String())
}

func (k *PublicKey) UnmarshalJSON(data []byte) error {
	var proxy string
	err := json.Unmarshal(data, &proxy)
	if err != nil {
		return err
	}
	pub, err := ParsePublicKey(proxy)
	k.x, k.y = pub.x, pub.y
	return err
}

var p192 *elliptic.CurveParams

func init() {
	p192 = &elliptic.CurveParams{Name: "P-192", BitSize: 192}
	p192.P, _ = new(big.Int).SetString("6277101735386680763835789423207666416083908700390324961279", 10)
	p192.N, _ = new(big.Int).SetString("6277101735386680763835789423176059013767194773182842284081", 10)
	p192.B, _ = new(big.Int).SetString("64210519e59c80e70fa7e9ab72243049feb8deecc146b9b1", 16)
	p192.Gx, _ = new(big.Int).SetString("188da80eb03090f67cbf20eb43a18800f4ff0afd82ff1012", 16)
	p192.Gy, _ = new(big.Int).SetString("07192b95ffc8da78631011ed6b24cdd573f977a11e794811", 16)
}

func GenerateKeyPair() (priv PrivateKey, pub PublicKey, err error) {
	priv, pub.x, pub.y, err = elliptic.GenerateKey(p192, rand.Reader)
	return
}

func GenerateChallenge(pub PublicKey) (challenge, solution string, err error) {
	secret, x, y, err := elliptic.GenerateKey(p192, rand.Reader)
	if err != nil {
		return "", "", fmt.Errorf("generating challenge: %w", err)
	}

	// what we send to the client
	challenge = encodePoint(x, y)

	// what the client should return if she applies her private key to the challenge
	// (see Solve below)
	solX, _ := p192.ScalarMult(pub.x, pub.y, secret)
	solution = solX.Text(16)

	return
}

//export Solve
func Solve(challenge *C.char, key *C.char) (*C.char) {
	x, y, err := parsePoint(C.GoString(challenge))
	if err != nil {
		return C.CString("")
	}
	priv, error := ParsePrivateKey(C.GoString(key))
	if error != nil {
		log.Println("c ", error)
		return C.CString("")
	}
	solX, _ := p192.ScalarMult(x, y, priv)
	return C.CString(solX.Text(16))
}

// from ecjacobian::print() in shared/crypto.cpp
func encodePoint(x, y *big.Int) (s string) {
	if y.Bit(0) == 1 {
		s += "-"
	} else {
		s += "+"
	}
	s += x.Text(16)
	return
}

func parsePoint(s string) (x, y *big.Int, err error) {
	if len(s) < 1 {
		return nil, nil, errors.New("auth: could not parse curve point: too short")
	}

	var ok bool
	x, ok = new(big.Int).SetString(s[1:], 16)
	if !ok {
		return nil, nil, errors.New("auth: could not set X coordinate of curve point")
	}

	// the next steps find y using the formula y^2 = x^3 - 3*x + B
	// x^3
	xxx := new(big.Int).Mul(x, x)
	xxx.Mul(xxx, x)
	// 3*x
	threeX := new(big.Int).Add(x, x)
	threeX.Add(threeX, x)
	// x^3 - 3*x + B
	yy := new(big.Int).Sub(xxx, threeX)
	yy.Add(yy, p192.B)

	// find a square root
	y = new(big.Int).ModSqrt(yy, p192.P)

	if s[0] == '-' && y.Bit(0) == 0 {
		y.Sub(p192.P, y)
	}

	return
}

func main() {

}