const repl = require('repl');
const pkg = require('./package.json');
const crypto = require('crypto');
const util = require('./util.js');

const startRepl = function(instream, outstream) {

  // check for Node.js global variables and move those values to Python
  const globalVariableChecker = function() {

    // get list of global variables
    var varlist = Object.getOwnPropertyNames(r.context);

    // trim the list
    const cutoff = varlist.indexOf('help') + 1;
    varlist.splice(0, cutoff);

    // if there aren't any, we're done
    if (varlist.length === 0) return;

    // for each global
    for(var i in varlist) {

      // turn it to JSON
      const v = varlist[i];
      const j = JSON.stringify(r.context[v]);

      // if it's a string
      if (typeof j === 'string' ) {

        // calculate the md5(json)
        const h = hash(j);

        // it it's different to what we had last time
        if (lastGlobal[v] !== h) {

          // check to see if this is a simple data structure i.e.
          // only migrate variables which equal to the JSON.parse'd version of their JSON.stringified selves
          // i.e don't migrate objects that contain functions
          if (util.deepEqual(JSON.parse(j), r.context[v])) {

            // if we reached here, then we're going to move a variable from Node.js --> Python
            
            // calculate data type
            const datatype = isArray(r.context[v]) && typeof r.context[v][0] === 'object' ? 'array' : typeof r.context[v];
            
            // make a special JSON object
            const obj = { _pixiedust: true, type: 'variable', key: v, datatype: datatype, value: r.context[v] };
            
            // write it to stdout for the Python parser to find
            outstream.write('\n' + JSON.stringify(obj) + '\n')

            // store it in our lastGLobal dictionary - so that we only update it when the value changes
            lastGlobal[v] = h;
          }
        }
      }
    }
  };

  // sync Node.js to Python every 1 second
  interval = setInterval(globalVariableChecker, 1000);
  interval.unref();

  // custom writer function that outputs nothing
  const writer = function(output) {
    globalVariableChecker();
    // don't output anything
    return '';
  };

  const options = {
    input: instream,
    output: outstream,
    prompt: '',
    writer: writer
  };
  const r = repl.start(options);
  var lastGlobal = {};
  var interval = null;

  // generate hash from data
  const hash = function(data) {
    return crypto.createHash('md5').update(data).digest("hex");
  }

  const isArray = Array.isArray || function(obj) {
    return obj && toString.call(obj) === '[object Array]';
  };

  // custom print function for Notebook interface
  const print = function(data) {
    // bundle the data into an object
    globalVariableChecker();
    const obj = { _pixiedust: true, type: 'print', data: data };
    outstream.write(JSON.stringify(obj) + '\n');
  };

  // custom display function for Notebook interface
  const display = function(data) {
    // bundle the data into an object
    globalVariableChecker();
    const obj = { _pixiedust: true, type: 'display', data: data };
    outstream.write(JSON.stringify(obj) + '\n');

  };

  // custom display function for Notebook interface
  const store = function(data, variable) {
    globalVariableChecker();
    if (!data && !variable) return;
    // bundle the data into an object
    const obj = { _pixiedust: true, type: 'store', data: data, variable: variable };
    outstream.write(JSON.stringify(obj) + '\n');
   
  };

  // display html in Notebook cell
  const html = function(data) {
    // bundle the data into an object
    const obj = { _pixiedust: true, type: 'html', data: data};
    outstream.write(JSON.stringify(obj) + '\n');
    globalVariableChecker();
  };

  // display image in Notebook cell
  const image = function(data) {
    // bundle the data into an object
    const obj = { _pixiedust: true, type: 'image', data: data};
    outstream.write(JSON.stringify(obj) + '\n');
    globalVariableChecker();
  };

  const help = function() {
    console.log(pkg.name, pkg.version);
    console.log(pkg.repository.url);
    console.log();
    console.log("JavaScript functions:");
    console.log("* print(x) - print out x");
    console.log("* display(x) - turn x into Pandas dataframe and display with Pixiedust");
    console.log("* html(x) - display HTML x in Notebook cell");
    console.log("* image(x) - display image URL x in a Notebook cell");
    console.log("* help() - display help");
    console.log();
    console.log("Python helpers:");
    console.log("* npm.install(x) - install npm package x");
    console.log("* npm.uninstall(x) - remove npm package x");
    console.log("* npm.list() - list installed npm packages");
    console.log("* node.cancel() - cancel Node.js execution");
    console.log("* node.clear() - clear and reset the Node.js engine");
    console.log("* node.help() - view help")
  };

  // add silverlining library and print/display
  var resetContext = function() {
    r.context.print = print;
    r.context.display = display;
    r.context.store = store;
    r.context.html = html;
    r.context.image = image;
    r.context.help = help;
    lastGlobal = {};
  };

  // add print/disply/store back in on reset
  r.on('reset', resetContext);

  // reset the context
  resetContext();

  return r;
};

startRepl(process.stdin, process.stdout);
console.log(pkg.name, pkg.version, "started. Cells starting '%%node' may contain Node.js code.");
