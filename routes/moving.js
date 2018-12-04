var express = require('express');
var router = express.Router();

router.get('/', moving);
router.get('/:page', moving);

function moving(req, res, next){
   let page = 10;
   if(req.params.page){
       page = Number(req.params.page);
   }
    let db = res.locals.db;
    db.find(
        {
            selector: {
               _id: {
                  "$exists": true
               },
               data: {
                  isMoving: {
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
            limit: page
        },
    function(err, result) {
        res.json(result.docs);   
    })
}

module.exports = router;