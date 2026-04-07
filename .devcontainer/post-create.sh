#!/bin/bash

# Exit immediately on error, treat unset variables as an error, and fail if any command in a pipeline fails.
set -euo pipefail

# Function to run a command and show logs only on error
run_command() {
    local command_to_run="$*"
    local output
    local exit_code
    
    # Capture all output (stdout and stderr)
    output=$(eval "$command_to_run" 2>&1) || exit_code=$?
    exit_code=${exit_code:-0}
    
    if [ $exit_code -ne 0 ]; then
        echo -e "\033[0;31m[ERROR] Command failed (Exit Code $exit_code): $command_to_run\033[0m" >&2
        echo -e "\033[0;31m$output\033[0m" >&2
        
        exit $exit_code
    fi
}

# Installing UV (Python package manager)
echo -e "\n🐍 Installing UV - Python Package Manager..."
run_command "pip install uv"
echo "✅ Done"

# Installing CLI-based AI Agents

echo -e "\n🤖 Installing Copilot CLI..."
run_command "npm install -g @github/copilot@latest"
echo "✅ Done"

echo -e "\n🤖 Installing Codex CLI..."
run_command "npm install -g @openai/codex@latest"
echo "✅ Done"

echo -e "\n🤖 Installing Gemini CLI..."
run_command "npm install -g @google/gemini-cli@latest"
echo "✅ Done"

echo -e "\n🤖 Installing Specify CLI..."
run_command "uv tool install specify-cli --from git+https://github.com/github/spec-kit.git"
echo "✅ Done"

# if [ -f /workspaces/frictionless-architect/frontend/package.json ]; then
#     echo -e "\n🌐 Installing frontend dependencies and Playwright browser..."
#     run_command "cd /workspaces/frictionless-architect/frontend && npm config set bin-links false && npm install && node ./node_modules/playwright/cli.js install --with-deps chromium"
#     echo "✅ Done"
# fi

# Installing commitizen
echo -e "\n🛠️ Installing commitizen..."
run_command "pip install commitizen"
echo "✅ Done"

# Installing SonarQube
echo -e "\n🔍 Installing SonarQube Scanner..."
run_command "sudo apt-get update && sudo apt-get install -y default-jre"
run_command "sudo apt-get install -y libatk1.0-0 at-spi2-common libatk-bridge2.0-0 libgtk-3-0 libgtk-4-1 libgdk-pixbuf-xlib-2.0-0 libasound2 libasound2-data libcups2 libx11-xcb1 libxcomposite1 libxrandr2 libxss1 libwayland-client0 libwayland-egl1 libxdamage1 libxkbcommon0 libxshmfence1 libdbus-1-3 libdrm2 libegl1 libgbm1 libgl1-mesa-dri libgstreamer1.0-0"
echo "✅ Done"

# Installing Snyk CLI
echo -e "\n🔒 Installing Snyk CLI..."
run_command "npm install -g snyk@latest"
echo "✅ Done"

echo -e "\n🧹 Cleaning cache..."
run_command "sudo apt-get autoclean"
run_command "sudo apt-get clean"

echo "✅ Setup completed. Happy coding! 🚀"
