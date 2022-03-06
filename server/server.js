/*
    Dependencies:

    express:                Web Server Framework for nodejs
    http:                   Used to create a server
    path:                   Used to combine relative paths and show our app where its static files are, etc.
    mongoose:               Used as a wrapper for mongodb, we use it to connect to the database
    express-session:        Allows sessions which are basically how users log in to their account and stay logged in during their session
    connect-mongo:          Used for storing sessions in our database
    axios:                  Used to make requests to routes from inside socket.io, so that we can save our conversation in
                            our database
    body-parser:            Used to parse information from forms mainly, probably won't use but just in case
    socket.io:              Create a socket connection with server and client, how we send messages without reloading

    Other:

    PORT:           The default port number that the server will run on if there is no environmental
                    variable configured (which would happen when deployed on heroku)
*/

let express = require("express"),
    http    = require("http"),
    path    = require("path");
let mongoose = require("mongoose");
let session = require("express-session");
let mongoStore = require("connect-mongo");
let bodyParser = require("body-parser");
const PORT = 8000;
const app = express();
const server = http.createServer(app);
const cors = require('cors');

// initializing socket.io
const io = require("socket.io")(server);


// Example database object that we save message from client into database
const SimpleObject = require('./models/simple');


// Access to environmental variables
require('dotenv').config();


// For using c.o.r.s (Cross Origin Resource Sharing)
// So we can make request across different urls,
// which will happen when deploying live version
app.use(cors());


// Setting up conventional stuff for server
//probably won't need since likely won't be making conventional api calls to server,
// mainly realtime socket stuff
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
let routes = require('./routes/routes');
app.use('/api/', routes);


/////////////// DB initialization
let URI; // will be updated once deployed
// Connect to database
mongoose.connect(process.env.DBLOCALURI || URI,
    {
        useNewUrlParser: true,
        useUnifiedTopology: true
    })

let db = mongoose.connection;
db.on('error', console.error.bind(console, 'Error connecting to mongodb'));

db.on('connected', function() {
    console.log("Database has connected!")
});

let sessionData = session({
    secret: 'Server initialized',
    resave: true,
    saveUninitialized: true,
    store: mongoStore.create({
        mongoUrl: process.env.DBLOCALURI
    })
})
app.use(sessionData);





const MAXSPEED = 4;
function getRandomInt(max) {
    //random num from 1 to max, inclusive
    return (Math.floor(Math.random() * max)) + 1;
}


const enemy_info = {
    'jc': {
        'is_good': true,
        'id': 0,
        'max_time_alive': 200,
        'speed': getRandomInt(MAXSPEED)
    },
    'cow': {
        'is_good': true,
        'id': 1,
        'max_time_alive': 200,
        'speed': getRandomInt(MAXSPEED)
    },
    'ricky': {
        'is_good': false,
        'id': 2,
        'max_time_alive': 300,
        'speed': getRandomInt(MAXSPEED)
    },
    'david': {
        'is_good': false,
        'id': 3,
        'max_time_alive': 300,
        'speed': getRandomInt(MAXSPEED)
    },
    'anton': {
        'is_good': false,
        'max_time_alive': 300,
        'speed': getRandomInt(MAXSPEED),
        'id': 4
    },
    'armando': {
        'is_good': true,
        'max_time_alive': 300,
        'speed': getRandomInt(MAXSPEED),
        'id': 5
    },
    'david2': {
        'is_good': true,
        'max_time_alive': 300,
        'speed': 20,
        'id': 6

    },
}




// main socket.io stuff
io.on('connection', socket => {

    // When client joins, emit message
    socket.emit("WelcomeClient", {
        message: "Welcome to sky danger ranger! we're glad to have you here. It's gonna be a ride!"
    });

    socket.on('fetchEnemies', request => {
        socket.emit("enemyInfoToClient", enemy_info);
        console.log("enemies fetched")
    })

    // Client sends message
    socket.on('clientMessageToServer', request => {
        console.log(`Message from Client with id ${socket.id}: ${request.message}`);
    });

    // Client sends message to be stored in DB
    socket.on("clientMessageToDatabase", request => {
        if (!request.username || !request.message) {
            console.log("User didn't specify both username and message! Rip to the B.I.G.");
            return;
        }

        let newDBObject = {
            username: request.username,
            message: request.message
        };

        SimpleObject.create(newDBObject).then(createdDBObject => {
            console.log("New object created! Here it is: ", createdDBObject);
        });
    });

    // Client disconnects
    socket.on('disconnect', () => {
        console.log(`Client with the following id has connected: ${socket.id}`);
    });
});



/*
 * Create Server
 */
server.listen((process.env.PORT || PORT), () => {
    console.log("Sky Danger Ranger is running in port " + PORT);
});