#!/usr/bin/env node
/**
 * KYC/AML Agentic AI System - Frontend Server
 * Serves the web UI and provides a simple proxy for development
 */

const express = require('express');
const path = require('path');
const fs = require('fs');
const compression = require('compression');

const app = express();
const PORT = process.env.PORT || 3000;
const API_URL = process.env.API_URL || 'http://localhost:8000';

// Middleware
app.use(compression());

// Health check endpoint (MUST be before static middleware)
app.get('/health', (req, res) => {
    res.json({ status: 'healthy', service: 'frontend' });
});

// Serve enhanced index_with_steps.html for root route (SPA support)
// This MUST be before the static middleware to intercept / requests
app.get('/', (req, res) => {
    // Always serve the enhanced version with processing steps
    const enhancedPath = path.join(__dirname, 'index_with_steps.html');
    const defaultPath = path.join(__dirname, 'index.html');
    
    console.log('Serving root route...');
    console.log('Enhanced path exists:', fs.existsSync(enhancedPath));
    
    if (fs.existsSync(enhancedPath)) {
        console.log('✓ Serving index_with_steps.html');
        res.sendFile(enhancedPath);
    } else {
        console.log('✗ Falling back to index.html');
        res.sendFile(defaultPath);
    }
});

// Serve static assets with proper caching
app.use(express.static(path.join(__dirname, '.')));

app.use((req, res, next) => {
    if (req.path.match(/\.(js|css|png|jpg|jpeg|gif|svg|ico|woff|woff2|eot|ttf)$/)) {
        res.set('Cache-Control', 'public, max-age=604800');
    }
    next();
});

// API proxy for development (optional)
app.all('/api/*', (req, res) => {
    const url = API_URL + req.path.replace('/api', '');
    
    const proxyReq = require('http').request({
        hostname: new URL(API_URL).hostname,
        port: new URL(API_URL).port || 80,
        path: req.path.replace('/api', ''),
        method: req.method,
        headers: req.headers
    }, (proxyRes) => {
        proxyRes.on('data', (chunk) => res.write(chunk));
        proxyRes.on('end', () => res.end());
    });

    proxyReq.on('error', (e) => {
        console.error('Proxy error:', e);
        res.status(502).json({ error: 'Gateway error' });
    });

    req.on('data', (chunk) => proxyReq.write(chunk));
    req.on('end', () => proxyReq.end());
});

// Error handling
app.use((err, req, res, next) => {
    console.error('Server error:', err);
    res.status(500).json({ error: 'Internal server error' });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`
╔════════════════════════════════════════════════════╗
║   KYC/AML Agentic AI - Frontend Server             ║
╚════════════════════════════════════════════════════╝

✓ Frontend Server running on http://0.0.0.0:${PORT}
✓ Open your browser at http://localhost:${PORT}
✓ API Gateway: ${API_URL}

    `);
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('SIGTERM received. Shutting down gracefully...');
    process.exit(0);
});

process.on('SIGINT', () => {
    console.log('SIGINT received. Shutting down gracefully...');
    process.exit(0);
});

