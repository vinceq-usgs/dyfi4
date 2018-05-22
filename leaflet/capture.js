"use strict";

/*
TODO: Documentation

*/

var fs = require("fs");
var system = require("system");

var args = system.args;
if (args.length < 3) {
    console.log("Usage: phantomjs capture.js data.js output.png");
    console.log("data.js: file that contains event GeoJSON data");
    console.log("output.png: output image file");

    phantom.exit();
}

var input = args[1];
var output = args[2];

var template = "viewer.html.template";
var tmpinput = "tmp.viewer." + system.pid + ".html";

// Rather than mess around with CORS, async JS calls, etc.,
// easier to just make a temporary copy of the viewer.html that
// reads a temporary data.js file

var html = fs.read(template).replace("__DATAFILE__",input);

console.log("Saving to " + tmpinput);
var f = fs.open(tmpinput,{mode:"w",charset:"UTF=8"});
f.writeLine(html);
f.close();


// Now read and render this file

var page = require("webpage").create();
page.open(tmpinput,function() { 

  // Set page size and other settings here

  page.viewportSize = { width: 612, height: 684 };
  //page.paperSize = { width: "612px", height: "684px", margin: "0px" };
  //page.evaluate(function() { document.body.bgColor = "white"; });

  console.log("Now rendering to " + output);
  page.render(output);

  // If we make it to this point, delete the temporary file
  fs.remove(tmpinput);
  phantom.exit(1);
});

