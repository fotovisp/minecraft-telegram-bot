# iDRAC 7 Telegram Management Bot 

A lightweight asynchronous Telegram bot for remote power management and status monitoring of **Dell PowerEdge R720xd** servers. This tool uses secure SSH key authentication to interact with the iDRAC 7 controller.

## 🚀 Features
* **Live Status:** Check real-time power status (ON/OFF) via Telegram.
* **Power Control:** Remotely Power Up, Graceful Shutdown, or Hard Reset the server.
* **Secure Auth:** Uses RSA SSH keys (no passwords stored in plain text).
* **Dockerized:** Fully containerized for easy deployment and isolation.

## 🖥 Tested Hardware
* **Model:** Dell PowerEdge R720xd
* **Controller:** iDRAC 7 Enterprise
* **Firmware:** v2.65.65.65 (Latest Stable)
* **BIOS:** v2.9.0

## 🛠 Tech Stack
* **Python 3.11**
* **Aiogram 3.x** (Telegram Framework)
* **Fabric/Invoke** (SSH Orchestration)
* **Docker & Docker Compose**

## 📋 Prerequisites

### 1. Generate SSH Keys
iDRAC 7 requires legacy RSA keys. Generate a 2048-bit key on your host machine:
\`\`\`bash
ssh-keygen -t rsa -b 2048 -f ~/.ssh/idrac_key
\`\`\`

### 2. Upload Public Key to iDRAC
Push your key to the iDRAC controller using the \`racadm\` utility:
\`\`\`bash
racadm -r <IDRAC_IP> -u root -p <PASSWORD> sshpkauth -i 2 -k 1 -t "\$(cat ~/.ssh/idrac_key.pub)"
\`\`\`

### 3. SSH Client Configuration
To ensure the bot connects properly, add this entry to your \`~/.ssh/config\`:
\`\`\`text
Host idrac
    HostName <IDRAC_IP>
    User root
    IdentityFile ~/.ssh/idrac_key
    PubkeyAcceptedAlgorithms +ssh-rsa
    HostKeyAlgorithms +ssh-rsa
    StrictHostKeyChecking no
\`\`\`

## ⚙️ Installation & Deployment

### 1. Project Setup
Clone the repository and prepare the environment:
\`\`\`bash
git clone https://github.com/fotovisp/minecraft-telegram-bot
cd minecraft-telegram-bot
cp .env.example .env
# Edit .env with your BOT_TOKEN and admin USER_ID
\`\`\`

### 2. Server-Side Execution (start_bot.sh)
The project includes a \`start_bot.sh\` script located on the host server. This script automates the deployment process by building the image and starting the container in detached mode.

To launch the bot, run:
\`\`\`bash
chmod +x start_bot.sh
./start_bot.sh
\`\`\`

### 3. Manual Docker Management
Alternatively, you can manage the container using standard Docker Compose commands:
\`\`\`bash
# Build and start
docker compose up -d --build

# Check logs
docker compose logs -f

# Stop the bot
docker compose down
\`\`\`

## 📂 Project Structure
* \`bot.py\` – Core bot logic and Telegram handlers.
* \`Dockerfile\` – Python environment and dependencies.
* \`docker-compose.yml\` – Service orchestration and volume mapping for SSH keys.
* \`start_bot.sh\` – Automation script for server-side execution.
* \`.env.example\` – Template for required environment variables.
* \`.gitignore\` – Protection for sensitive files (.env, keys, logs).

---
**Developed b fotovisp**
