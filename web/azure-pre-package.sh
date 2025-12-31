#!/bin/bash
echo "Building Next.js application..."
npm ci
npm run build
echo "Build complete. Contents of out directory:"
ls -la out/
