var express = require('express');
var router = express.Router();

var oldData = false;

router.get('/', function(req, res, next){
    let db = res.locals.db;
    db.find(
        {
            selector: {
               _id: {
                  "$exists": true
               },
               data: {
                  active: {
                     "$exists": true
                  }
               }
            },
            fields: [
               "data",
               "timestamp"
            ],
            sort: [
               {
                  "timestamp": "desc"
               }
            ],
            limit: 1
        },
    function(err, result) {
       if(result){
        oldData = result.docs[0].data.active;
        res.json(result.docs[0].data.active);   
       }else
        res.json(oldData);
    })
});

module.exports = router;