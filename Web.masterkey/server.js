const express = require("express");
const app = express();
const cors = require("cors");
const PORT = process.env.PORT || 3001;
const path = require("path");

app.use(express.json());
app.use(cors());

app.use(express.static(path.join(__dirname, "public")));

app.get("/masterkey", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "masterkey.html"));
});

// Khởi động server
app.listen(PORT, () => {
  console.log(`Server conected ${PORT}`);
});
