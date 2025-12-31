#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

// Get API URL from environment variable (set by postprovision hook)
const apiUrl = process.env.API_URL || '/api';

// Create config.js with the API URL
const configPath = path.join(__dirname, 'config.js');
const configContent = `window.__API_URL__ = '${apiUrl}';`;

console.log('=== Startup Script ===');
console.log('API URL:', apiUrl);
console.log('Writing config.js to:', configPath);

fs.writeFileSync(configPath, configContent, 'utf8');
console.log('Created config.js');

// Start serve
console.log('Starting serve on port 8080...');
const serve = spawn('npx', ['serve@latest', '.', '-s', '-p', '8080'], {
  stdio: 'inherit',
  shell: true
});

serve.on('error', (err) => {
  console.error('Failed to start serve:', err);
  process.exit(1);
});

serve.on('exit', (code) => {
  console.log('serve exited with code:', code);
  process.exit(code || 0);
});
