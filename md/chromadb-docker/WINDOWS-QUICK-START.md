# Windows Quick Start Guide

## Product Owner RAG - Windows Setup

This guide is specifically for **Windows users**. All commands and scripts are Windows-compatible.

---

## Prerequisites

✅ **Docker Desktop** - Must be installed and running
✅ **AWS Credentials** - Configured in `%USERPROFILE%\.aws\credentials`
✅ **ChromaDB** - Knowledge base already ingested

---

## Quick Start (Windows)

### Option 1: Batch File (Simplest)

Double-click to run:

```
start-po-rag.bat
```

Or from Command Prompt:
```cmd
cd C:\Work\Prophix.Conso.2026.1\docs\DC\md\chromadb-docker
start-po-rag.bat
```

### Option 2: PowerShell (Recommended)

Right-click `start-po-rag.ps1` → **Run with PowerShell**

Or from PowerShell:
```powershell
cd C:\Work\Prophix.Conso.2026.1\docs\DC\md\chromadb-docker
.\start-po-rag.ps1
```

### Option 3: Manual Docker Compose

```cmd
cd C:\Work\Prophix.Conso.2026.1\docs\DC\md\chromadb-docker
docker-compose -f docker-compose-with-po-rag.yml up -d
```

---

## Accessing the Portal

Once started, open your web browser:

**http://localhost:8501**

---

## Stopping Services

### Batch File:
```cmd
stop-po-rag.bat
```

### PowerShell:
```powershell
.\stop-po-rag.ps1
```

### Manual:
```cmd
docker-compose -f docker-compose-with-po-rag.yml down
```

---

## Windows-Specific Notes

### Docker Desktop Requirements

Make sure Docker Desktop is:
- ✅ Installed (latest version)
- ✅ Running (check system tray icon)
- ✅ WSL 2 integration enabled (Settings → General)

### AWS Credentials Location

Windows path: `C:\Users\YourUsername\.aws\credentials`

Format:
```ini
[prophix-devops]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
```

### PowerShell Execution Policy

If you get an error running `.ps1` scripts:

```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Firewall / Antivirus

If port 8501 is blocked:
1. Open **Windows Defender Firewall**
2. Click **Advanced settings**
3. Click **Inbound Rules** → **New Rule**
4. Select **Port** → **TCP** → Port **8501**
5. Select **Allow the connection**
6. Apply to all profiles

---

## Troubleshooting (Windows)

### Docker Desktop not running

**Symptom:** "Error: Docker is not running"

**Solution:**
1. Start Docker Desktop from Start Menu
2. Wait for Docker to fully start (whale icon in system tray)
3. Run the start script again

### Port 8501 already in use

**Symptom:** "Bind for 0.0.0.0:8501 failed: port is already allocated"

**Solution:**
```cmd
# Find what's using port 8501
netstat -ano | findstr :8501

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or change port in docker-compose-with-po-rag.yml
# Change "8501:8501" to "8502:8501"
# Then access at http://localhost:8502
```

### Cannot connect to ChromaDB

**Symptom:** "No results found in knowledge base"

**Solution:**
```cmd
# Check if ChromaDB container is running
docker ps | findstr chromadb

# If not running, start just ChromaDB first
docker-compose up -d chromadb

# Wait 10 seconds, then start Product Owner RAG
timeout /t 10
docker-compose -f docker-compose-with-po-rag.yml up -d product-owner-rag
```

### AWS Credentials not found

**Symptom:** "Unable to locate credentials"

**Solution:**
```cmd
# Verify credentials file exists
dir %USERPROFILE%\.aws\credentials

# If missing, create it:
mkdir %USERPROFILE%\.aws
notepad %USERPROFILE%\.aws\credentials

# Add your credentials:
[prophix-devops]
aws_access_key_id = YOUR_KEY
aws_secret_access_key = YOUR_SECRET
```

### Streamlit not loading

**Symptom:** Browser shows "This site can't be reached"

**Solution:**
```cmd
# Check container status
docker-compose -f docker-compose-with-po-rag.yml ps

# Check logs for errors
docker-compose -f docker-compose-with-po-rag.yml logs product-owner-rag

# Restart container
docker-compose -f docker-compose-with-po-rag.yml restart product-owner-rag

# Wait 10 seconds then try http://localhost:8501 again
```

---

## Windows File Paths

All paths in this project use Windows format:

| Linux Path | Windows Path |
|------------|--------------|
| `/mnt/c/Work/...` | `C:\Work\...` |
| `./script.sh` | `script.bat` or `.\script.ps1` |
| `~/.aws/` | `%USERPROFILE%\.aws\` or `C:\Users\YourName\.aws\` |

---

## Viewing Logs (Windows)

### Command Prompt:
```cmd
cd C:\Work\Prophix.Conso.2026.1\docs\DC\md\chromadb-docker
docker-compose -f docker-compose-with-po-rag.yml logs -f product-owner-rag
```

### PowerShell:
```powershell
cd C:\Work\Prophix.Conso.2026.1\docs\DC\md\chromadb-docker
docker-compose -f docker-compose-with-po-rag.yml logs -f product-owner-rag
```

Press `Ctrl+C` to exit logs.

---

## Windows Scripts Available

| Script | Type | Purpose |
|--------|------|---------|
| `start-po-rag.bat` | Batch | Start services (simple) |
| `start-po-rag.ps1` | PowerShell | Start services (colorful) |
| `stop-po-rag.bat` | Batch | Stop services (simple) |
| `stop-po-rag.ps1` | PowerShell | Stop services (colorful) |

**Recommendation:** Use `.bat` files for simplicity or `.ps1` for better output.

---

## Complete Windows Workflow

### First Time Setup

1. **Verify Docker Desktop is running**
   - Check system tray for Docker whale icon
   - Should show "Docker Desktop is running"

2. **Verify AWS credentials**
   ```cmd
   type %USERPROFILE%\.aws\credentials
   ```
   Should show `[prophix-devops]` profile

3. **Navigate to directory**
   ```cmd
   cd C:\Work\Prophix.Conso.2026.1\docs\DC\md\chromadb-docker
   ```

4. **Start services**
   ```cmd
   start-po-rag.bat
   ```

5. **Open browser**
   - Go to: http://localhost:8501
   - Ask: "How does equity method consolidation work?"

6. **When done, stop services**
   ```cmd
   stop-po-rag.bat
   ```

---

## Network Access from Other Windows Machines

To allow other computers to access the Product Owner Portal:

### 1. Find your Windows machine IP

```cmd
ipconfig
```

Look for "IPv4 Address" (e.g., `192.168.1.100`)

### 2. Allow port in Windows Firewall

```cmd
# Run as Administrator
netsh advfirewall firewall add rule name="Product Owner RAG" dir=in action=allow protocol=TCP localport=8501
```

### 3. Share URL with product owner

Give them: `http://192.168.1.100:8501`

(Replace with your actual IP address)

---

## Deployment to Windows Server

If you have a Windows Server:

### 1. Install Docker Desktop on Windows Server

Download from: https://www.docker.com/products/docker-desktop

### 2. Copy files to server

```cmd
# From your machine
xcopy /E /I C:\Work\Prophix.Conso.2026.1\docs\DC\md\chromadb-docker \\SERVER\C$\fc-knowledge-base\
```

### 3. On server, configure AWS credentials

```cmd
mkdir %USERPROFILE%\.aws
notepad %USERPROFILE%\.aws\credentials
```

### 4. Start services on server

```cmd
cd C:\fc-knowledge-base\chromadb-docker
start-po-rag.bat
```

### 5. Share server URL

Give product owner: `http://server-hostname:8501`

---

## Summary

**Start:** Double-click `start-po-rag.bat`
**Access:** http://localhost:8501
**Stop:** Double-click `stop-po-rag.bat`

All scripts are Windows-native - no WSL or Linux required! 🪟
