# Quick Start Guide

Get Service Renewal Hub running in under 5 minutes.

## Prerequisites

- Node.js >= 18
- Python >= 3.9
- MongoDB (running locally or cloud)
- Yarn or npm

## Steps

### 1. Clone & Setup Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your MongoDB URL and a secure JWT secret
```

### 2. Setup Frontend

```bash
cd ../frontend
yarn install
cp .env.example .env
# Edit .env if backend is not on localhost:8001
```

### 3. Start MongoDB

```bash
# If using local MongoDB:
sudo systemctl start mongod
# OR on macOS:
brew services start mongodb-community
```

### 4. Start Backend

```bash
cd backend
source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### 5. Start Frontend (new terminal)

```bash
cd frontend
yarn start
```

### 6. Access Application

1. Open http://localhost:3000
2. Click "Sign Up" to create your admin account (first user is admin)
3. Go to Settings to configure email and branding

## That's it! 🎉

Your Service Renewal Hub is now running.

---

## Next Steps

- Configure email provider (Settings > Email)
- Customize branding (Settings > Branding)
- Add your first service
- Invite team members

See [README.md](README.md) for detailed documentation.
