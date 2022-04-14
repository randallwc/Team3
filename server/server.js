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
    http = require("http"),
    path = require("path");
let mongoose = require("mongoose");
let session = require("express-session");
let sharedSIOSession = require("express-socket.io-session");
let mongoStore = require("connect-mongo");
let bodyParser = require("body-parser");
const PORT = 8000;
const app = express();
const server = http.createServer(app);
const cors = require("cors");

// initializing socket.io
const io = require("socket.io")(server, {
    pingTimeout: 300000,
    maxHttpBufferSize: 1e7,
    pingInterval: 70000,
    transports: ['websocket']
});

// Example database object that we save message from client into database
const SimpleObject = require("./models/simple");

// Access to environmental variables
require("dotenv").config();

// For using c.o.r.s (Cross Origin Resource Sharing)
// So we can make request across different urls,
// which will happen when deploying live version
app.use(cors());

// Setting up conventional stuff for server
//probably won't need since likely won't be making conventional api calls to server,
// mainly realtime socket stuff
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
let routes = require("./routes/routes");
app.use("/api/", routes);

/////////////// DB initialization
let URI = `mongodb+srv://${process.env.DBUSERNAME}:${process.env.DBPASSWORD}@skydangerrangerdb.ozahe.mongodb.net/${process.env.DBNAME}?retryWrites=true&w=majority`;
// Connect to database
mongoose.connect(process.env.DBLOCALURI || URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
});

let db = mongoose.connection;
db.on("error", console.error.bind(console, "Error connecting to mongodb"));

db.on("connected", function () {
    console.log("Database has connected!");
});

let sessionData = session({
    secret: "Server initialized",
    resave: true,
    saveUninitialized: true,
    store: mongoStore.create({
        mongoUrl: process.env.DBLOCALURI || URI,
    }),
});
app.use(sessionData);

io.use(
    sharedSIOSession(sessionData, {
        autoSave: true,
    })
);

const MAXSPEED = 4;
function getRandomInt(max) {
    //random num from 1 to max, inclusive
    return Math.floor(Math.random() * max) + 1;
}

const enemy_info = {
    jc: {
        is_good: true,
        id: 0,
        max_time_alive: 200,
        speed: getRandomInt(MAXSPEED),
    },
    cow: {
        is_good: true,
        id: 1,
        max_time_alive: 200,
        speed: getRandomInt(MAXSPEED),
    },
    ricky: {
        is_good: false,
        id: 2,
        max_time_alive: 300,
        speed: getRandomInt(MAXSPEED),
    },
    david: {
        is_good: false,
        id: 3,
        max_time_alive: 300,
        speed: getRandomInt(MAXSPEED),
    },
    anton: {
        is_good: false,
        max_time_alive: 300,
        speed: getRandomInt(MAXSPEED),
        id: 4,
    },
    armando: {
        is_good: true,
        max_time_alive: 300,
        speed: getRandomInt(MAXSPEED),
        id: 5,
    },
    david2: {
        is_good: true,
        max_time_alive: 300,
        speed: 20,
        id: 6,
    },
};

// main socket.io stuff
io.on("connection", (socket) => {

    //// Fetching types of enemies
    // listenForEnemyTypesFetched(socket);

    //// Joining rooms
    listenForJoiningNewRoom(socket, roomTracker);
    listenForJoiningExistingRoom(socket, roomTracker);

    //// Fetch all entities
    listenForFetchingAllEnemies(socket); // remove replace with setinterval

    //// Handle Enemies
    listenForAppendingEnemyByHost(socket);
    listenForEnemyRemoved(socket);
    // listenForUpdatingEnemyCoordsByHost(socket);

    //// Client disconnects
    listenForDisconnection(socket, roomTracker);

    //// Handle Rangers
    // Ranger updates coordinates
    listenForUpdatingCoordinatesAndMetadata(socket);
    //// Send opponent rangers to everyone in room
    listenForFetchingOpponentRangers(socket, roomTracker);// remove replace with setinterval
});

//////////////////////////////////////////////////////////
// Setup Calls
//////////////////////////////////////////////////////////
const emitWelcome = (socket) => {
    io.to(socket.id).emit("welcome_client", {
        message:
            "Welcome to sky danger ranger! we're glad to have you here. It's gonna be a ride!",
        socket_id: socket.id,
    });
};

const listenForEnemyTypesFetched = (socket) => {
    socket.on("fetch_enemies", (request) => {
        socket.emit("enemy_info_to_client", enemy_info);
    });
};

//////////////////////////////////////////////////////////
// Handling Enemies
//////////////////////////////////////////////////////////
const roomToEnemyList = {};
const listenForAppendingEnemyByHost = (socket) => {
    socket.on("host_appending_new_enemy", (request) => {
        // ensure person sending is the host
        if (
            !!roomTracker[socket.handshake.session.roomID] && roomTracker[socket.handshake.session.roomID]["host"] === socket.handshake.session.timeUserID
        ) {
            let id = request.id;
            if (!roomToEnemyList[socket.handshake.session.roomID]) {
                // Initialize as empty
                roomToEnemyList[socket.handshake.session.roomID] = {};
            }
            roomToEnemyList[socket.handshake.session.roomID][id] = request;
        }
    });
};

const listenForEnemyRemoved = (socket) => {
    socket.on("remove_enemy", (request) => {
        const id = request.id;
        let enemyList = roomToEnemyList[socket.handshake.session.roomID];
        delete enemyList[id];
    });
};

const listenForUpdatingEnemyCoordsByHost = (socket) => {
    // Assuming enemies don't change levels
    // Expects request in the form of
    // req = {
    //     'id':id,
    //     'x':x,
    //     'y':y,
    // }

    socket.on("host_updating_enemy_coordinates", (request) => {
        if (
            roomTracker[socket.handshake.session.roomID]["host"] === socket.handshake.session.timeUserID
        ) {
            let enemyList = roomToEnemyList[socket.handshake.session.roomID];
            if (!!enemyList[request.id]) {
                // If enemy still exists in server
                // Not sure what would potentially happen in high speed socket transmissions
                enemyList[request.id]["x"] = request.x;
                enemyList[request.id]["y"] = request.y;
                // console.log(`Updating id: ${request.id} with coords: (${request.x}, ${request.y})`)
            }
        }
    });
};

//////////////////////////////////////////////////////////
// Handling Room Joining
//////////////////////////////////////////////////////////
// Keep track of what room all rangers are connected to
let roomTracker = {};

const listenForJoiningExistingRoom = (socket, roomTracker) => {
    socket.on("join_existing_room", (request) => {
        console.log("ID joining:", socket.id);
        console.log("Before Joining existing room", roomTracker);
        if (!!roomTracker[request.room_id]) {
            socket.join(request.room_id);
            roomTracker[request.room_id].list.push(request.time_user_id);
            socket.broadcast
                .to(request.room_id)
                .emit("new_player_joined_room", {
                    room_id: request.room_id,
                    socket_id: socket.id,
                });

            console.log("After Joining existing room", roomTracker);

            // Room ID
            socket.handshake.session.roomID = request.room_id;
            // User ID unique to each client
            socket.handshake.session.userID = request.user_id;
            // Unique UUID to append to user ID
            socket.handshake.session.epochTime = request.epoch_time;
            //Concatinated userID and UUID
            socket.handshake.session.timeUserID = request.time_user_id;
            // Username picked by player
            socket.handshake.session.username = request.username;

            socket.handshake.session.save();

            emitWelcome(socket);
        }
    });
};

const listenForJoiningNewRoom = (socket, roomTracker) => {
    socket.on("join_new_room", (request) => {
        console.log("ID joining:", socket.id);
        console.log("Before new room", roomTracker);

        if (!roomTracker[request.room_id]) {
            socket.join(request.room_id);
            roomTracker[request.room_id] = {
                list: [request.time_user_id],
                host: request.time_user_id,
            };

            console.log("After new room", roomTracker);

            // Room ID
            socket.handshake.session.roomID = request.room_id;
            // User ID unique to each client
            socket.handshake.session.userID = request.user_id;
            // Unique UUID to append to user ID
            socket.handshake.session.epochTime = request.epoch_time;
            //Concatinated userID and UUID
            socket.handshake.session.timeUserID = request.time_user_id;
            // Username picked by player
            socket.handshake.session.username = request.username;

            socket.handshake.session.save();

            emitWelcome(socket);
        }
    });
};

//////////////////////////////////////////////////////////
// Handle Rangers
//////////////////////////////////////////////////////////
// Coordinates of all rangers connected to server
let rangerCoordinatesTracker = {};

const listenForFetchingOpponentRangers = (socket, roomTracker) => {
    socket.on("fetch_opponent_rangers", (request) => {
        const roomID = socket.handshake.session?.roomID;
        if (!!roomID) {
            // to individual socketID, only the person who requested
            io.to(socket.id).emit(
                "server_sending_opponent_rangers_in_game",
                roomTracker[roomID]
            );
        }
    });
};

const listenForUpdatingCoordinatesAndMetadata = (socket) => {
    // Should also take into account health
    socket.on("update_my_coordinates_and_meta", (request) => {
        // console.log(`ID: ${socket.id} ${request?.x} ${request?.y}, ${request?.is_firing}`);
        rangerCoordinatesTracker[socket.handshake.session.timeUserID] = {
            x: request?.x,
            y: request?.y,
            z: request?.z,
            is_firing: request?.is_firing
        };

        // all except sender
        socket.to(socket.handshake.session.roomID)
            .emit("update_opponent_ranger_coordinates", {
                x: request?.x,
                y: request?.y,
                z: request?.z,
                socket_id: socket.id,
                is_firing: request?.is_firing,
                time_user_id: socket.handshake.session.timeUserID
            });
    });
};

//////////////////////////////////////////////////////////
// Misc
//////////////////////////////////////////////////////////
const listenForClientMessageToDB = (socket) => {
    socket.on("clientMessageToDatabase", (request) => {
        if (!request.username || !request.message) {
            console.log(
                "User didn't specify both username and message! Rip to the B.I.G."
            );
            return;
        }

        let newDBObject = {
            username: request.username,
            message: request.message,
        };

        SimpleObject.create(newDBObject).then((createdDBObject) => {
            console.log("New object created! Here it is: ", createdDBObject);
        });
    });
};

const listenForDisconnection = (socket, roomTracker) => {
    socket.on("disconnect", (reason) => {
        console.log(`Client with the following id has disconnected: ${socket.id}, userID: ${socket.handshake.session.timeUserID}`);
        console.log(`Was in room:`, socket.handshake.session?.roomID);
        console.log(`Reason:`, reason);

        let roomLength =
            roomTracker[socket.handshake.session.roomID]?.list.length;
        let list = roomTracker[socket.handshake.session.roomID]?.list;

        for (let i = 0; i < roomLength; i++) {
            // remove person from list of players in room
            if (list[i] === socket.handshake.session.timeUserID) {
                list.splice(i, 1);
            }
        }
    });
};

const listenForFetchingAllEnemies = (socket) => {
    socket.on("fetch_all_enemies", (request) => {
        if (!!socket.handshake.session.roomID) {
            // Get Enemies
            let enemies = roomToEnemyList[socket.handshake.session.roomID];
            if (!enemies) {
                io.to(socket.id).emit("all_entities_to_client", {
                    enemies: {},
                });
            } else {
                io.to(socket.id).emit("all_entities_to_client", {
                    enemies: enemies,
                });
            }

        }
    });
};

/*
 * Create Server
 */
server.listen(process.env.PORT || PORT, () => {
    console.log("Sky Danger Ranger is running in port " + PORT);
});
