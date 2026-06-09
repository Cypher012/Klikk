package main

import (
	"bytes"
	"context"
	"encoding/base64"
	"fmt"
	"image/jpeg"
	"os"
	"os/exec"
	"time"

	"github.com/disintegration/imaging"
)

const (
	screenshotPath = "/tmp/klikk-screen.png"
	targetWidth    = 512
	jpegQuality    = 70
	originalWidth  = 1920
	originalHeight = 1080
)

func takeScreenshot() (string, error) {
	// Capture screen with grim
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := exec.CommandContext(ctx, "grim", "-o", "DP-3", screenshotPath).Run(); err != nil {
		return "", fmt.Errorf("grim failed: %w", err)
	}
	defer os.Remove(screenshotPath)

	// Open and resize
	img, err := imaging.Open(screenshotPath)
	if err != nil {
		return "", fmt.Errorf("open screenshot: %w", err)
	}
	resized := imaging.Resize(img, targetWidth, 0, imaging.Lanczos)
	// resized := img

	// Encode to JPEG in memory
	var buf bytes.Buffer
	if err := jpeg.Encode(&buf, resized, &jpeg.Options{Quality: jpegQuality}); err != nil {
		return "", fmt.Errorf("jpeg encode: %w", err)
	}

	return base64.StdEncoding.EncodeToString(buf.Bytes()), nil
}

// Scale coordinates Claude gave us (relative to 512px wide)
// back to the real screen resolution
func scaleCoords(x, y int) (int, int) {
	scaleX := float64(originalWidth) / float64(targetWidth)
	scaleY := float64(originalHeight) / float64(targetWidth)
	return int(float64(x) * scaleX), int(float64(y) * scaleY)
}
