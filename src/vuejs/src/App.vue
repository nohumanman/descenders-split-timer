<template>
  <v-app>
    
    <!-- Footer -->
    <AppFooter v-if="$route.path != '/live-racing/spectated-player'" />
    <!-- App Bar -->
    <TopNavigation v-if="$route.path != '/live-racing/spectated-player'" />

    <!-- Main Content -->
    <v-main>
      <!-- Render your router view -->
      <router-view />
    </v-main>

    

  </v-app>
</template>

<script setup>
  const apiUrl = import.meta.env.VITE_APP_API_URL;
</script>

<script>
  export default {
    name: 'App',
    mounted() {
      console.log('App created');
      console.log(this.$socket)
      this.$socket.emit('message', 'lmao')
    }
  }
</script>
