"use strict";

/*
TODO: Documentation

*/

var viewportWidth = 612;
var viewportHeight = 584;
var clipWidth = 200;
var clipHeight = 200;
var quality = 65;

var fs = require("fs");
var system = require("system");

var args = system.args;
if (args.length < 3) {
    console.log("Usage: phantomjs capture.js data.js output.[png,jpg] [-thumbnail]");
    console.log("data.js: file that contains event GeoJSON data");
    console.log("output.png: output image file");

    phantom.exit();
}

var input = args[1];
var output = args[2];
var thumbnail = args[3];

var template = "viewer.html.template";
var tmpinput = "tmp.viewer." + system.pid + ".html";

// Rather than mess around with CORS, async JS calls, etc.,
// easier to just make a temporary copy of the viewer.html that
// reads a temporary data.js file

var html = fs.read(template).replace(/__DATAFILE__/g,input);

if (thumbnail) {
    html = html.replace(/__THUMBNAIL__/g,"1");
}
else {
    html = html.replace(/__THUMBNAIL__/g,"0");
}

var f = fs.open(tmpinput,{mode:"w",charset:"UTF=8"});
f.writeLine(html);
f.close();

// Now read and render this file

var page = require("webpage").create();
page.viewportSize = { width: viewportWidth, height: viewportHeight };
//page.evaluate(function() { document.body.bgColor = "white"; });
//page.paperSize = { width: "612px", height: "684px", margin: "0px" };

if (thumbnail) {
    var clipLeft = Math.floor((viewportWidth - clipWidth)/2);
    var clipTop = Math.floor((viewportHeight - clipHeight)/2);
    
    page.clipRect = {left: clipLeft, top: clipTop, width: clipWidth, height: clipHeight};
}

page.open(tmpinput,function(status) { 

    if (status !== 'success') {
        console.log('Unable to load '+tmpinput);
        phantom.exit();
    }

    page.render(output, {'quality': quality});

    // If we make it to this point, delete the temporary file
    fs.remove(tmpinput);
    phantom.exit(1);
});

