package ai

import (
	"context"
	"encoding/json"
	"fmt"
	"os"

	anthropic "github.com/anthropics/anthropic-sdk-go"
	"github.com/anthropics/anthropic-sdk-go/option"
	"github.com/invopop/jsonschema"
)

type Anthropic struct {
	client anthropic.Client
}

type ScreenAnalysis struct {
	X           int    `json:"x"`
	Y           int    `json:"y"`
	Instruction string `json:"instruction"`
}

func generateSchema(v any) map[string]any {
	r := jsonschema.Reflector{
		AllowAdditionalProperties: false,
		DoNotReference:            true,
	}

	s := r.Reflect(v)

	b, _ := json.Marshal(s)

	var m map[string]any
	json.Unmarshal(b, &m)

	return m
}

func NewAnthropic() *Anthropic {
	client := anthropic.NewClient(
		option.WithAPIKey(os.Getenv("ANTHROPIC_API_KEY")),
	)
	return &Anthropic{client}
}

func (a *Anthropic) NewMessage(prompt string) string {
	msg, _ := a.client.Messages.New(
		context.TODO(),
		anthropic.MessageNewParams{
			Model:     anthropic.ModelClaudeHaiku4_5,
			MaxTokens: 1024,
			Messages: []anthropic.MessageParam{
				anthropic.NewUserMessage(
					anthropic.NewTextBlock(prompt),
				),
			},
		},
	)

	return msg.Content[0].Text
}

func (a *Anthropic) NewStreamingMessage(
	prompt string,
	onText func(string),
) error {

	stream := a.client.Messages.NewStreaming(
		context.TODO(),
		anthropic.MessageNewParams{
			Model:     anthropic.ModelClaudeOpus4_8,
			MaxTokens: 1024,
			Messages: []anthropic.MessageParam{
				anthropic.NewUserMessage(
					anthropic.NewTextBlock(prompt),
				),
			},
		},
	)

	for stream.Next() {
		event := stream.Current()

		switch eventVariant := event.AsAny().(type) {
		case anthropic.ContentBlockDeltaEvent:
			switch delta := eventVariant.Delta.AsAny().(type) {
			case anthropic.TextDelta:
				onText(delta.Text)
			}
		}
	}

	return stream.Err()
}

func (a *Anthropic) AnalyzeScreen(
	task string,
	imageBase64 string,
) (*ScreenAnalysis, error) {

	schema := generateSchema(&ScreenAnalysis{})

	msg, err := a.client.Messages.New(
		context.TODO(),
		anthropic.MessageNewParams{
			Model:     anthropic.ModelClaudeHaiku4_5,
			MaxTokens: 256,

			Messages: []anthropic.MessageParam{
				anthropic.NewUserMessage(
					anthropic.NewImageBlockBase64(
						"image/jpeg",
						imageBase64,
					),

					anthropic.NewTextBlock(fmt.Sprintf(`
The screenshot has been resized to 512px width.

Task:
%s

Find the next UI element the user should interact with.
Return coordinates relative to the resized image.
`, task)),
				),
			},

			OutputConfig: anthropic.OutputConfigParam{
				Format: anthropic.JSONOutputFormatParam{
					Schema: schema,
				},
			},
		},
	)

	if err != nil {
		return nil, err
	}

	fmt.Printf(
		"🔢 Tokens — input: %d, output: %d, total: %d\n",
		msg.Usage.InputTokens,
		msg.Usage.OutputTokens,
		msg.Usage.InputTokens+msg.Usage.OutputTokens,
	)

	for _, block := range msg.Content {
		switch variant := block.AsAny().(type) {

		case anthropic.TextBlock:
			var result ScreenAnalysis

			if err := json.Unmarshal(
				[]byte(variant.Text),
				&result,
			); err != nil {
				return nil, err
			}

			return &result, nil
		}
	}

	return nil, fmt.Errorf("no structured output returned")
}
