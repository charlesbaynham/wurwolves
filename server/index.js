const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const path = require('path');
const cluster = require('cluster');
const numCPUs = require('os').cpus().length;

const isDev = process.env.NODE_ENV !== 'production';
const PORT = process.env.PORT || 3000;

// proxy middleware options
const options = {
  target: 'http://127.0.0.1:8000', // target host
  changeOrigin: false, // needed for virtual hosted sites
  ws: true, // proxy websockets
  // router: {
  //   // when request.headers.host == 'dev.localhost:3000',
  //   // override target 'http://www.example.org' to 'http://localhost:8000'
  //   'dev.localhost:3000': 'http://localhost:8000',
  // },
};

// static serving middleware options
const static_1_year_cache_options = {
  cacheControl: true,
  immutable: true,
  maxAge: "1y",
};

const static_dirs = [
  "static",
  "images"
]

// create the proxy (without context)
const apiProxy = createProxyMiddleware(options);

// Multi-process to utilize all CPU cores.
if (!isDev && cluster.isMaster) {
  console.error(`Node cluster master ${process.pid} is running`);

  // Fork workers.
  for (let i = 0; i < numCPUs; i++) {
    cluster.fork();
  }

  cluster.on('exit', (worker, code, signal) => {
    console.error(`Node cluster worker ${worker.process.pid} exited: code ${code}, signal ${signal}`);
  });

} else {
  const app = express();

  // Redirect all calls to "/api", "/docs" or the API spec to the FastAPI backend
  app.use('/api', apiProxy);
  app.use('/docs', apiProxy);
  app.use('/openapi.json', apiProxy);

  // Serve static files with a 1-year cache
  for (const static_dir of static_dirs) {
    app.use("/" + static_dir,
      express.static(path.resolve(__dirname, '../react-ui/build/' + static_dir), static_1_year_cache_options)
    );
  }

  // Serve remaining static files (which might change) with "no-cache" which does
  // cache them, but checks the cache validity each time
  app.use(express.static(path.resolve(__dirname, '../react-ui/build')));

  // All remaining requests return the React app, so it can handle routing.
  app.get('*', function (request, response) {
    response.sendFile(path.resolve(__dirname, '../react-ui/build', 'index.html'));
  });

  app.listen(PORT, function () {
    console.error(`Node ${isDev ? 'dev server' : 'cluster worker ' + process.pid}: listening on port ${PORT}`);
  });
}
