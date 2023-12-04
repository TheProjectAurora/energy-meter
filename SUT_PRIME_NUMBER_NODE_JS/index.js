const express = require('express');
const app = express();
const port = 3000;
const path = require('path');

let lastPrime = 2;

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

app.use(express.static(path.join(__dirname)));

app.get('/', (req, res) => {
    res.send(`
    <html>
      <head>
        <title>Simple Node.js Page</title>
        <link rel="stylesheet" type="text/css" href="style.css">
        <script>
          let primeCount = 0;

          function sendCalculateRequest() {
            fetch('/calculate?start=2&count=5000')
              .then(response => response.text())
              .then(data => {
                const container = document.getElementById('primeContainer');
                container.innerText = data;
                container.style.display = 'block';
                document.getElementById('calculateButton').style.display = 'none';
              })
              .catch(error => console.error('Error:', error));
          }

          function requestNextPrime() {
              if (primeCount >= 5000) {
                  document.getElementById('primeContainer').innerText = 'Reached 5000 prime numbers!';
                  return;
              }

              document.getElementById('primeContainer').innerText = \`Requesting prime number \${primeCount + 1}...\`;

              setTimeout(() => {
                  fetch('/nextPrime')
                      .then(response => response.text())
                      .then(data => {
                          document.getElementById('primeContainer').innerText = data;
                          primeCount++;
                          requestNextPrime();
                      })
                      .catch(error => {
                          console.error('Error:', error);
                          document.getElementById('primeContainer').innerText = 'Error fetching prime number';
                      });
              }, 2000);
          }
        </script>
      </head>
      <body>
        <div class="content-container">
          <button id="calculateButton" onclick="sendCalculateRequest()">Calculate the first 5000 prime numbers</button>
          <button id="nextPrimesButton" onclick="requestNextPrime()">Request the next prime number</button>
          <div id="primeContainer"></div>
        </div>
      </body>
    </html>
  `);
});

app.get('/calculate', (req, res) => {
    const start = parseInt(req.query.start, 10);
    const count = parseInt(req.query.count, 10);
    const primes = calculatePrime(start, count);
    res.send(`Prime Numbers:\n\n${primes.join(', ')}`);
});

app.get('/nextPrime', (req, res) => {
    const nextPrime = calculatePrime(lastPrime + 1, 1)[0];
    lastPrime = nextPrime;
    res.send(`The next prime number is: ${nextPrime}`);
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
