import io from 'socket.io-client';

const socket = io('http://localhost:40000');

socket.on('connect', () => {
    console.log('Connected to server');
    socket.send('GET_PLAYERS');
});

socket.on('disconnect', () => {
    console.log('Disconnected from server');
    // reconnect
    socket.connect();
});



export default socket;
