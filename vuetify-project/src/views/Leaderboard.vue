<template>
    <v-container>
      <h1>Leaderboard</h1>
      <v-row>
        <v-col v-for="trail in trails" cols="12" sm="6" md="4">
          <v-card
            class="mx-auto"
            max-width="344"
            outlined
            raised
          >
            <v-card-title class=text-center>
              {{ trail.trail_name }}
            </v-card-title>
            <v-card-subtitle class=text-center>
              {{  trail.world_name }}
            </v-card-subtitle>
            
          </v-card>
        </v-col>
      </v-row>
    </v-container>

  </template>

<script>
export default {
  name: 'Leaderboard',
  data () {
    return {
      // fetch localhost:8082/get-trails
      trails: [],
    };
  },
  mounted () {
    fetch('http://localhost:8082/get-trails')
      .then(response => response.json())
      .then(data => {
        this.trails = data["trails"];
      });
  },
};
</script>