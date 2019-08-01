var Sequelize = require('sequelize');
var dbConnection = require('../shared-code/dbConnection');
var dataHandler = require('../shared-code/dataHandler');

module.exports = function (context, req) {
    context.log('Calling get-random-recipes');

    let sequelize = dbConnection.getDbConnection();

    sequelize.authenticate()
    .then(() => {
        dataHandler.getRandomRecipes(context, sequelize).then(
            function(resp) {
                
                context.res = {
                    status: 200,
                    body: resp
                };
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