const http = require('http');
const server = require('../src/index');

function testRoot() {
  const options = { hostname: '127.0.0.1', port: 3000, path: '/', method: 'GET' };
  const req = http.request(options, (res) => {
    let data = '';
    res.on('data', chunk => data += chunk);
    res.on('end', () => {
      try {
        const json = JSON.parse(data);
        if (res.statusCode === 200 && json.status === 'ok') {
          console.log('TEST PASS: root health check');
          process.exit(0);
        }
        console.error('TEST FAIL: unexpected response', res.statusCode, data);
        process.exit(2);
      } catch (err) {
        console.error('TEST FAIL: invalid json', err.message);
        process.exit(3);
      }
    });
  });
  req.on('error', (e) => { console.error('TEST FAIL: request error', e.message); process.exit(4); });
  req.end();
}

// give server a moment to start
setTimeout(testRoot, 200);
