import express from "express";
import SocketIO from "socket.io";
import https from "https";
import fs from "fs";
import { SocketAddress } from "net";


const options={
    key: fs.readFileSync("./private.key"),
    cert: fs.readFileSync("./certificate.crt")
}

const app = express();

app.set("view engine", "pug");
app.set("views", __dirname+"/src/views");
app.use("/public", express.static(__dirname+"/src/public"));
app.get("/",(req,res)=>res.render("home"));
app.get("/*",(req,res)=>res.redirect("/"));

const handleListen=()=>console.log("Listening on port 6006");


const server=https.createServer(options,app);
const io = SocketIO(server);

io.on("connection", (socket) => {
    socket.on("join_room", (roomName) => {
      socket.join(roomName);
      socket.to(roomName).emit("welcome");
    });
    socket.on("offer", (offer, roomName) => {
      socket.to(roomName).emit("offer", offer);
    });
    socket.on("answer", (answer, roomName) => {
      socket.to(roomName).emit("answer", answer);
    });
    socket.on("ice", (ice, roomName) => {
      socket.to(roomName).emit("ice", ice);
    });
});


server.listen(6006,handleListen);