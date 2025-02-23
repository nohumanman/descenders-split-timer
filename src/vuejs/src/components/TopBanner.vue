<template>
    <v-banner
      bg-color="warning"
      icon="mdi-wifi-strength-alert-outline"
      lines="one"
      sticky
    >
      <template v-slot:text>
        Server API offline! Please check your connection.
      </template>

    </v-banner>
  </template>