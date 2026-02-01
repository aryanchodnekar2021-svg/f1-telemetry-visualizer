# f1-telemetry-visualizer
An interactive Formula 1 race replay dashboard built with Python, Arcade, and FastF1. Features real-time telemetry graphs, driver position tracking, and session playback controls.
# F1 Telemetry Visualizer 🏎️ 📊

An interactive Python application that visualizes Formula 1 race data using [FastF1](https://github.com/theOehrly/Fast-F1) and the [Arcade](https://api.arcade.academy/) library.

This tool loads historical race data (default: Silverstone 2023) and renders a "replay" of the session, allowing you to track specific drivers and analyze their telemetry (Speed, Throttle, Brake, Gear) in sync with their position on the track.

## ✨ Features
* **Live Track Map:** Visualizes all drivers on the circuit simultaneously.
* **Telemetry Graphs:** Real-time plotting of Speed, Throttle, Brake, and Gear.
* **Interactive Leaderboard:** Click any driver to switch the telemetry focus.
* **Playback Controls:** Pause, play, and adjust replay speed.

## 🎮 Controls
| Input | Action |
| :--- | :--- |
| **Mouse Left** | Click a driver on the leaderboard to track them |
| **Spacebar** | Pause / Resume replay |
| **Arrow Up** | Increase replay speed |
| **Arrow Down** | Decrease replay speed |

## 📦 Requirements
* Python 3.8+
* `arcade`
* `fastf1`
* `pandas`
  <img width="1280" height="663" alt="image" src="https://github.com/user-attachments/assets/ee948b56-cec2-42bf-b6b7-7f3523485b9a" />
