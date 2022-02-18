const express = require('express');
const router = express.Router();


// Going to localhost:8000/api/sky will return this
router.get('/sky', (request, response, next) => {
    return response.status(200).send({
        message: "Sky Danger Ranger is about to be the BEEZ knees"
    });
});

module.exports = router;