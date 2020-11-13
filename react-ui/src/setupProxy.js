// This file is only used for development: in production, the node server
// index.js is used instead
const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');

const PORT = process.env.PORT || 3000;

// proxy middleware options
const options = {
  target: 'http://127.0.0.1:8000', // target host
  changeOrigin: false,
  ws: true,
};

// create the proxy (without context)
const apiProxy = createProxyMiddleware(options);

module.exports = app => {
    // mount `apiProxy` in web server
    app.use('/api', apiProxy);
}
