#!/usr/bin/env node
/**
 * Temporary API Server for Decision App
 * Node.js server to provide API endpoints for the React frontend
 */

const express = require('express');
const cors = require('cors');
const app = express();
const port = 8001;

// Middleware
app.use(cors({
    origin: ['http://localhost:3000', 'http://localhost:5173'],
    credentials: true
}));
app.use(express.json());

// Mock data
const supportedSymbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT'];

const mockRecommendations = {
    'BTCUSDT': { recommendation: 'BUY', confidence: 0.75 },
    'ETHUSDT': { recommendation: 'HOLD', confidence: 0.65 },
    'ADAUSDT': { recommendation: 'SELL', confidence: 0.55 },
    'SOLUSDT': { recommendation: 'BUY', confidence: 0.70 },
    'BNBUSDT': { recommendation: 'HOLD', confidence: 0.60 },
    'XRPUSDT': { recommendation: 'BUY', confidence: 0.68 }
};

// Routes
app.get('/', (req, res) => {
    res.json({
        message: 'One Trade API - Temporary Server',
        version: '1.0.0',
        timestamp: new Date().toISOString()
    });
});

app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        components: {
            api: true,
            database: true,
            recommendations: true
        }
    });
});

app.get('/api/v1/enhanced-recommendations/supported-symbols', (req, res) => {
    res.json(supportedSymbols);
});

app.get('/api/v1/enhanced-recommendations/generate/:symbol', (req, res) => {
    const { symbol } = req.params;
    const { timeframe = '1d', days = 30 } = req.query;
    
    const symbolUpper = symbol.toUpperCase();
    const mockData = mockRecommendations[symbolUpper] || { recommendation: 'HOLD', confidence: 0.60 };
    
    res.json({
        symbol: symbolUpper,
        recommendation: mockData.recommendation,
        confidence: mockData.confidence,
        timestamp: new Date().toISOString(),
        details: {
            timeframe,
            days: parseInt(days),
            strategy: 'mock_strategy',
            indicators: {
                rsi: Math.random() * 100,
                macd: (Math.random() - 0.5) * 0.01,
                bollinger_position: Math.random()
            }
        }
    });
});

app.get('/api/v1/strategies', (req, res) => {
    res.json({
        strategies: ['RSI Strategy', 'MACD Strategy', 'Bollinger Bands Strategy'],
        timestamp: new Date().toISOString()
    });
});

app.get('/api/v1/backtests/:symbol', (req, res) => {
    const { symbol } = req.params;
    
    res.json({
        symbol: symbol.toUpperCase(),
        strategy: 'RSI Strategy',
        total_trades: Math.floor(Math.random() * 50) + 20,
        win_rate: Math.random() * 0.4 + 0.5, // 50-90%
        total_return: (Math.random() - 0.5) * 0.4, // -20% to +20%
        sharpe_ratio: Math.random() * 2 + 0.5, // 0.5 to 2.5
        max_drawdown: Math.random() * 0.15, // 0-15%
        timestamp: new Date().toISOString()
    });
});

app.get('/api/v1/market-data/:symbol', (req, res) => {
    const { symbol } = req.params;
    const { timeframe = '1d', days = 30 } = req.query;
    
    const basePrice = symbol.toUpperCase() === 'BTCUSDT' ? 50000 : 3000;
    const data = [];
    const currentTime = new Date();
    
    for (let i = 0; i < parseInt(days); i++) {
        const price = basePrice * (1 + (i * 0.001) + (Math.random() - 0.5) * 0.02);
        data.push({
            timestamp: new Date(currentTime - i * 24 * 60 * 60 * 1000).toISOString(),
            price: Math.round(price * 100) / 100,
            volume: Math.floor(Math.random() * 1000000) + 500000
        });
    }
    
    res.json({
        symbol: symbol.toUpperCase(),
        timeframe,
        days: parseInt(days),
        data: data.reverse(),
        timestamp: new Date().toISOString()
    });
});

// Error handling
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Something went wrong!' });
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({ error: 'Endpoint not found' });
});

// Start server
app.listen(port, () => {
    console.log('='.repeat(60));
    console.log('🚀 One Trade API - Temporary Node.js Server');
    console.log('='.repeat(60));
    console.log();
    console.log(`📡 Server running on: http://localhost:${port}`);
    console.log('🔗 API Base URL: http://localhost:8000');
    console.log('📊 Health Check: http://localhost:8000/health');
    console.log('📋 Supported Symbols:', supportedSymbols.join(', '));
    console.log();
    console.log('⚡ Press Ctrl+C to stop the server');
    console.log('='.repeat(60));
    console.log();
});
