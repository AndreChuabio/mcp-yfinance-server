const http = require('http');

function testEndpoint(method, path, body = null) {
    return new Promise((resolve, reject) => {
        const options = {
            hostname: 'localhost',
            port: 3000,
            path: path,
            method: method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        const req = http.request(options, (res) => {
            let data = '';

            res.on('data', (chunk) => {
                data += chunk;
            });

            res.on('end', () => {
                try {
                    const parsed = JSON.parse(data);
                    resolve({ status: res.statusCode, data: parsed });
                } catch (error) {
                    resolve({ status: res.statusCode, data: data });
                }
            });
        });

        req.on('error', (error) => {
            reject(error);
        });

        if (body) {
            req.write(JSON.stringify(body));
        }

        req.end();
    });
}

async function runTests() {
    console.log('Starting sentiment analysis tests...\n');

    try {
        console.log('Test 1: Health check');
        const health = await testEndpoint('GET', '/');
        console.log(`Status: ${health.status}`);
        console.log(`Response:`, health.data);
        console.log(health.status === 200 ? 'PASSED' : 'FAILED');
        console.log('');

        console.log('Test 2: Single ticker sentiment analysis');
        const ticker = await testEndpoint('GET', '/sentiment/ticker/AAPL');
        console.log(`Status: ${ticker.status}`);
        console.log(`Response:`, JSON.stringify(ticker.data, null, 2));
        console.log(ticker.status === 200 && ticker.data.ticker ? 'PASSED' : 'FAILED');
        console.log('');

        console.log('Test 3: Single ticker with social sentiment');
        const tickerSocial = await testEndpoint('GET', '/sentiment/ticker/TSLA?social=true');
        console.log(`Status: ${tickerSocial.status}`);
        console.log(`Ticker: ${tickerSocial.data.ticker}`);
        console.log(`Score: ${tickerSocial.data.sentiment_score}`);
        console.log(`Sources: ${tickerSocial.data.sources_analyzed}`);
        console.log(tickerSocial.status === 200 && tickerSocial.data.source_breakdown ? 'PASSED' : 'FAILED');
        console.log('');

        console.log('Test 4: Batch ticker analysis');
        const batch = await testEndpoint('POST', '/sentiment/analyze', {
            tickers: ['AAPL', 'MSFT', 'GOOGL'],
            includeSocial: false,
            newsLimit: 10
        });
        console.log(`Status: ${batch.status}`);
        console.log(`Tickers analyzed: ${Object.keys(batch.data).length}`);
        console.log(`Response:`, JSON.stringify(batch.data, null, 2));
        console.log(batch.status === 200 && Object.keys(batch.data).length === 3 ? 'PASSED' : 'FAILED');
        console.log('');

        console.log('Test 5: Historical sentiment');
        const history = await testEndpoint('GET', '/sentiment/ticker/AAPL/history?days=7');
        console.log(`Status: ${history.status}`);
        console.log(`Response:`, JSON.stringify(history.data, null, 2));
        console.log(history.status === 200 && history.data.ticker ? 'PASSED' : 'FAILED');
        console.log('');

        console.log('Test 6: Trending tickers');
        const trending = await testEndpoint('GET', '/sentiment/trending?tickers=AAPL,TSLA,NVDA&threshold=0.2');
        console.log(`Status: ${trending.status}`);
        console.log(`Response:`, JSON.stringify(trending.data, null, 2));
        console.log(trending.status === 200 && trending.data.trending ? 'PASSED' : 'FAILED');
        console.log('');

        console.log('Test 7: Invalid ticker');
        const invalid = await testEndpoint('GET', '/sentiment/ticker/');
        console.log(`Status: ${invalid.status}`);
        console.log(`Response:`, invalid.data);
        console.log(invalid.status === 400 ? 'PASSED' : 'FAILED');
        console.log('');

        console.log('Test 8: Invalid batch request');
        const invalidBatch = await testEndpoint('POST', '/sentiment/analyze', { invalid: 'data' });
        console.log(`Status: ${invalidBatch.status}`);
        console.log(`Response:`, invalidBatch.data);
        console.log(invalidBatch.status === 400 ? 'PASSED' : 'FAILED');
        console.log('');

        console.log('All tests completed');
    } catch (error) {
        console.error('Test error:', error.message);
        console.log('Make sure the server is running on port 3000');
        process.exit(1);
    }
}

runTests();
