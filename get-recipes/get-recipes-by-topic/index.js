var Sequelize = require('sequelize');
var dbConnection = require('../shared-code/dbConnection');
var dataHandler = require('../shared-code/dataHandler');

module.exports = function (context, req) {
    context.log('Calling get-recipes-by-topic');

    if (!req.query.topic) {
        context.res = {
            status: 400,
            body: "Please enter in a topic as a query parameter"
        };
        context.done();
    }

    let topic = req.query.topic;

    let sequelize = dbConnection.getDbConnection();

    sequelize.authenticate()
    .then(() => {
        dataHandler.getRecipesByTopic(context, sequelize, topic).then(
            function(resp) {
                
                if (resp.length === 0) {
                    context.res = {
                        status: 404,
                        body: "We have no collected recipes on requested topic."
                    }
                } else {
                    context.res = {
                        status: 200,
                        body: resp
                    };
                }
                context.done();
            }
        )
        
    }).catch(err => {
        context.log('ERROR: ', err);
        context.res = {
            status: 500,
            body: "Internal Server Error"
        };
        context.done();
    });
};