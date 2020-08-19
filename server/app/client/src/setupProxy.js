const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function (app) {
  app.use(
    createProxyMiddleware(
      '/upload',
      {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    ),
    createProxyMiddleware(
      '/result',
      {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    )
  )
};
