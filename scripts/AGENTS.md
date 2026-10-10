# Scripts agent guide

## Purpose

This directory contains the local run controls for the project. These scripts are responsible for starting and stopping the backend server across supported platforms.

## Current contents

- `start.sh` and `stop.sh` for Mac and Linux shells
- `start.ps1` and `stop.ps1` for Windows PowerShell

## Behavior

Each start script should:

- enter the backend directory;
- ensure the local Python environment is available;
- install dependencies with `uv` when needed;
- launch the FastAPI app with Uvicorn;
- write the active process ID to a local `.pm-server.pid` file.

Each stop script should:

- read the PID file;
- stop the running process cleanly;
- remove the PID file when complete.

## Notes

These scripts are deliberately simple. Do not add complex orchestration, extra services, or environment setup beyond what is needed to run the local app and confirm it responds correctly.