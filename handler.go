package main

import (
	"fmt"
	"net"
	"net/http"

	"github.com/cypher012/klikk/ai"
)

type Handler struct {
	aiClient *ai.Anthropic
}

func NewHandler(aiClient *ai.Anthropic) *Handler {
	return &Handler{aiClient: aiClient}
}

func (h *Handler) Trigger(w http.ResponseWriter, r *http.Request) {
	fmt.Println("\n⚡ Hotkey pressed! Opening input modal...")

	conn, err := net.Dial("unix", SOCKET_PATH)
	if err != nil {
		fmt.Println("Error: Python overlay socket not open.")
		w.WriteHeader(http.StatusServiceUnavailable)
		return
	}
	defer conn.Close()

	task, err := getUserInput()
	if err != nil || task == "" {
		fmt.Println("Input cancelled or empty.")
		return
	}
	fmt.Println("User input received:", task)

	sendMessage(conn, Message{Type: "bubble", Text: "Taking screenshot..."})

	imageBase64, err := takeScreenshot()
	if err != nil {
		fmt.Println("Screenshot error:", err)
		sendMessage(conn, Message{Type: "bubble", Text: "Screenshot failed"})
		return
	}

	sendMessage(conn, Message{Type: "bubble", Text: "Analyzing screen..."})

	analysis, err := h.aiClient.AnalyzeScreen(task, imageBase64)
	if err != nil {
		fmt.Println("AI error:", err)
		sendMessage(conn, Message{Type: "bubble", Text: "Couldn't analyze screen"})
		return
	}

	realX, realY := scaleCoords(analysis.X, analysis.Y)
	fmt.Printf("Claude says: click (%d, %d) → scaled to (%d, %d)\n",
		analysis.X, analysis.Y, realX, realY)
	fmt.Println("Instruction:", analysis.Instruction)

	sendMessage(conn, Message{Type: "move", X: realX, Y: realY})
	sendMessage(conn, Message{Type: "bubble", Text: analysis.Instruction})

	fmt.Fprintln(w, "Success")
}
