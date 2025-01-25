<template>
  <v-container class="fill-height">
    <v-responsive
      class="align-centerfill-height mx-auto"
      max-width="900"
    >
      <v-img
        class="mb-4"
        height="150"
        src="@/assets/logo.png"
      />

      <div class="text-center">
        <div class="text-body-2 font-weight-light mb-n1">Welcome to the</div>
        <h1 class="text-h2 font-weight-bold">Descenders Modkit</h1>
        <div class="text-body-2 font-weight-light mb-n1">Developed on behalf of Descenders Competitive.</div>
      </div>

      <div class="py-4" />
  
      <v-row>
        <v-col cols="6">
          <v-card
            append-icon="mdi-open-in-app"
            class="py-4"
            color="surface-variant"
            prepend-icon="mdi-text-box-outline"
            :to="'/leaderboard'"
            rel="noopener noreferrer"
            rounded="lg"
            subtitle="See all of the trails and find the fastest times."
            title="Leaderboard"
            variant="text"
          >

            <v-overlay
              opacity=".06"
              scrim="primary"
              contained
              model-value
              persistent
            />
          </v-card>
        </v-col>

        <v-col cols="6">
          <v-card
            append-icon="mdi-open-in-app"
            class="py-4"
            color="surface-variant"
            :to="'/time-database'"
            prepend-icon="mdi-database"
            rel="noopener noreferrer"
            rounded="lg"
            subtitle="Request verification and see newly submitted times."
            title="Time Database"
            variant="text"
          >
            <v-overlay
              opacity=".06"
              scrim="primary"
              contained
              model-value
              persistent
            />
          </v-card>
        </v-col>

        <v-col cols="6">
          <v-card
            append-icon="mdi-open-in-app"
            class="py-4"
            color="surface-variant"
            :to="'/live-racing'"
            prepend-icon="mdi-bike"
            rel="noopener noreferrer"
            rounded="lg"
            subtitle="Tools to manage live races and streaming APIs."
            title="Live Racing Tools"
            variant="text"
          >
            <v-overlay
              opacity=".06"
              scrim="primary"
              contained
              model-value
              persistent
            />
          </v-card>
        </v-col>

        <v-col cols="6">
          <v-card
            append-icon="mdi-open-in-new"
            class="py-4"
            color="surface-variant"
            href="https://discord.gg/aqwnkgSxPQ/"
            prepend-icon="mdi-account-group-outline"
            rel="noopener noreferrer"
            rounded="lg"
            subtitle="Connect with the Descenders Competitive team."
            target="_blank"
            title="Community"
            variant="text"
          >
            <v-overlay
              opacity=".06"
              scrim="primary"
              contained
              model-value
              persistent
            />
          </v-card>
        </v-col>
        <v-col cols="3">
          <v-card
            class="py-4"
            color="primary"
            href="">
            <!-- Currently x users online, x times submitted in past 30 days -->
            <v-card-title>
              {{  totalUsersOnline }}
            </v-card-title>
            <v-card-subtitle>
              Users Online
            </v-card-subtitle>
          </v-card>
        </v-col>
        <v-col cols="3">
          <v-card
            class="py-4"
            color="blue"
            href="">
            <!-- Currently x users online, x times submitted in past 30 days -->
            <v-card-title>
              {{ timesSubmittedPast30Days }} 
            </v-card-title>
            <v-card-subtitle>
              times in past 30 days
            </v-card-subtitle>
          </v-card>
        </v-col>
        <v-col cols="3">
          <v-card
            class="py-4"
            color="primary"
            href="">
            <v-card-title>
              {{ totalStoredTimes }}
            </v-card-title>
            <v-card-subtitle>
              total stored times
            </v-card-subtitle>
          </v-card>
        </v-col>
        <v-col cols="3">
          <v-card
            class="py-4"
            color="primary"
            href="">
            <v-card-title>
              {{  totalReplaySize }}GB
            </v-card-title>
            <v-card-subtitle>
              of stored replays
            </v-card-subtitle>
          </v-card>
        </v-col>
      </v-row>
    </v-responsive>
  </v-container>
</template>

<script setup>
  //
</script>

<script>
  import { ref } from 'vue'

  var totalReplaySize = ref(0)
  var totalStoredTimes = ref(0)
  var totalUsersOnline = ref(0)
  var timesSubmittedPast30Days = ref(0)

  
  fetch('http://localhost:8082/get-gb-stored-replays')
    .then(response => response.json())
    .then(data => {
      totalReplaySize.value = data;
    })
    .catch(error => {
      totalReplaySize.value = "ERROR ";
    });
  
  fetch('http://localhost:8082/api/get-total-stored-times')
    .then(response => response.json())
    .then(data => {
      // import as integer
      totalStoredTimes.value = parseInt(data);
      // add commas to the number
      totalStoredTimes.value = totalStoredTimes.value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }).catch(error => {
      totalStoredTimes.value = "ERROR";
    });
  
  fetch('http://localhost:8082/api/get-total-users-online')
    .then(response => response.json())
    .then(data => {
      totalUsersOnline.value = data;
    }).catch(error => {
      totalUsersOnline.value = "ERROR";
    });
  
  var timestampThirtyDaysAgo = (new Date().getTime() - 30 * 24 * 60 * 60 * 1000) / 1000;
  console.log(timestampThirtyDaysAgo);
  fetch('http://localhost:8082/api/get-total-stored-times?timestamp=' + timestampThirtyDaysAgo.toString())
    
    .then(response => response.json())
    .then(data => {
      timesSubmittedPast30Days.value = parseInt(data);
      // add commas to the number
      timesSubmittedPast30Days.value = timesSubmittedPast30Days.value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }).catch(error => {
      timesSubmittedPast30Days.value = "ERROR";
    });
</script>
