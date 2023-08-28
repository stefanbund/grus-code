/**
csvManager
  takes an array of javascript objects and writes to a csv file, named at time of write.
  TO DO:
  enable one file to be overwritten as the program proceeds, to capture records before a crash (might) occur.
  v 1: writing to csv, using the active trade as a format for each row. can be called. I tried to empty completed trades, but will not for now,
  will limit writing to new csv every 30 seconds. This will grow, you should take the last file created as a final account
**/
const createCsvWriter = require('csv-writer').createObjectCsvWriter;
var sl = require('./strategyLogic');
var mj = require("mathjs");

const csvWriter = createCsvWriter({
    path: setFileName(),
    header: [
        {id: 'id', title: 'id'},
        {id: 'margin', title: 'margin'},
        {id: 'bidPrice', title: 'bidPrice'},
        {id: 'amt', title: 'amt'},
        {id: 'bidOrderTime', title: 'bidOrderTime'},
        {id: 'orderid', title: 'orderid'},
        {id: 'repricedAt', title: 'repricedAt'},
        {id: 'initialmp', title: 'initialmp'},
        {id: 'bidFillTime', title: 'bidFillTime'},
        {id: 'sellPrice', title: 'sellPrice'},
        {id: 'sellOrderTime', title: 'sellOrderTime'},
        {id: 'sellFillTime', title: 'sellFillTime'},
        {id: 'sold', title: 'sold'},
        {id: 'addedToBudget', title: 'addedToBudget'},
        {id: 'currencyPair', title: 'currencyPair'},
        {id: 'executed_value', title: 'executed_value'},
        {id: 'operatingBudget', title: 'operatingBudget'},
        {id: 'inFee', title: 'inFee'},
        {id: 'outFee', title: 'outFee'},
        {id: 'gain', title: 'gain'},
        {id: 'roi', title: 'roi'},
        {id: 'tpsid', title: 'tpsid'},
        {id: 'analysisID', title: 'analysisID'},
        {id: 'safeToTrade', title: 'safeToTrade'}
    ]
});

 exports.writeCompleteTradesToCSV = function(completedTrades)
{
  //console.log("completed trades array: " + completedTrades);
  for(var i = 0; i < completedTrades.length; i++)
  {
    //console.log(typeof completedTrades[i]);
    for (var key in completedTrades[i])
    {
      console.log("iterate this object: " + key, completedTrades[i][key]);
    }
    if(completedTrades[i] != undefined)
    {
      // var d2 = (completedTrades[i].bidPrice * completedTrades[i].amt);
      var d2 = mj.multiply(completedTrades[i].bidPrice, completedTrades[i].amt);
      completedTrades[i].inFee = sl.calcInFee(d2);
      //var d1 = (completedTrades[i].sellPrice * completedTrades[i].amt);
      var d1 = mj.multiply(completedTrades[i].sellPrice, completedTrades[i].amt);
      completedTrades[i].outFee = sl.calcEndFee(d1);
      // var earningsThisCycle = d1 - (completedTrades[i].inFee + completedTrades[i].endFee); //what you end up with after fees and gains
      var totalFees = mj.add(completedTrades[i].inFee, completedTrades[i].outFee);
      //var earningsThisCycle = mj.subtract(d1, totalFees);
      completedTrades[i].gain = mj.subtract(d1, d2);//d1 - d2;
      completedTrades[i].roi = sl.calcEndRoi(completedTrades[i].gain, completedTrades[i].amt);
    }
  }
  writeArrayToCSV(completedTrades);
}

function writeArrayToCSV(a)
{
  csvWriter.writeRecords(a)       // returns a promise
      .then(() => {
          console.log('write is Done');
          completedTrades.length = 0;
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

/** ******************/
