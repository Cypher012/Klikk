package main

import (
	"fmt"
	"net"
)

func main() {
	conn, err := net.Dial("unix", "/tmp/aicursor.sock")
	if err != nil {
		fmt.Println("Error connecting: ", err)
		return
	}
	defer conn.Close()

	msg := `{"type": "bubble", "text":"hello from Go!"}` + "\n"
	conn.Write([]byte(msg))
	fmt.Println("message sent!")
}
