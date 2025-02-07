<template>
    <v-container>
      <h1>Live Racing</h1>
      {{users}}
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
      this.$socket.on('users_update', (data) => {
        // data is like {'total_users_online': 3}
        console.log('updating users');
        this.users = data;
      })
      this.$socket.emit('message', 'get_users');
      setInterval(() => {
        this.$socket.emit('message', 'get_users');
      }, 800);
    }
  }
  </script>