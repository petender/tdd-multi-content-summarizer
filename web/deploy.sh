#!/bin/bash

# Azure App Service deployment script for Next.js static export

echo "Starting deployment..."

# Install dependencies
echo "Installing dependencies..."
npm ci --production=false

# Build the Next.js application
echo "Building Next.js application..."
npm run build

# Verify the output directory exists
if [ ! -d "out" ]; then
    echo "ERROR: 'out' directory not found after build!"
    exit 1
fi

echo "Build completed successfully!"
echo "Contents of 'out' directory:"
ls -la out

echo "Deployment preparation complete!"
