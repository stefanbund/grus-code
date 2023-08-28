/** 1.0: for chaser, store completed trades
store trade data for analysis, via csv
format an array for csv and initialize the writer object
'caps.csv' is now the middle ground for gladiator 1.6 and orderBookAnalysis
1.1: added two new csv writers for relevant bids and asks, will write to 2 files used by histogram
**/
const createCsvWriter = require('csv-writer').createObjectCsvWriter;
const filename = 'caps.csv'; //contain simply last two caps from oba

const bidWriter = createCsvWriter({
    path: 'relevantBids.csv',
    header: [
        {id: 'price', title: 'price'},
        {id: 'qty', title: 'qty'}
    ]
});

const askWriter = createCsvWriter({
    path: 'relevantAsks.csv',
    header: [
      {id: 'price', title: 'price'},
      {id: 'qty', title: 'qty'}
    ]
});

exports.writeRelevantArraysToCSV = function(csvBids, csvAsks)
{
  bidWriter.writeRecords(csvBids)       // returns a promise
      .then(() => {
          console.log('CM: RELEVANT BIDS, WRITTEN');
      });

  askWriter.writeRecords(csvAsks)       // returns a promise
      .then(() => {
          console.log('CM: RELEVANT ASKS, WRITTEN');
      });
}

const csvWriter = createCsvWriter({
    path: filename,
    header: [
        {id: 'bidCap', title: 'bidCap'},
        {id: 'askCap', title: 'askCap'}
    ]
});
exports.writeCapsToCSV = function(caps){
  console.log("write caps to csv: " + caps.bidCap + ", " + caps.askCap);
  writeArrayToCSV(caps);
}

function writeArrayToCSV(a)
{
  csvWriter.writeRecords(a)       // returns a promise
      .then(() => {
          console.log('write is Done');
          //completedTrades.length = 0;
      });
}

function setFileName()
{
  var ts = getMillisecondTimestampFilename();
  var ret = "./" + ts + "-file.csv";
  return ret;
}

function getMillisecondTimestampFilename()
{
  var d = new Date();
  return d.toString();
}
