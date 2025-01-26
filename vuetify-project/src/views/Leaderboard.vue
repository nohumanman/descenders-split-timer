<template>
    <v-container class="d-flex justify-center">
      <v-responsive
        class="align-center mx-auto"
        :max-width="height"
      >
      <v-row>
        <v-col cols="12">
          <v-card class="mx-auto" max-width="1000" outlined raised>
            <v-card-title class="text-center">
              Leaderboards
            </v-card-title>
          </v-card>
        </v-col>
      </v-row>
      <v-row>
        <v-col v-for="trail in trails" cols="12" sm="12" md="6">
          <v-card
            class="mx-auto"
            max-width="1000"
            outlined
            raised
          >
            <v-card-title class=text-center>
              {{ trail.trail_name }}
            </v-card-title>
            <v-card-subtitle class=text-center>
              {{  trail.world_name }}
            </v-card-subtitle>
            <v-data-table
              :headers="this.headers"
              :items="trail.leaderboard"
              height="400"
              item-value="name"
            >
              <template v-slot:item.place="{ item }">
                {{ item.place }}
              </template>
              <template v-slot:item.name="{ item }">
                {{ item.name }}
              </template>
              <template v-slot:item.time="{ item }">
                {{ item.time }}
              </template>
              <template v-slot:item.submission_timestamp="{ item }">
                {{ (
                  new Date(parseInt(item.submission_timestamp * 1000))
                  ).toLocaleDateString(
                    'en-uk', {
                      weekday: 'short',
                      year:'numeric',
                      month:'short',
                      day:'numeric'
                    }
                  )
                }}
              </template>
              <template v-slot:item.starting_speed="{ item }">
                {{ item.starting_speed }}
              </template>
              <template v-slot:item.time_id="{ item }">
                <v-btn :href="'localhost:8082/replay/' + item.time_id">Replay</v-btn>
              </template>
            </v-data-table>
          </v-card>
        </v-col>
      </v-row>
      </v-responsive>
    </v-container>
  </template>

<script>
export default {
  name: 'Leaderboard',
  data () {
    return {
      // fetch localhost:8082/get-trails
      trails: [],
      headers: [
          { title: '#', align: 'start', key: 'place' },
          { title: 'Name', align: 'end', key: 'name' },
          { title: 'Time', align: 'end', key: 'time' },
          { title: 'Time Submitted', align: 'end', key: 'submission_timestamp' },
          { title: 'Starting Speed', align: 'end', key: 'starting_speed'},
          { title: 'Replay', align: 'end', key: 'time_id' },
        ],
    };
  },
  methods: {
    async getLeaderboard(trail) {
      // for each trail in trail, find the leaderboard
      const response = await fetch('http://localhost:8082/get-leaderboard?trail_name=' + trail.trail_name + '&world_name=' + trail.world_name);
      const data = await response.json();
      return data;
    },
  },
  mounted () {
    fetch('http://localhost:8082/get-trails')
      .then(response => response.json())
    fetch('http://localhost:8082/get-trails')
      .then(response => response.json())
      .then(async data => {
        this.trails = data["trails"];
        for (const trail of this.trails) {
          trail.leaderboard = await this.getLeaderboard(trail);
        }
      })
    }
  };


</script>

<script setup>
    import { useDisplay } from 'vuetify'
    import { computed } from 'vue'

  // Destructure only the keys you want to use
  const { name } = useDisplay()
  const height = computed(() => {
    // name is reactive and
    // must use .value
    switch (name.value) {
      case 'xs': return 320
      case 'sm': return 470
      case 'md': return 950
      case 'lg': return 1200
      case 'xl': return 1100
      case 'xxl': return 1200
    }
    return undefined
  })

</script>