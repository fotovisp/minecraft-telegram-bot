#!/bin/bash

if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

cd $user_path/bot
source .venv/bin/activate
python3 bot.py
