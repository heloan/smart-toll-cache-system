# Toll Frontend (React)

## Overview

React-based operator dashboard for real-time toll booth transaction management. Provides an interface for toll booth operators to search, view, and correct transactions.

## Responsibilities

- Transaction search by vehicle plate, tag, lane, or plaza
- Real-time transaction correction interface
- Transaction status display and filtering
- Communication with backend API via NGINX gateway

## Tech Stack

| Technology | Version | Purpose                      |
|------------|---------|------------------------------|
| React      | 18      | UI framework                 |
| Node.js    | 18+     | Runtime                      |

## How to Run

```bash
# Via Docker Compose (recommended)
docker-compose -f infrastructure/docker-compose.yml up toll-frontend

# Local development
cd services/toll-frontend-react
npm install
npm start
```

## Ports

| Port | Protocol | Description          |
|------|----------|----------------------|
| 3000 | HTTP     | Development server   |
