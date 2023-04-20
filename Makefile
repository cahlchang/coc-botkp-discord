# Makefile

TARGET_DIR = lambda/coc-bot-kp/
COMMAND = lambroll deploy --function=function.json --src="."
WEBHOOK_URL_FILE = webhook_url.txt

.PHONY: run_command notify_discord

run_command_with_notification: run_command notify_discord

run_command:
	cd $(TARGET_DIR) && $(COMMAND)

notify_discord:
	curl -X POST -H "Content-Type: application/json" -d '{"content": "Make command has been executed."}' $(shell cat $(WEBHOOK_URL_FILE))
