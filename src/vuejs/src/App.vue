<template>
  <v-app>
    
    <TopNavigation />
    <!-- App Bar -->
   

    <!-- Main Content -->
    <v-main>
      <!-- Render your router view -->
      <router-view />
    </v-main>

    <!-- Footer -->
    <AppFooter />
  </v-app>
</template>

<script setup>
  const apiUrl = import.meta.env.VITE_APP_API_URL;
  console.log(apiUrl);
</script>



