var Sequelize = require('sequelize');
var dbConnection = require('../shared-code/dbConnection');
var dataHandler = require('../shared-code/dataHandler');

module.exports = function (context, req) {
    context.log('JavaScript HTTP trigger function processed a request.');

    let requestType;
    if (req.query.source) { 
        requestType = 'recipe'; // return 5 recipes from given source
    }
    else {
        requestType = 'info'; // returns sources by avg number of words before recipe
    }

    let sequelize = dbConnection.getDbConnection();

    sequelize.authenticate()
    .then(() => {
        if (requestType === 'info') {
            dataHandler.getLeastFluffyWebsite(context, sequelize).then(
                function(resp) {
                    
                    context.res = {
                        status: 200,
                        body: resp
                    };
                    context.done();
                }
            )
        } else {
            dataHandler.getRecipesBySource(context, sequelize, req.query.source).then(
                function(resp) {

                    if (resp.length === 0) {
                        context.res = {
                            status: 404,
                            body: "No recipes found for requested source"
                        };
                    } else {
                        context.res = {
                            status: 200,
                            body: resp
                        };
                    }

                    context.done();
                }
            )
            
        }
    }).catch(err => {
        context.log('ERROR: ', err);
        context.res = {
            status: 500,
            body: "Internal Server Error"
        };
        context.done();
    });
};