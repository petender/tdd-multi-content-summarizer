# Azure pre-package hook for Windows
Write-Host "Building Next.js application..." -ForegroundColor Cyan
npm ci
npm run build
Write-Host "Build complete. Contents of out directory:" -ForegroundColor Green
Get-ChildItem out
