var createError = require('http-errors');
var express = require('express');
var path = require('path');
var cookieParser = require('cookie-parser');
var logger = require('morgan');
var cloudant = require('@cloudant/cloudant');
var cloudantCredential = require('./cloudent-credential.json');
var cors = require('cors');
var moment = require('moment');

var cloudantConnexion = cloudant({
  url: cloudantCredential.url
});

var isactivatedRouter = require('./routes/isactivated');
var movingRouter = require('./routes/moving');
var accelerationRouter  = require('./routes/acceleration');

var app = express();

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'jade');

app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));
app.use(cors());

app.use(function(req, res, next) {
  var database;
  cloudantConnexion.db.list()
  .then((results) => {
    let date = moment().format('YYYY-MM-DD');
    let splitdb;
    results.forEach((dbName) => {
      splitdb = dbName.split('_');
      if(splitdb[2] === 'antivol' && splitdb[3] === date){
        database = cloudantConnexion.db.use(dbName);
        res.locals.db = database;
        next();
      }
    })
  });
}); 

app.use('/isactivated', isactivatedRouter);
app.use('/moving', movingRouter);
app.use('/acceleration', accelerationRouter);


// error handler
app.use(function(err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});

app.listen(process.env.PORT);

module.exports = app;
