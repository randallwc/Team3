const mongoose = require("mongoose");

let SimpleSchema = new mongoose.Schema({
  username: {
    type: String,
    required: true,
  },
  message: {
    type: String,
    required: true,
  },
});

let SimpleObject = mongoose.model("SimpleObject", SimpleSchema);
module.exports = SimpleObject;
