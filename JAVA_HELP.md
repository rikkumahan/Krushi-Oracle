
# 🆘 Java Setup Troubleshooting Guide

It seems like **Maven** is installed but not added to your system's "Path". This means Windows doesn't know where to look when you type `mvn`.

## ✅ The Fix (2 Options)

### Option 1: Use the Full Path (easiest)
Copy and paste this long command to run the backend:

```powershell
& "C:\Program Files\JetBrains\IntelliJ IDEA Community Edition 2025.2\plugins\maven\lib\maven3\bin\mvn.cmd" spring-boot:run
```

### Option 2: Add Maven to Path (Recommended)
1. Press `Win + S` and search for "Environment Variables"
2. Click **"Edit the system environment variables"**
3. Click **"Environment Variables..."** button
4. Under "System variables" (bottom box), find **Path** and double-click it
5. Click **New** and paste this path:
   `C:\Program Files\JetBrains\IntelliJ IDEA Community Edition 2025.2\plugins\maven\lib\maven3\bin`
6. Click **OK** -> **OK** -> **OK**
7. **Restart your terminal** (close and reopen)
8. Now you can just run: `mvn spring-boot:run`

---

## 🔍 Diagnostics
- **Java**: Installed (v24.0.2) ✅
- **Maven**: Found in IntelliJ Plugins ✅
- **Command**: `mvn` not recognized ❌

Use **Option 1** right now to get started quickly!
