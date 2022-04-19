// Will be used to store our scores
const mongoose = require("mongoose");

let HighscoreSchema = new mongoose.Schema({
    singleGameHighscores1: [{
        score: Number,
    }],
    lifetimeGameHighscores1: [{
        score: Number,
        username: String
    }],
    singleGameHighscores: [{
        playerID: Number,
    }],
    lifetimeGameHighscores: [{
        score: Number,
        username: String
    }],
});

HighscoreSchema.statics.handleSingleGameScore = function(){}

HighscoreSchema.statics.handleScoreForLifetimeScore = function(){}

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
