const express = require("express");
const router = express.Router();
const Highscore = require('../models/highscore');
const Player = require('../models/player');

// Going to localhost:8000/api/sky will return this
router.get("/sky", (request, response, next) => {
    return response.status(200).send({
        message: "Sky Danger Ranger is about to be the BEEZ knees",
    });
});

router.get('/fetch/lifetime/highscores', (request, response, next) => {

    try {
        // to be sent by client
        let {nScores} = request.query;
        const {mode} = request.query;

        // will default to this if not passed in
        if (!nScores){
            nScores = '5';
        }

        // trycatch will catch error if nscores isn't an integer
        nScores = parseInt(nScores);

        if (nScores > 50 || nScores < 1){
            return next(new Error("Please enter a number 1-50, inclusive"));
        }

        Highscore.fetchNHighestLifetimeScores(nScores, mode).then(scores => {
            return response.status(200).send({
                scores: scores
            });
        }).catch(err => {
            return next(err);
        });
    }catch (err) {
        return next(err);
    }
});

router.get('/fetch/singlegame/highscores', (request, response, next) => {

    try {
        // to be sent by client
        let {nScores} = request.query;
        const {mode} = request.query;

        // if not passed in, will default to this
        if (!nScores){
            nScores = '5';
        }

        // trycatch will catch error if nscores isn't an integer
        nScores = parseInt(nScores);

        if (nScores > 50 || nScores < 1){
            return next(new Error("Please enter a number 1-50, inclusive"));
        }

        Highscore.fetchNHighestSingleGameScores(nScores, mode).then(scores => {
            return response.status(200).send({
                scores: scores
            });
        }).catch(err => {
            return next(err);
        });
    }catch (err) {
        return next(err);
    }
});



// TODO: delete this once everything works, python client will send highscores
// router.get('/set/scores', (request, response, next) => {
//
//     try {
//
//         Player.addScore('anton', 12, 'multiplayer').then(player => {
//             return response.status(200).send({
//                 player: player
//             });
//         }).catch(err => {
//             return next(err);
//         });
//     }catch (err) {
//         return next(err);
//     }
// });





router.post('/insertscore', (request, response, next) => {

    const {username} = request.body;
    const {score} = request.body;
    const {mode} = request.body;

    if (!username){
        return next(new Error('Please pass in username'));
    }

    if (mode !== 'multiplayer' && mode !== 'singleplayer'){
        return next(new Error('Available modes to pass in: "singleplayer" & "multiplayer"'));
    }

    try {

        const intScore = parseInt(score);

        if (intScore < 0){
            return next(new Error('Score must be at least 0'));
        }

        Player.addScore(username, intScore, mode).then(player => {

            return response.status(200).send({
                player: player
            });
        }).catch(err => {
            return next(err);
        });
    }catch (err) {
        return next(err);
    }


});



module.exports = router;
