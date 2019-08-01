var Sequelize = require('sequelize')


module.exports = {


    getLeastFluffyWebsite: function(context, sequelize) {
        return new Promise(function (resolve, reject) {
            let sql = 'select Source, avg(numwordsbeforerecipe) AvgWordsBeforeRecipe from recipes.recipes group by source \
                        order by AvgWordsBeforeRecipe';
            sequelize.query(sql, {
                logging: context.log, plain: false, raw: true,
                type: Sequelize.QueryTypes.SELECT
            }).then(function(result) {
                resolve(result);
            }).catch(error => {
                context.log("ERROR: ", error)
                reject(error);
            });
        });
    },

    getRecipesBySource: function(context, sequelize, source) {
        return new Promise(function (resolve, reject) {
            let sql = "select top 5 Source, Title, NumWordsBeforeRecipe, FullPath as Link, EstimatedTime, Author from recipes.recipes where source= :source ORDER BY NEWID()";
            sequelize.query(sql, {
                logging: context.log, plain: false, raw: true, 
                replacements: {source: source},
                type: Sequelize.QueryTypes.SELECT
            }).then(function(result) {
                context.log("SUCCESSFULLY RECEIVED RESULTS ", result);
                resolve(result);
            }).catch(error => {
                context.log("ERROR: ", error)
                reject(error);
            });
        });
    },

    getRecipesByTopic: function(context, sequelize, topic) {
        return new Promise(function (resolve, reject) {
            topic = '%' + topic + '%'
            let sql = "select Source, Title, NumWordsBeforeRecipe, FullPath as Link, EstimatedTime, Author from recipes.recipes where title LIKE :topic";
            sequelize.query(sql, {
                logging: context.log, plain: false, raw: true, 
                replacements: {topic: topic},
                type: Sequelize.QueryTypes.SELECT
            }).then(function(result) {
                context.log("SUCCESSFULLY RECEIVED RESULTS ", result);
                resolve(result);
            }).catch(error => {
                context.log("ERROR: ", error)
                reject(error);
            });
        });
    },

    getRandomRecipes: function(context, sequelize) {
        return new Promise(function (resolve, reject) {
            let sql = "SELECT TOP 5 Source, Title, NumWordsBeforeRecipe, FullPath as Link, EstimatedTime, Author FROM recipes.recipes ORDER BY NEWID()";
            sequelize.query(sql, {
                logging: context.log, plain: false, raw: true, 
                type: Sequelize.QueryTypes.SELECT
            }).then(function(result) {
                context.log("SUCCESSFULLY RECEIVED RESULTS ", result);
                resolve(result);
            }).catch(error => {
                context.log("ERROR: ", error)
                reject(error);
            });
        });
    },

}
