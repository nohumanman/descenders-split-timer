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
        <v-navigation-drawer width="400">
        <v-list-item title="Worlds"></v-list-item>
        <v-divider></v-divider>
        <v-list-item>
          <v-text-field
            v-model="worldSearch"
            prepend-icon="mdi-magnify"
            hide-details
            single-line
          ></v-text-field>
        </v-list-item>
        <v-list-item 
          v-for="world in searchedWorlds" 
          :key="world" 
          link 
          @click="selectWorld(world)" 
          :class="{ 'v-list-item--active': selectedWorld === world }"
        >
          {{ world }}
        </v-list-item>
      </v-navigation-drawer>
      </v-row>
      <v-row>
        <v-col v-for="trail in c_trails" cols="12" sm="12" md="12" lg="6">
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
              {{  trail.world_name }} <v-btn icon="mdi-refresh" @click="refreshLeaderboard(trail)"></v-btn>
            </v-card-subtitle>
            <v-data-table-virtual
              :loading="!trail.leaderboard"
              disable-sort
              :headers="headers"
              :items="trail.leaderboard"
              height="580"
              item-value="name"
            >
              <template v-slot:item.place="{ item }">
                {{ item.place }}
              </template>
              <template v-slot:item.name="{ item }">
                {{ item.name }}
              </template>
              <template v-slot:item.time="{ item }">
                {{ secs_to_str(item.time) }}
              </template>
              <template v-slot:item.time_id="{ item }">
                <v-btn :href="'/time/' + item.time_id">
                  <v-icon>mdi-open-in-new</v-icon>
                </v-btn>
              </template>
            </v-data-table-virtual>
          </v-card>
        </v-col>
      </v-row>
      </v-responsive>
    </v-container>
  </template>


<script>

const apiUrl = import.meta.env.VITE_APP_API_URL;
export default {
  name: 'Leaderboard',
  data () {
    return {
      // fetch localhost:8082/get-trails
      trails: [],
      headers: [
          { title: '#', align: 'start', key: 'place' },
          { title: 'Name', align: 'center', key: 'name' },
          { title: 'Time', align: 'center', key: 'time' },
          { title: '', align: 'end', key: 'time_id' },
        ],
      selectedWorld: '',
      worldSearch: '',
    };
  },
  computed: {
    c_trails: function () {
      return this.trails.filter(i => i.world_name == this.selectedWorld)
    },
    searchedWorlds: function(){
      return this.worlds.filter(i => i.toLowerCase().includes(this.worldSearch.toLowerCase()))
    },
    worlds: function () {
      var wrlds = [];
      for (let i = 0; i < this.trails.length; i++) {
        if (!wrlds.includes(this.trails[i].world_name)) {
          wrlds.push(this.trails[i].world_name);
        }
      }
      console.log(wrlds);
      return wrlds;
    },
  },
  methods: {
    async getLeaderboard(trail) {
      // for each trail in trail, find the leaderboard
      const response = await fetch(`${apiUrl}/get-leaderboard?trail_name=${trail.trail_name}&world_name=${trail.world_name}`);
      const data = await response.json();
      return data;
    },
    async selectWorld(world) {
      console.log(world);
      this.selectedWorld = world;
      // add leaderboard to each trail
      for (let i = 0; i < this.trails.length; i++) {
        if (this.trails[i].world_name == world) {
          this.trails[i].leaderboard = await this.getLeaderboard(this.trails[i]);
        }
      }
    },
    refreshLeaderboard(trail){
      for (let i = 0; i < this.trails.length; i++) {
        if (this.trails[i].world_name == trail.world_name && this.trails[i].trail_name == trail.trail_name) {
          this.trails[i].leaderboard = null;
          this.getLeaderboard(this.trails[i]).then(data => {
            this.trails[i].leaderboard = data;
          });
        }
      }
    },
    secs_to_str(secs){
            secs = parseFloat(secs);
            var d_mins = Math.floor(secs / 60);
            var d_secs = Math.floor(secs % 60)
            var fraction = secs * 1000;
            fraction = Math.round(fraction % 1000);
            d_mins = d_mins.toString();
            d_secs = d_secs.toString();
            fraction = fraction.toString();
            if (d_mins.length == 1)
                d_mins = "0" + d_mins.toString()
            if (d_secs.length == 1)
                d_secs = "0" + d_secs
            while (fraction.length < 3)
                fraction = "0" + fraction
            return d_mins + ":" + d_secs + "." + fraction
        },
  },
  mounted () {
    fetch(`${apiUrl}/get-trails`)
      .then(response => response.json())
      .then(async data => {
        this.trails = data["trails"];
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
      case 'xs': return 450
      case 'sm': return 600
      case 'md': return 950
      case 'lg': return 1200
      case 'xl': return 1100
      case 'xxl': return 1200
    }
    return undefined
  })

</script>