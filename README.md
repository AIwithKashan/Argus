# 🛡️ Argus: Autonomous AI SRE Agent

> **An autonomous digital immune system for infrastructure that predicts crashes and self-heals in real-time.**

![Argus Architecture Diagram](architecture.png)

---

## 📖 The Problem
In modern cloud infrastructure, **downtime is expensive**. Traditional monitoring tools are "reactive"—they wait for a server to crash before alerting a human engineer at 3 AM. By the time the alert is received, the damage is done.

## 💡 The Solution: Argus
Argus moves beyond monitoring to **proactive self-healing**. It is an Autonomous Site Reliability Engineering (SRE) Agent.

Instead of relying on static thresholds, Argus uses **Google Gemini 2.5** to actively *reason* about system telemetry in real-time. When it detects a critical threat—such as a rogue process causing rapid overheating—it doesn't just send an alert. It **autonomously intervenes**, hunting down the specific process responsible and terminating it to restore system stability immediately.

---

## 🏗️ Key Features (The Agentic Loop)

Argus implements a complete autonomous loop:

### 1. 👁️ Deep Observability (The Eyes)
A local Python agent scans the host machine at the kernel level, collecting real-time data on:
* **CPU Load** (Total system usage)
* **RAM Usage** (Memory pressure)
* **Network I/O** (Real-time speed in MB/s)
* **Hardware Temperature** (via Windows WMI sensors, with physics-based simulation fallback)

### 2. 🧠 LLM Reasoning (The Brain)
Telemetry is streamed to a central Flask server. Anomalies are sent to the **Gemini 2.5 Flash API**. The LLM analyzes the *context* (e.g., "Is high CPU correlated with dangerous temperatures?") to distinguish between safe heavy load and a critical threat.

### 3. 🛠️ Autonomous Action (The Hands)
Upon confirming a threat, Gemini authorizes a **"Kill Command"**. The Agent switches to "Predator Mode," scanning the entire process list to identify the highest resource consumer and terminating it autonomously, protecting the host machine.

---

## 🚀 Quick Start Guide

**Prerequisites:** Windows 10/11, Python 3.10+, Administrator Privileges.

### 1. Installation
```bash
git clone https://github.com/AIwithKashan/Argus-Autonomous-AI-SRE
cd Argus
pip install -r requirements.txt 
```

2. Configuration
Open .env file in the root directory and add your Google Gemini API Key:

GEMINI_API_KEY=your_actual_api_key_here

4. Launch (One-Click Orchestration)
⚠️ IMPORTANT: You must run your terminal as Administrator for hardware access and process termination privileges.

Run the main orchestrator script:

```bash
python main.py
```

This will automatically launch three windows: The Brain (Server), the Agent (Hunter), and the Mission Control Dashboard (in your browser).

🧪 The Demo: Triggering a Self-Healing Event
To demonstrate Argus's autonomy, we include a "Villain" script (cpu_burner.py) that simulates a runaway process.

Ensure Argus is running and the dashboard shows GREEN status.

Open a new terminal and run the burner:

```bash
python cpu_burner.py
```

Watch the autonomous response:

The dashboard will turn RED (Critical) as CPU and Temp spike.

Gemini logs will show: ACTION: KILL.

The Argus Agent will identify the python.exe running the burner and terminate it.

The system will return to GREEN automatically.

🛠️ Tech Stack
AI Engine: Google Gemini 2.5 Flash

Backend: Python Flask

Frontend: Streamlit with custom Altair charts (Cyberpunk UI)

System Core: psutil (Process management), WMI (Windows Management Instrumentation)
