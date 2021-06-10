#!/bin/bash

# Put file in crontab
# @reboot /bot/autostart.sh

SESSION_NAME=bot

tmux_command() {
        tmux send-keys -t "$SESSION_NAME" "$*" C-m
}

tmux new -d -s $SESSION_NAME

tmux_command cd /bot
tmux_command python3 main.py