# Deployment Testing Guide

## Fresh Deployment Test (New Environment)

This document tracks testing for a completely fresh deployment from a cloned repository.

### Test Scenario: Clone → New Environment → Deploy

```bash
# 1. Clone repo
git clone <repo-url>
cd azd-demo-live

# 2. Create new environment
azd env new testenv123

# 3. Login to Azure
azd auth login

# 4. Deploy everything
azd up
```

### Expected Behavior

#### During `azd up`:

1. **Provision Phase**:
   - Creates two resource groups:
     - `rg-testenv123` (web app, storage, cosmos, monitoring)
     - `rg-testenv123-func` (Linux Functions)
   - Outputs `FUNCTIONS_URI` to environment: `https://func-{token}v2.azurewebsites.net`
   - Outputs `FUNCTIONS_APP_NAME` to environment: `func-{token}v2`

2. **Package Phase** (prepackage hooks run):
   - **For Web Service**:
     - Checks `azd env get-value FUNCTIONS_URI`
     - **ISSUE**: On first `azd up`, FUNCTIONS_URI may not be available yet
     - Falls back to placeholder: `window.__API_URL__ = '/api';`
     - Builds Next.js app (copies `public/config.js` → `out/config.js`)
   
   - **For API Service**:
     - No prepackage hook, just packages Python code

3. **Deploy Phase**:
   - Deploys API to `func-{token}v2` (uses FUNCTIONS_APP_NAME)
   - Deploys web to `app-{token}` (uses APPSERVICE_NAME)

### Known Issues & Solutions

#### Issue 1: First Deployment - Placeholder API URL

**Problem**: During the first `azd up` in a new environment, the prepackage hook for the web service runs before the FUNCTIONS_URI environment variable is persisted, resulting in `config.js` containing the placeholder `/api` instead of the actual function URL.

**Solution**: After the first `azd up` completes, run:
```bash
azd deploy web
```

This will:
1. Re-run the prepackage hook (FUNCTIONS_URI now exists)
2. Update `public/config.js` with correct function URL
3. Rebuild and redeploy the web app

#### Issue 2: Old Function App References

**Problem**: If you previously deployed to an environment that had a function app without the `v2` suffix (e.g., `func-{token}`), the old app may still exist and cause confusion.

**Solution**: 
- The infrastructure now uses separate resource groups to avoid conflicts
- New deployments always use the `v2` suffix
- Old function apps can be manually deleted from the Azure portal if needed

### Verification Checklist

After deployment, verify:

- [ ] Environment variables are set:
  ```bash
  azd env get-value FUNCTIONS_URI
  # Should show: https://func-{token}v2.azurewebsites.net
  
  azd env get-value FUNCTIONS_APP_NAME  
  # Should show: func-{token}v2
  
  azd env get-value APPSERVICE_NAME
  # Should show: app-{token}
  ```

- [ ] Web app `config.js` has correct URL:
  ```bash
  # Check the deployed config.js
  curl https://app-{token}.azurewebsites.net/config.js
  # Should show: window.__API_URL__ = 'https://func-{token}v2.azurewebsites.net/api';
  ```

- [ ] Function endpoints are accessible:
  ```bash
  curl https://func-{token}v2.azurewebsites.net/api/test-transcript
  # Should return JSON response
  ```

- [ ] Web app calls correct function URL:
  ```
  1. Open browser dev tools (Network tab)
  2. Navigate to https://app-{token}.azurewebsites.net/article
  3. Submit an article URL
  4. Verify XHR request goes to: https://func-{token}v2.azurewebsites.net/api/summarize-article
  ```

### Architecture Notes

#### Separate Resource Groups

The deployment creates two resource groups to avoid Azure platform limitations:

- **Main RG** (`rg-{env}`): App Service (Linux B1), Storage, Cosmos DB, OpenAI, Application Insights
- **Functions RG** (`rg-{env}-func`): Azure Functions (Linux Consumption Y1)

**Why?** Azure does not allow mixing Linux App Service plans (B1) and Linux Consumption Functions (Y1) in the same resource group.

#### Function App Naming

Function apps are created with a `v2` suffix: `func-{token}v2`

**Why?** To avoid conflicts if you're migrating from a Windows Functions deployment to Linux Functions in the same environment.

### Troubleshooting

#### "Failed to load resource: 404" in browser console

**Cause**: Web app is calling a function URL that doesn't exist.

**Check**:
1. View browser Network tab - what URL is being called?
2. Check `curl https://app-{token}.azurewebsites.net/config.js`
3. Compare with `azd env get-value FUNCTIONS_URI`

**Fix**:
```bash
azd deploy web
```

#### "ModuleNotFoundError" in Function App

**Cause**: Python dependencies not installed or wrong Python version.

**Fix**:
```bash
cd api
func azure functionapp publish $(azd env get-value FUNCTIONS_APP_NAME) --python
```

#### Web app shows "/api" in config.js

**Cause**: FUNCTIONS_URI wasn't available during prepackage hook.

**Fix**:
```bash
azd deploy web
```

### Automated Fresh Deployment (Recommended)

For a completely automated fresh deployment, use this two-step process:

```bash
# Step 1: Provision and initial deploy
azd up

# Step 2: Redeploy web with correct function URL
azd deploy web
```

This ensures the config.js always has the correct function URL, even on first deployment.
