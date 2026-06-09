package main

import (
	"encoding/json"
	"fmt"
	"net"
	"net/http"
	"os/exec"
	"strings"

	"github.com/cypher012/klikk/ai"
	"github.com/joho/godotenv"
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

var SOCKET_PATH = "/tmp/aicursor.sock"

func main() {
	err := godotenv.Load()
	if err != nil {
		fmt.Println("Error loading .env file:", err)
	}

	port := ":9999"
	fmt.Printf("🚀 Klikk Dev Server started! Listening on http://localhost%s\n", port)

	aiClient := ai.NewAnthropic()
	h := NewHandler(aiClient)

	http.HandleFunc("/trigger", h.Trigger)

	if err := http.ListenAndServe(port, nil); err != nil {
		fmt.Println("Error starting server:", err)
	}
}

func getUserInput() (string, error) {
	out, err := exec.Command(
		"zenity", "--entry", "--title=Klikk", "--text=What do you want to do",
	).Output()
	if err != nil {
		return "", err
	}
	return strings.TrimSpace(string(out)), nil
}
