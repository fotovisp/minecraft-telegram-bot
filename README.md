# Minecraft & IDRAC 7 Server Management Telegram Bot 🤖

A powerful asynchronous Telegram bot built with Aiogram 3.x to remotely control a Minecraft server and the physical hardware it runs on. It bridges the gap between game management (via tmux/mcrcon) and hardware control (via iDRAC 7).

## 🚀 Features

### 🔌 Hardware Management (iDRAC 7)
* Power Control: power on / power off commands to manage physical server state.
* Smart Status: Checks if the server is connected to electricity (iDRAC ping) and its current power state via racadm.
* Automated Monitoring: When powering on, the bot pings the host OS and notifies you once it is fully booted.

### 🎮 Minecraft Server Control
* Process Management: start, stop, and restart server instances within a tmux session.
* Player Access: list command to see who is online using mcrcon.
* Reliable Backups: backup command triggers a multi-disk redundancy script to safeguard world data.

## 🛠 Tech Stack
* Python 3.11 (Aiogram 3.x, Fabric)
* Docker & Docker Compose (Containerization)
* Tmux (Session persistence)
* Mcrcon (RCON protocol communication)
* Bash (Automation scripts)

## 📋 Requirements & Setup

### 1. SSH Configuration
The bot expects an SSH alias named "idrac" to handle legacy RSA algorithms required by iDRAC 7. Add this to your ~/.ssh/config:

Host idrac
    HostName <YOUR_IDRAC_IP>
    User <YOUR_USER>
    IdentityFile ~/.ssh/idrac_key
    PubkeyAcceptedAlgorithms +ssh-rsa
    HostKeyAlgorithms +ssh-rsa
    StrictHostKeyChecking no

### 2. Minecraft Server Setup
* Enable RCON in your server.properties and set a password.
* Ensure tmux is installed on the host server.
* Place backup.sh in your server directory and make it executable.

### 3. Environment Variables
Copy .env.example to .env and fill in your credentials:
* Bot Token & Admin ID
* Host SSH details (IP, User)
* iDRAC credentials
* RCON password & Tmux session name

## ⚙️ Deployment

For production (Docker):
$ docker compose up -d --build

For testing/manual start:
$ chmod +x start_bot.sh
$ ./start_bot.sh

## 📂 Project Structure
* commands/admin_commands.py — Admin-only handlers (power, backup, stop).
* commands/user_commands.py — User handlers (start, restart, list, status).
* config.py — Environment variables & configuration.
* telegram_bot.py — Bot & dispatcher setup, SSH helpers.
* main.py — Entry point.
* backup.example — Example backup script.
* start_bot.sh — Shell script for quick launch.
* requirements.txt — Python dependencies.
* docker-compose.yml — Docker orchestration file.

---
Developed for automated server infrastructure management.
