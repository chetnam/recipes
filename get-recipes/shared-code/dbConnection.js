
var Sequelize = require('sequelize');

let db_user = process.env['db_user'];
let db_pwd = process.env['db_pwd'];
let database_name = process.env['db_name'];
let server_name = process.env['db_svr'];
let server_address = server_name + '.database.windows.net';

module.exports = {

    getDbConnection: function() {
        return new Sequelize(database_name, db_user, db_pwd, {
            host: server_address,
            port: 1433,
            dialect: 'mssql',
            dialectOptions: {
                encrypt: true
            },
            pool: {
                max: 5,
                min: 0,
                acquire: 300000,
                idle: 10000
            },
        });
    }
}
