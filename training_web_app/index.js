const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');

const app = express();
const PORT = 3000;

app.set('view engine', 'ejs');
app.use(bodyParser.urlencoded({ extended: true }));

// Read JSON file and load the dataset
let dataset = JSON.parse(fs.readFileSync('data.json', 'utf-8'));
let currentIndex = 0;

app.get('/', (req, res) => {
  if (currentIndex < dataset.length) {
    res.render('index', { entry: dataset[currentIndex], index: currentIndex, total: dataset.length });
  } else {
    res.send('All entries have been labeled.');
  }
});

app.post('/label', (req, res) => {
  const { index, label } = req.body;
  dataset[index].label = label;
  fs.writeFileSync('labeled_dataset.json', JSON.stringify(dataset, null, 2));
  
  // Move to the next entry
  currentIndex++;
  if (currentIndex < dataset.length) {
    res.redirect('/');
  } else {
    res.send('All entries have been labeled.');
  }
});

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
