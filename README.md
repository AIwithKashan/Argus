# 🛡️ Argus: Autonomous AI SRE Agent

![Project Status](https://img.shields.io/badge/Status-Completed-success)
![AI](https://img.shields.io/badge/AI-Gemini%202.5-purple)
![Platform](https://img.shields.io/badge/Platform-Windows-blue)

> **An autonomous digital immune system for infrastructure that predicts crashes and self-heals in real-time.**

![Argus Architecture Diagram](architecture.png)

---
## 👥 Team Members

| Name | Role |
|------|------|
| **Kashan Khan (AIwithKashan)** | Co-Developer & Infrastructure Lead |
| **Ayushi Dwivedi (ayushidubey4569-cell)** | Co-Developer & Load Testing Engineer |

## 📖 The Problem
In modern cloud infrastructure, **downtime is expensive**. Traditional monitoring tools are "reactive"—they wait for a server to crash before alerting a human engineer at 3 AM. By the time the alert is received, the damage is done.

## 💡 The Solution: Argus
Argus moves beyond monitoring to **proactive self-healing**. It is an Autonomous Site Reliability Engineering (SRE) Agent.

Instead of relying on static thresholds, Argus uses **Google Gemini 2.5** to actively *reason* about system telemetry in real-time. When it detects a critical threat—such as a rogue process causing rapid overheating or memory exhaustion—it doesn't just send an alert. It **autonomously intervenes**, intelligently hunting down the specific process responsible and terminating it to restore system stability immediately.

---

## 🏗️ Key Features (The Agentic Loop)

Argus implements a complete autonomous loop, moving from perception to action in seconds:

### 1. 👁️ Deep Observability (The Eyes)
A local Python agent scans the host machine at the kernel level, collecting real-time data on:
* **CPU Load** (Total system usage)
* **RAM Usage** (Memory pressure)
* **Network I/O** (Real-time throughput)
* **Hardware Temperature** (via Windows WMI sensors, with physics-based simulation fallback)

### 2. 🧠 Gemini 2.5 Reasoning (The Brain)
Telemetry is streamed to a central Flask server. Anomalies are sent to the **Gemini 2.5 API**. The LLM analyzes the *context* (e.g., "Is high CPU correlated with dangerous temperatures?") to distinguish between safe heavy load and a critical threat.

### 3. 🛠️ Smart Autonomous Action (The Hands)
Upon confirming a threat, Gemini authorizes a **"Kill Command"**. The Agent switches to "Predator Mode." Unlike simple scripts, Argus is a **Smart Hunter**:
* It scans the process list for the highest resource consumer.
* It checks a robust **Safety Whitelist** to avoid killing critical system apps (e.g., Explorer, Browsers).
* It intelligently differentiates between its own components (Dashboard, Server) and rogue Python scripts, ensuring it only terminates the threat.

---

## 🔥 Load Testing Module (By Ayushi)

To validate Argus’s autonomous threat response, a custom **Multicore CPU Burner** has been implemented by Ayushi.

This module generates **100% CPU usage on every core** to simulate extreme real-world overload scenarios.

### 🎯 Why This Module Matters
- Helps Argus detect CPU-based anomalies  
- Triggers autonomous “Kill Command”  
- Tests prediction accuracy of the AI engine  
- Validates the safety-checking mechanism  
- Ensures Argus reliably distinguishes between legitimate and harmful workloads  

### 📂 File Location
`load_generators/cpu_burner_multicore.py`

### ▶️ Run the Burner
```bash
python cpu_burner_multicore.py
```
---

## 🚀 Quick Start Guide

**Prerequisites:** Windows 10/11, Python 3.10+, Administrator Privileges.

### 1. Installation
```bash
git clone https://github.com/AIwithKashan/Argus-Autonomous-AI-SRE
cd Argus
pip install -r requirements.txt
```
### 2. Configuration
Open .env file in the root directory and add your Google Gemini API Key:
```
GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Launch (One-Click Orchestration)

⚠️ IMPORTANT: You must run your terminal as Administrator for hardware access and process termination privileges.

Run the main orchestrator script:
```
python main.py
```

This automatically launches the Brain (Server), the Smart Agent (Hunter), and the Cyberpunk Mission Control Dashboard in your browser.

### 🧪 The Demo: Triggering a Self-Healing Event
To demonstrate Argus's autonomy, we include "Villain" scripts to simulate attacks.

Ensure Argus is running and the dashboard shows GREEN status.

Open a new terminal and run the CPU burner:
```
python cpu_burner.py
```

Watch the autonomous response:

The dashboard header turns RED (CRITICAL THREAT DETECTED).

The CPU Chart turns red as it crosses the danger line.

Gemini logs show: ACTION: KILL.

The Smart Agent identifies the specific python.exe running the burner (ignoring the dashboard process) and terminates it.

The dashboard reports the exact terminated PID in the "Action Report" panel and returns to GREEN.

### 🛠️ Tech Stack
AI Engine: Google Gemini 2.5

Backend: Python Flask, SQLite

Frontend: Streamlit, Altair (Cyberpunk UI Theme)

System Core: psutil (Process management), WMI (Windows hardware sensors), pywin32
