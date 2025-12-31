# YouTube Transcript Fetching - Cloud IP Blocking Issue

## Problem
YouTube blocks requests from cloud provider IPs (Azure, AWS, GCP) when using the `youtube-transcript-api` library. This causes transcript fetching to fail when the Azure Function is deployed.

**Error:** `RequestBlocked: YouTube is blocking requests from your IP`

## Why Rick Astley Worked But Other Videos Don't

- ✅ The Rick Astley video worked because you tested it **locally from your machine**
- ❌ Other videos fail because **Azure's IPs are blocked by YouTube**

## Current Behavior

The application works perfectly when:
- Running locally on your development machine
- The video has captions/subtitles available

The application fails when:
- Deployed to Azure Functions
- YouTube detects requests coming from Azure datacenter IPs

## Workaround Options

### Option 1: Use YouTube Official Transcript Feature (Recommended)
Instead of scraping, users can:
1. Open the YouTube video
2. Click the "..." menu → "Show transcript"
3. Copy and paste the transcript into the app
4. App processes the pasted transcript text

**Implementation**: Add a text area where users can paste transcripts directly.

### Option 2: Use a Proxy Service
Configure the app to route requests through a proxy:
- Requires setting up and paying for a proxy service
- May violate YouTube's Terms of Service
- Not recommended for production

### Option 3: Browser Extension Approach
Create a browser extension that:
- Runs in the user's browser (not from Azure)
- Fetches transcripts using the user's IP
- Sends results to your Azure Function

### Option 4: Accept the Limitation
Document that the service works best:
- For development/testing (run locally)
- For videos you've already tested locally
- Provide clear error messages guiding users to manual transcript copy/paste

## Recommended Solution: Add Manual Transcript Input

This is the most reliable approach. Update the web interface to support:

1. **Automatic mode** (try to fetch automatically - works locally)
2. **Manual mode** (user pastes transcript - always works)

Benefits:
- No API keys or quotas needed
- No Terms of Service concerns  
- Works 100% of the time
- Users maintain control over their data

## Technical Details

The application includes fallback logic:
1. Tries `youtube-transcript-api` first (free, works locally)
2. Catches `RequestBlocked` exception in Azure
3. Returns user-friendly error message

The code is in [api/shared/video_processor.py](api/shared/video_processor.py).

## Testing

To test locally (will work):
```powershell
python api/test_new_video.py
```

To test in Azure (will be blocked):
```powershell
python test_api_call.py
```
