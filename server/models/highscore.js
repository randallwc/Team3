// Will be used to store our scores
const mongoose = require("mongoose");
const masterKey = 'MasterKey';

let HighscoreSchema = new mongoose.Schema({
    singleGameHighscores: [{
        playerID: mongoose.ObjectId,
        username: String,
        score: Number
    }],
    lifetimeGameHighscores: [{
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


HighscoreSchema.statics.handleSingleGameScore = function(playerID, username, score){
    return new Promise((resolve, reject) => {

        Highscore.findOne({key: masterKey}).then(highscores => {
            let {singleGameHighscores} = highscores;

            // find if score is already in array
            //1 if it is, chheck score to see if given score is higher, if so, and sort
            let scorerFound = false;
            for(const scoreObject of singleGameHighscores){
                const thisIsTheUser = scoreObject.username === username && scoreObject.playerID.toString() === playerID;
                const userScoredHigherThisTime = scoreObject.score < score;
                if (thisIsTheUser && userScoredHigherThisTime){
                    scoreObject.score = score;
                    scorerFound = true;
                }
            }

            //2 if it isn't, append to array and sort
            if (!scorerFound){
                singleGameHighscores.push({
                    playerID: playerID,
                    username: username,
                    score: score
                });
            }

            singleGameHighscores.sort(sortByScore);
            return highscores.save();
        }).then(highscores => {
            resolve(highscores);
        }).catch(err => {
            reject(err);
        })
    });
}

HighscoreSchema.statics.handleScoreForLifetimeScore = function(playerID, username, score){
    Highscore.findOne({key: masterKey}).then(highscores => {
        const {lifetimeGameHighscores} = highscores;

        // find if score is already in array
        //1 if it is, add to the score and sort
        let scorerFound = false;
        for(const scoreObject of lifetimeGameHighscores){
            const thisIsTheUser = scoreObject.username === username && scoreObject.playerID.toString() === playerID;
            if (thisIsTheUser){
                scoreObject.score += score;
                scorerFound = true;
            }
        }

        //2 if it isn't, append to array and sort
        if (!scorerFound){
            lifetimeGameHighscores.push({
                playerID: playerID,
                username: username,
                score: score
            });
        }

        lifetimeGameHighscores.sort(sortByScore);
        return highscores.save();
    }).then(highscores => {
        return resolve(highscores);
    }).catch(err => {
        return reject(err);
    })
}

HighscoreSchema.statics.fetchNHighestSingleGameScores = function(nScores){
    return new Promise((resolve, reject) => {
        if (!nScores || nScores < 1){
            reject(new Error('Please enter a valid [n] scores'));
        }
        const dummyScores = [11,10,9,8,7,6,5,4,3,2];
        return resolve(dummyScores)
    });
}

HighscoreSchema.statics.fetchNHighestLifetimeScores = function(nScores){
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
