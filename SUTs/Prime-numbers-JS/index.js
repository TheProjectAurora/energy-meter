const express = require('express');
const app = express();
const port = 3000;
const path = require('path');

let globalLastPrime = 2; // Keep track of the last prime number globally

app.use(express.static(path.join(__dirname)));

app.get('/', (req, res) => {
    res.send(`
    <html>
      <head>
        <title>Simple Node.js Page</title>
        <link rel="stylesheet" type="text/css" href="style.css">
        <script>
          let primeCount = 0;
          let primeNumbers = [];
          let lastPrime = 1;

          document.addEventListener('DOMContentLoaded', () => {
              fetch('/currentPrime')
                  .then(response => response.json())
                  .then(data => {
                      lastPrime = data.currentPrime - 1;
                  })
                  .catch(error => console.error('Error:', error));
          });

          function sendCalculateRequest() {
            const count = document.getElementById('primeNumberInput').value;
            fetch('/calculate?start=2&count=' + count)
              .then(response => response.text())
              .then(data => {
                const container = document.getElementById('primeContainer');
                container.innerText = data;
                container.style.display = 'block';
              })
              .catch(error => console.error('Error:', error));
          }

          function requestNextPrime() {
            lastPrime = 1; // Reset lastPrime to 1 so that the next prime starts from 2
            fetchNextPrime();
          }

          function fetchNextPrime() {
            const totalCount = parseInt(document.getElementById('primeNumberInput').value, 10);
            if (primeCount >= totalCount) {
                return;
            }
            fetch('/nextPrime?lastPrime=' + lastPrime)
                .then(response => response.text())
                .then(data => {
                    const nextPrime = data.split(': ')[1];
                    primeNumbers.push(nextPrime);
                    lastPrime = parseInt(nextPrime, 10);
                    const container = document.getElementById('primeContainer');
                    container.innerText = primeNumbers.join(', ');
                    primeCount++;
                    if (primeCount < totalCount) {
                        fetchNextPrime();
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('primeContainer').innerText = 'Error fetching prime number';
                });
          }

          function reset() {
            primeCount = 0;
            primeNumbers = [];
            lastPrime = 1;
            document.getElementById('primeContainer').innerText = 'Prime numbers will appear here';
            fetch('/reset?lastPrime=' + lastPrime)
                .catch(error => console.error('Error:', error));
          }
        </script>
      </head>
      <body>
        <div class="content-container">
          <div class="inputs-buttons-container">
            <div class="input-container">
              <label for="primeNumberInput">Prime numbers:</label>
              <input type="number" id="primeNumberInput" value="5000" min="1" />
            </div>
            <button id="calculateButton" onclick="sendCalculateRequest()">Calculate prime numbers</button>
            <button id="nextPrimesButton" onclick="requestNextPrime()">Request the next prime number</button>
            <button id="resetButton" onclick="reset()">C</button>
          </div>
          <div id="primeContainer">Prime numbers will appear here</div>
        </div>
      </body>
    </html>
  `);
});

app.get('/calculate', (req, res) => {
    const start = parseInt(req.query.start, 10);
    const count = parseInt(req.query.count, 10);
    const primes = calculatePrime(start, count);
    res.send(primes.join(', '));
});

app.get('/nextPrime', (req, res) => {
    let lastPrime = parseInt(req.query.lastPrime, 10) || globalLastPrime;
    const nextPrime = calculatePrime(lastPrime + 1, 1)[0];
    globalLastPrime = nextPrime;
    res.send(`The next prime number is: ${nextPrime}`);
});

app.get('/reset', (req, res) => {
    globalLastPrime = 2;
    res.send('Reset successful');
});

app.get('/currentPrime', (req, res) => {
    res.send({ currentPrime: globalLastPrime });
});

function calculatePrime(start, count) {
    let primes = [];
    let num = start;

    while (primes.length < count) {
        let isPrime = true;
        for (let i = 2; i <= Math.sqrt(num); i++) {
            if (num % i === 0) {
                isPrime = false;
                break;
            }
        }
        if (isPrime) {
            primes.push(num);
        }
        num++;
    }
    return primes;
}

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
