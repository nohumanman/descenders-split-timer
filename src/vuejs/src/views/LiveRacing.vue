<template>
    <v-container>
      <h1>Live Racing</h1>
      <v-row cols="12" md="2">
        <v-col v-for="user in users" :key="user.steam_id">
          <v-card>
            <v-card-title>{{user.steam_name}}</v-card-title>
            <v-card-subtitle>{{user.steam_id}}</v-card-subtitle>
            <v-card-text>
              <div v-for="key, index in user">
                {{index}}: {{key}}
              </div>
            </v-card-text>
            <v-text-field v-model="user.eval" prepepend-icon="mdi-account">

            </v-text-field>
            <v-btn @click='sendEval(user)'>Send</v-btn>
            <v-btn @click="spectatePlayer(user)">SPECTATE</v-btn>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </template>

  <script>
    export default {
    name: 'App',
    data() {
      return {
        users: []
      }
    },
    mounted() {
      // awesome! now we need to tell the websocket that we're authenticated
      this.$socket.emit('authenticate', JSON.stringify({
        'token': localStorage.getItem("discord_token")
      }));
      this.$socket.on('users_update', (data) => {
        // data is like [{steam_id: 123, steam_name: 'name', eval: 'eval'}, ...]
        data.forEach(user => {
          // if use exists, update it, otherwise add it
          user = [];
          let index = this.users.findIndex(u => u.steam_id === user.steam_id);
          if (index !== -1) {
            // UPDATE (do not remove existing keys)
            for (const [key, value] of Object.entries(user)) {
              this.users[index][key] = value;
            }
          } else {
            // ADD
            this.users.push(user);            
          }
        });
      })
      this.$socket.on('message', (data) => {
        console.log('Message from server:', data);

            var data_json = JSON.parse(data);
            if (data_json['type'] == 'send'){
                if (data_json['identifier'] == 'steam_id'){
                  console.log("Setting steam_id to", data_json['data']);
                    localStorage.setItem("steam_id", data_json['data']);
                }
            }

      });
      this.$socket.emit('message', 'get_users');
      setInterval(() => {
        this.$socket.emit('message', 'get_users');
      }, 800);
    }
    ,
    methods: {
      sendEval(user) {
        this.$socket.emit('message', {'type': 'eval', 'data': user});
      },
      spectatePlayer(user){
        // we need to find ourselves
        var us = this.users.find(u => u.steam_id === localStorage.getItem('steam_id'));
        // then tell ourself to spectate the player
        us.eval = `SPECTATE|${user.steam_id}`;
        this.sendEval(us);
        // the server needs to know
      }
    }
  }
  </script>