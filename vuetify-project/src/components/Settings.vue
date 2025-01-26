<template v-slot:append>
    <v-btn @click="toggleTheme" icon="mdi-weather-sunny"></v-btn>
    <v-menu
        :close-on-content-click="false"
        location="end"
    >
        <template v-slot:activator="{ props }">
            <v-btn v-bind="props" icon="mdi-cog"></v-btn>
        </template>
        <v-card min-width="300">
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn variant="text">Logout</v-btn>
            </v-card-actions>
            </v-card>
    </v-menu>
</template>

<script setup>
    import { useTheme } from 'vuetify'
  const theme = useTheme()

    // Load the theme from localStorage if available
    if (localStorage.getItem('theme')) {
    theme.global.name.value = localStorage.getItem('theme')
    }

    function toggleTheme () {
    const newTheme = theme.global.current.value.dark ? 'light' : 'dark'
    theme.global.name.value = newTheme
    localStorage.setItem('theme', newTheme)
    }
</script>