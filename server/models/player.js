// Will be used to store our scores
const mongoose = require("mongoose");
const Highscore = require('../models/highscore');
let PlayerSchema = new mongoose.Schema({
    username: {
        type: String,
        required: true,
    },
    multiplayerSingleGameHighscore: {
        type: Number,
        default: 0
    },
    multiplayerLifetimeScore: {
        type: Number,
        default: 0
    },
    singleplayerSingleGameHighscore: {
        type: Number,
        default: 0
    },
    singleplayerLifetimeScore: {
        type: Number,
        default: 0
    },

});

PlayerSchema.statics.addScore = function(username, score, mode){
    return new Promise((resolve, reject) => {

        let fieldToModifyLifetime;
        let fieldToModifySingleGame;

        if (mode === 'multiplayer'){
            fieldToModifyLifetime = 'multiplayerLifetimeScore';
            fieldToModifySingleGame = 'multiplayerSingleGameHighscore';
        }else if (mode === 'singleplayer'){
            fieldToModifyLifetime = 'singleplayerLifetimeScore';
            fieldToModifySingleGame = 'singleplayerSingleGameHighscore';
        }else{
            return Promise.reject(new Error('Available modes to pass in: "singleplayer" & "multiplayer"'));
        }


        Player.findOne({username: username}).then(player => {
            if (!player){
                //player not found with that username, create a new one
                const newPlayerDetails = {
                    username: username,
                }
                // set scores
                newPlayerDetails[fieldToModifyLifetime] = score
                newPlayerDetails[fieldToModifySingleGame] = score

                return Player.create(newPlayerDetails);
            }else{
                //player found, update their scores
                if (!player[fieldToModifySingleGame] || player[fieldToModifySingleGame] < score){
                    player[fieldToModifySingleGame] = score;
                }
                player[fieldToModifyLifetime] += score;
                return player.save();
            }
        }).then(player => {
            resolve(player);
        }).catch(err => {
            reject(err);
        });
    });
}


PlayerSchema.pre('save', async function(next){
    // game was multiplayer
    const lifetimeMultiplayerModified = this.isModified('multiplayerLifetimeScore');
    const singleGameMultiplayerModified = this.isModified('multiplayerSingleGameHighscore');

    // game was single player
    const lifetimeSinglePlayerModified = this.isModified('singleplayerLifetimeScore');
    const singleGameSinglePlayerModified = this.isModified('singleplayerSingleGameHighscore');

    if (lifetimeMultiplayerModified || singleGameMultiplayerModified){
        if (lifetimeMultiplayerModified){
            await Highscore.handleScoreForLifetimeScore(this._id, this.username, this.multiplayerLifetimeScore, mode);
        }
        if (singleGameMultiplayerModified){
            await Highscore.handleSingleGameScore(this._id, this.username, this.multiplayerSingleGameHighscore, mode);
        }
        next();
    }else if (lifetimeSinglePlayerModified || singleGameSinglePlayerModified){

        if (lifetimeSinglePlayerModified){
            await Highscore.handleScoreForLifetimeScore(this._id, this.username, this.singleplayerLifetimeScore, mode);
        }
        if (singleGameSinglePlayerModified){
            await Highscore.handleSingleGameScore(this._id, this.username, this.singleplayerSingleGameHighscore, mode);
        }
    }else{
        next();
    }
});


let Player = mongoose.model("Player", PlayerSchema);
module.exports = Player;