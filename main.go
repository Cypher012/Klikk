package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net"
)

type Message struct {
	Type string `json:"type"`
	Text string `json:"text,omitempty"`
	X    int    `json:"x,omitempty"`
	Y    int    `json:"y,omitempty"`
}

func sendMessage(conn net.Conn, msg Message) error {
	data, err := json.Marshal(msg)
	if err != nil {
		return err
	}
	_, err = conn.Write(append(data, '\n'))
	return err
}

func main() {
	conn, err := connectSocket()
	if err != nil {
		log.Fatal("Error connecting: ", err)
	}
	defer conn.Close()

	// Send bubble message
	err = sendMessage(conn, Message{Type: "bubble", Text: "Hello from Go!"})
	if err != nil {
		log.Fatal(err)
	}

	// Send move message
	sendMessage(conn, Message{Type: "move", X: 500, Y: 300})

	fmt.Println("message sent!")
}

func connectSocket() (net.Conn, error) {
	conn, err := net.Dial("unix", "/tmp/aicursor.sock")
	if err != nil {
		return nil, err
	}
	return conn, nil
}
