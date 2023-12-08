const express = require('express');
const app = express();
const port = 3000; // You can use any port that is free on your system

// Serve static files from the 'public' directory
app.use(express.static('public'));

app.get('/', (req, res) => {
  res.sendFile(__dirname + '/public/index.html');
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}/`);
});