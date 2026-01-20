# 🔧 TROUBLESHOOTING GUIDE

## Problem: AttributeError with python-telegram-bot

### Root Cause

The error `AttributeError: 'Updater' object has no attribute '_Updater__polling_cleanup_cb'` occurs when:

- Using Python 3.13 with python-telegram-bot version 20.x
- Python 3.13 changed how `__slots__` work, breaking compatibility

### Solution Applied

✅ Updated `requirements.txt` to use `python-telegram-bot==21.9` (Python 3.13 compatible)
✅ Updated Dockerfile to use Python 3.11-slim (more stable)
✅ Added proper environment variables to Dockerfile

## How to Fix Your Running Container

### Option 1: Rebuild Docker Container (Recommended)

**If you have Docker Desktop:**

1. Open Docker Desktop
2. Stop the `wisdom_bot` container
3. Delete the container
4. Delete the image `motiv_bot_motiv_bot`
5. Run the rebuild script:

   ```powershell
   cd c:\Users\User\Documents\viral_cont\motiv_bot
   .\rebuild.ps1
   ```

**Or manually:**

```powershell
cd c:\Users\User\Documents\viral_cont\motiv_bot
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Option 2: Run Locally (For Testing)

```powershell
cd c:\Users\User\Documents\viral_cont\motiv_bot

# Install updated dependencies
pip install -r requirements.txt

# Run the bot
.\run_local.ps1
# OR
python bot.py
```

## Files Changed

### 1. requirements.txt

- ✅ Updated `python-telegram-bot` from 20.6 to 21.9
- ✅ Added `requests==2.31.0`

### 2. Dockerfile

- ✅ Added environment variables for Python
- ✅ Upgraded pip before installing dependencies
- ✅ Simplified .env handling

### 3. New Files Created

- ✅ `docker-compose.yml` - Easy container management
- ✅ `rebuild.ps1` - Quick rebuild script
- ✅ `run_local.ps1` - Local testing script
- ✅ `README.md` - Full documentation
- ✅ `.env.example` - Environment template
- ✅ `.dockerignore` - Exclude unnecessary files

## Verification Steps

After rebuilding, check if the bot is running:

```powershell
# View logs
docker-compose logs -f

# Check container status
docker ps

# Test the bot
# Send /start to your bot in Telegram
```

## Expected Output

You should see:

```
⏰ Планировщик запущен
🚀 Бот запущен! @your_bot_username
👤 Админ: 379494671
📢 Канал: -1003629404812
```

## Common Issues

### Issue: "docker-compose: command not found"

**Solution:** Use Docker Desktop GUI or install Docker Compose

### Issue: "BOT_TOKEN не установлен"

**Solution:** Make sure `.env` file exists and contains valid tokens

### Issue: Container keeps restarting

**Solution:** Check logs with `docker-compose logs -f`

### Issue: Can't connect to Docker daemon

**Solution:** Start Docker Desktop application

## Need Help?

1. Check logs: `docker-compose logs -f`
2. Verify .env file has all required variables
3. Make sure Docker Desktop is running
4. Try running locally first to isolate Docker issues

## Quick Commands Reference

```powershell
# Rebuild everything
docker-compose up -d --build --force-recreate

# Stop bot
docker-compose down

# View logs
docker-compose logs -f

# Restart bot
docker-compose restart

# Run locally
python bot.py
```
