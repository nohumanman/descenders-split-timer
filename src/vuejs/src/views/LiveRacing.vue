<template>
    <v-container>
      <h1>Live Racing</h1>
      <v-row>
        <v-col cols="12" md="2">
          <v-card v-for="user in users" :key="user.steam_id">
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
      this.$socket.emit('message', 'get_users');
      setInterval(() => {
        this.$socket.emit('message', 'get_users');
      }, 800);
    }
  ,
  methods: {
    sendEval(user) {
      this.$socket.emit('message', {'type': 'eval', 'data': user});
    }
    }
  }
  </script>