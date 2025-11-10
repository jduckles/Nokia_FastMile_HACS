# Setup and Publishing Guide

This guide will help you set up, test, and publish your Nokia FastMile 5G Home Assistant integration.

## Table of Contents

1. [Local Testing](#local-testing)
2. [Publishing to GitHub](#publishing-to-github)
3. [Adding to HACS](#adding-to-hacs)
4. [Installing in Home Assistant](#installing-in-home-assistant)

---

## Local Testing

Before publishing, test the integration locally in your Home Assistant instance.

### Step 1: Copy Integration to Home Assistant

```bash
# Copy the integration folder to your HA config directory
cp -r /home/daniel/NokiaFastMile/custom_components/nokia_fastmile /path/to/homeassistant/config/custom_components/

# For Home Assistant OS/Supervised:
cp -r /home/daniel/NokiaFastMile/custom_components/nokia_fastmile /config/custom_components/

# For Docker:
cp -r /home/daniel/NokiaFastMile/custom_components/nokia_fastmile /your/ha/config/custom_components/
```

### Step 2: Restart Home Assistant

Restart Home Assistant completely to load the new integration:
- UI: Settings → System → Restart
- CLI: `ha core restart`

### Step 3: Add the Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Nokia FastMile 5G"
4. Enter your device credentials:
   - Host: `192.168.192.1`
   - Username: `admin`
   - Password: `your_password`
5. Click Submit

### Step 4: Verify All Sensors

Check that all sensors are created and showing data:

```bash
# List all entities
ha-cli state list | grep nokia_fastmile
```

Expected entities:
- 17 sensors
- 1 button

---

## Publishing to GitHub

### Step 1: Create GitHub Repository

1. Go to [GitHub](https://github.com/) and log in
2. Click the **+** icon → **New repository**
3. Fill in details:
   - **Repository name**: `nokia-fastmile-ha` (or your choice)
   - **Description**: "Home Assistant integration for Nokia FastMile 5G receivers"
   - **Visibility**: Public (required for HACS)
   - **Initialize with**: None (we'll push existing code)
4. Click **Create repository**

### Step 2: Update Repository URLs

Before publishing, update these files with your GitHub username:

**1. manifest.json**
```bash
cd /home/daniel/NokiaFastMile/custom_components/nokia_fastmile
nano manifest.json
```

Update:
```json
"codeowners": ["@YOUR_GITHUB_USERNAME"],
"documentation": "https://github.com/YOUR_USERNAME/nokia-fastmile-ha",
"issue_tracker": "https://github.com/YOUR_USERNAME/nokia-fastmile-ha/issues",
```

**2. README_INTEGRATION.md, INFO.md, INSTALLATION.md**

Replace all instances of:
- `yourusername` → `YOUR_GITHUB_USERNAME`
- Update repository URLs

### Step 3: Initialize Git and Push

```bash
cd /home/daniel/NokiaFastMile

# Initialize git repository
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial release v1.0.0"

# Add remote (replace with your repository URL)
git remote add origin https://github.com/YOUR_USERNAME/nokia-fastmile-ha.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 4: Create First Release

1. Go to your repository on GitHub
2. Click **Releases** → **Create a new release**
3. Fill in release details:
   - **Tag version**: `v1.0.0`
   - **Release title**: `v1.0.0 - Initial Release`
   - **Description**: Copy from CHANGELOG.md
4. Click **Publish release**

---

## Adding to HACS

### Option 1: Add as Custom Repository (Immediate)

Users can add your integration immediately as a custom repository:

1. In Home Assistant, open HACS
2. Go to **Integrations**
3. Click **⋮** (three dots) → **Custom repositories**
4. Add URL: `https://github.com/YOUR_USERNAME/nokia-fastmile-ha`
5. Category: **Integration**
6. Click **Add**

**Share these instructions with users in your README.**

### Option 2: Submit to HACS Default Repository (Official)

To get your integration listed in the default HACS repository:

1. Ensure your repository meets [HACS requirements](https://hacs.xyz/docs/publish/start)
2. Create a submission issue at [HACS/integration](https://github.com/hacs/integration/issues/new/choose)
3. Fill in the template with your repository details
4. Wait for review and approval

**Requirements checklist:**
- ✅ Public GitHub repository
- ✅ Valid `hacs.json` file
- ✅ Valid `manifest.json` file
- ✅ README with installation instructions
- ✅ At least one release/tag
- ✅ No hard-coded credentials
- ✅ Proper error handling
- ✅ Follows Home Assistant guidelines

---

## Installing in Home Assistant

### Method 1: Via HACS (Recommended)

**For Custom Repository:**

1. Open HACS in Home Assistant
2. Go to **Integrations**
3. Click **⋮** → **Custom repositories**
4. Add: `https://github.com/YOUR_USERNAME/nokia-fastmile-ha`
5. Category: **Integration**
6. Click **Add**
7. Find "Nokia FastMile 5G" and click **Download**
8. Restart Home Assistant
9. Add integration via UI

**For Official HACS (after approval):**

1. Open HACS in Home Assistant
2. Search for "Nokia FastMile 5G"
3. Click **Download**
4. Restart Home Assistant
5. Add integration via UI

### Method 2: Manual Installation

```bash
# Download latest release
cd /tmp
wget https://github.com/YOUR_USERNAME/nokia-fastmile-ha/archive/refs/tags/v1.0.0.zip
unzip v1.0.0.zip

# Copy to Home Assistant
cp -r nokia-fastmile-ha-1.0.0/custom_components/nokia_fastmile /config/custom_components/

# Restart Home Assistant
ha core restart
```

---

## Maintenance and Updates

### Creating New Releases

When you make changes:

1. Update version in `manifest.json`
2. Update `CHANGELOG.md`
3. Commit changes:
   ```bash
   git add .
   git commit -m "Release v1.1.0: Added feature X"
   git push
   ```
4. Create new release on GitHub with the new tag

### Handling Issues

1. Monitor [GitHub Issues](https://github.com/YOUR_USERNAME/nokia-fastmile-ha/issues)
2. Respond to user questions
3. Fix bugs and create new releases
4. Update documentation as needed

### Community Support

Consider creating:
- **GitHub Discussions** for Q&A
- **Wiki** for extended documentation
- **Community forum thread** on Home Assistant forums

---

## Testing Checklist

Before each release, test:

- [ ] Installation via HACS
- [ ] Installation manually
- [ ] Configuration flow
- [ ] All sensors update correctly
- [ ] Reboot button works
- [ ] Options flow works
- [ ] Error handling (wrong credentials, offline device)
- [ ] Removal and reinstallation
- [ ] Multiple devices (if applicable)
- [ ] Different Home Assistant versions

---

## Repository Structure

Final structure:
```
nokia-fastmile-ha/
├── custom_components/
│   └── nokia_fastmile/
│       ├── __init__.py
│       ├── button.py
│       ├── config_flow.py
│       ├── const.py
│       ├── manifest.json
│       ├── nokia_api.py
│       ├── sensor.py
│       ├── strings.json
│       └── translations/
│           └── en.json
├── .gitignore
├── CHANGELOG.md
├── hacs.json
├── INFO.md
├── INSTALLATION.md
├── LICENSE
└── README_INTEGRATION.md
```

**Rename README_INTEGRATION.md to README.md before publishing:**
```bash
mv README_INTEGRATION.md README.md
```

---

## Quick Start Commands

```bash
# 1. Update URLs in files (replace YOUR_USERNAME)
find . -type f -name "*.md" -exec sed -i 's/yourusername/YOUR_USERNAME/g' {} +
find . -type f -name "*.json" -exec sed -i 's/yourusername/YOUR_USERNAME/g' {} +

# 2. Rename main README
mv README_INTEGRATION.md README.md

# 3. Initialize and push to GitHub
cd /home/daniel/NokiaFastMile
git init
git add .
git commit -m "Initial release v1.0.0"
git remote add origin https://github.com/YOUR_USERNAME/nokia-fastmile-ha.git
git branch -M main
git push -u origin main

# 4. Test locally first
cp -r custom_components/nokia_fastmile /config/custom_components/
ha core restart
```

---

## Need Help?

- **Home Assistant Development**: https://developers.home-assistant.io/
- **HACS Documentation**: https://hacs.xyz/docs/publish/start
- **Home Assistant Community**: https://community.home-assistant.io/
- **GitHub Help**: https://docs.github.com/

---

## Congratulations!

You've created a complete, production-ready Home Assistant integration! 🎉

Your integration includes:
- ✅ 17 sensors monitoring all aspects of your Nokia FastMile
- ✅ Reboot button for device control
- ✅ UI-based configuration
- ✅ HACS compatibility
- ✅ Complete documentation
- ✅ Proper error handling
- ✅ Professional repository structure

Share it with the community and help other Nokia FastMile users!
