const express = require("express");
const router = express.Router();
const Highscore = require('../models/highscore');


// Going to localhost:8000/api/sky will return this
router.get("/sky", (request, response, next) => {
    return response.status(200).send({
        message: "Sky Danger Ranger is about to be the BEEZ knees",
    });
});

router.get('/fetch/lifetime/highscores', (request, response, next) => {

    try {
        // to be sent by client
        let {nScores} = request.body;

        // this if statement will be removed in the future
        // for testing purposes
        if (!nScores){
            nScores = '10';
        }

        // trycatch will catch error if nscores isn't an integer
        nScores = parseInt(nScores);

        if (nScores > 50 || nScores < 1){
            return next(new Error("Please enter a number 1-50, inclusive"));
        }

        Highscore.fetchNHighestLifetimeScores(nScores).then(scores => {
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
        let {nScores} = request.body;

        // this if statement will be removed in the future
        // for testing purposes
        if (!nScores){
            nScores = '10';
        }

        // trycatch will catch error if nscores isn't an integer
        nScores = parseInt(nScores);

        if (nScores > 50 || nScores < 1){
            return next(new Error("Please enter a number 1-50, inclusive"));
        }

        Highscore.fetchNHighestSingleGameScores(nScores).then(scores => {
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

module.exports = router;
