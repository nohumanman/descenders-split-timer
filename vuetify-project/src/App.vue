<template>
  <v-app>
    <!-- App Bar -->
    <v-app-bar app>

      <v-container>
        <v-row  align="center" justify="space-between">
          <v-col cols="auto">
            <router-link to="/">
              <img src="@/assets/logo.png" alt="Descenders Modkit Logo" height="40" />
            </router-link>
          </v-col>
          <v-col>
            <template v-for="route in routes">
              <v-btn
                v-if="route.name !== 'Home'"
                text
                :to="route.path"
                :key="route.name"
              >{{ route.name }}</v-btn>
            </template>
          </v-col>
        </v-row>
      </v-container>
      
      <template v-slot:append>
        <v-btn @click="toggleTheme" icon="mdi-weather-sunny"></v-btn>
        <v-btn icon="mdi-cog"></v-btn>
      </template>
      <v-spacer />

    </v-app-bar>

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
  import { useTheme } from 'vuetify'

  const theme = useTheme()

  function toggleTheme () {
    theme.global.name.value = theme.global.current.value.dark ? 'light' : 'dark'
  }
</script>

<script>
  import { routes } from '@/router'
  export default {
    name: 'App',
    data() {
      return {
        routes,
        darkMode: true
      }
    }
  }
</script>
