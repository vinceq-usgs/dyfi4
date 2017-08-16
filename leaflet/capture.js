var page = require('webpage').create();
page.open('viewer.html', function() {
  // staticImage module is running this in cwd='./leaflet'
  console.log('Rendering viewer.html');
  page.render('screenshot.png');
  console.log('Created screenshot.png');
  phantom.exit();
});
