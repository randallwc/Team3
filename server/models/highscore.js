// Will be used to store our scores
const mongoose = require("mongoose");
const masterKey = 'MasterKey';

let HighscoreSchema = new mongoose.Schema({
    // single player
    singleplayerSingleGameHighscores: [{
        playerID: mongoose.ObjectId,
        username: String,
        score: Number
    }],
    singleplayerLifetimeGameHighscores: [{
        playerID: mongoose.ObjectId,
        username: String,
        score: Number
    }],
    // multiplayer
    multiplayerSingleGameHighscores: [{
        playerID: mongoose.ObjectId,
        username: String,
        score: Number
    }],
    multiplayerLifetimeGameHighscores: [{
        playerID: mongoose.ObjectId,
        username: String,
        score: Number
    }],
    key: {
        // master key will be 'MasterKey'
        type: String,
        unique: true
    }
});

const sortByScore = (first, second) => {
    if (first.score > second.score) {
        return -1;
    }else if (first.score < second.score) {
        return 1;
    }
    return 0;
};


HighscoreSchema.statics.handleSingleGameScore = function(playerID, username, score, mode){

    let fieldToModifySingleGame;

    if (mode === 'multiplayer'){
        fieldToModifySingleGame = 'multiplayerSingleGameHighscores';
    }else if (mode === 'singleplayer'){
        fieldToModifySingleGame = 'singleplayerSingleGameHighscores';
    }else{
        return Promise.reject(new Error('Available modes to pass in: "singleplayer" & "multiplayer"'));
    }


    return new Promise((resolve, reject) => {

        Highscore.findOne({key: masterKey}).then(highscores => {
            let scores = highscores[fieldToModifySingleGame];

            // find if score is already in array
            //1 if it is, chheck score to see if given score is higher, if so, and sort
            let scorerFound = false;
            for(const scoreObject of scores){
                const thisIsTheUser = scoreObject.username === username && scoreObject.playerID.toString() === playerID.toString();
                const userScoredHigherThisTime = scoreObject.score < score;
                if (thisIsTheUser && userScoredHigherThisTime){
                    scoreObject.score = score;
                    scorerFound = true;
                }
            }

            //2 if it isn't, append to array and sort
            if (!scorerFound){
                scores.push({
                    playerID: playerID,
                    username: username,
                    score: score
                });
            }

            scores.sort(sortByScore);
            return highscores.save();
        }).then(highscores => {
            return resolve(highscores);
        }).catch(err => {
            return reject(err);
        })
    });
}

HighscoreSchema.statics.handleScoreForLifetimeScore = function(playerID, username, score, mode){

    let fieldToModifyLifetime;

    if (mode === 'multiplayer'){
        fieldToModifyLifetime = 'multiplayerLifetimeGameHighscores';
    }else if (mode === 'singleplayer'){
        fieldToModifyLifetime = 'singleplayerLifetimeGameHighscores';
    }else{
        return Promise.reject(new Error('Available modes to pass in: "singleplayer" & "multiplayer"'));
    }

    return new Promise((resolve, reject) => {
        Highscore.findOne({key: masterKey}).then(highscores => {
            const scores = highscores[fieldToModifyLifetime];

            // find if score is already in array
            //1 if it is, add to the score
            let scorerFound = false;
            for(const scoreObject of scores){
                console.log(scoreObject, username, playerID, score, 'magic trick', playerID, 'batic', scoreObject.playerID.toString())
                const thisIsTheUser = scoreObject.username === username && scoreObject.playerID.toString() === playerID.toString();
                console.log('HEREHREKLR;ALEKJFSAL;DKFJASD ', scoreObject.username === username, scoreObject.playerID.toString() === playerID)
                if (thisIsTheUser){
                    scoreObject.score = score;
                    scorerFound = true;

                }
            }

            //2 if it isn't, append to array
            if (!scorerFound){
                scores.push({
                    playerID: playerID,
                    username: username,
                    score: score
                });
            }

            scores.sort(sortByScore);
            return highscores.save();
        }).then(highscores => {
            return resolve(highscores);
        }).catch(err => {
            return reject(err);
        })
    });

}

HighscoreSchema.statics.fetchNHighestSingleGameScores = function(nScores, mode){

    let fieldToModifySingleGame;

    if (mode === 'multiplayer'){
        fieldToModifySingleGame = 'multiplayerSingleGameHighscores';
    }else if (mode === 'singleplayer'){
        fieldToModifySingleGame = 'singleplayerSingleGameHighscores';
    }else{
        return Promise.reject(new Error('Available modes to pass in: "singleplayer" & "multiplayer"'));
    }

    return new Promise((resolve, reject) => {
        if (!nScores || nScores < 1){
            reject(new Error('Please enter a valid [n] scores'));
        }
        const dummyScores = [11,10,9,8,7,6,5,4,3,2];
        return resolve(dummyScores)
    });
}

HighscoreSchema.statics.fetchNHighestLifetimeScores = function(nScores, mode){

    let fieldToModifyLifetime;

    if (mode === 'multiplayer'){
        fieldToModifyLifetime = 'multiplayerLifetimeGameHighscores';
    }else if (mode === 'singleplayer'){
        fieldToModifyLifetime = 'singleplayerLifetimeGameHighscores';
    }else{
        return Promise.reject(new Error('Available modes to pass in: "singleplayer" & "multiplayer"'));
    }

    return new Promise((resolve, reject) => {
        if (!nScores || nScores < 1){
            reject(new Error('Please enter a valid [n] scores'));
        }
        const dummyScores = [10,9,8,7,6,5,4,3,2,1];
        return resolve(dummyScores)
    });
}

let Highscore = mongoose.model("Highscore", HighscoreSchema);
module.exports = Highscore;
