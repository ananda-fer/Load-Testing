# 🚀 Load Testing Tool for Termux

Python-based load testing tool specifically designed for Termux (Android). Test your own websites' capacity and performance.

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Termux-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

## 📋 Features

- **Multi-threading**: Simulate multiple concurrent users
- **Real-time Metrics**: Live progress bar and performance stats
- **Customizable**: Adjust concurrent users, duration, and request rate
- **Ethical Use**: Designed only for testing YOUR OWN websites

## 🛠️ Installation
### Prerequisites
- Termux (Android)
- Python 3.8+
- Internet connection

## Setup in Termux
### Update packages
pkg update && pkg upgrade

### Install Python
pkg install python -y

### Install required packages
pip install requests

### Clone repository
git clone https://github.com/ananda-fer/Load-Testing.git

cd Load-Testing

### Make script executable
chmod +x load-test.py

### Quick Start
python load-test.py
