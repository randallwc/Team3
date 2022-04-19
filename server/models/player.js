// Will be used to store our scores
const mongoose = require("mongoose");
const Highscore = require('../models/highscore');
let PlayerSchema = new mongoose.Schema({
    username: {
        type: String,
        required: true,
    },
    lifetimeScore: {
        type: Number,
        default: 0
    },
    singleGameHighscore: {
        score: Number,
        default: 0
    }
});




PlayerSchema.statics.addScore = function(username, score){
    return new Promise((resolve, reject) => {
        Player.findOne({username: username}).then(player => {
            if (!player){
                //player not found with that username, create a new one
                const newPlayerDetails = {
                    username: username,
                    lifetimeScore: score,
                    singleGameHighscore: score
                }

                return Player.create(newPlayerDetails);
            }else{
                //player found, update their scores
                if (player.singleGameHighscore < score){
                    player.singleGameHighscore = score;
                }
                player.lifetimeScore += score;

                return player.save();
            }
        }).then(player => {
            resolve(player);
        }).catch(err => {
            reject(err);
        });
    });
}


PlayerSchema.pre('save', function(next){

});




let Player = mongoose.model("Player", PlayerSchema);
module.exports = Player;
