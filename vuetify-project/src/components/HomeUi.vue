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
      </v-row>
    </v-responsive>
  </v-container>
</template>

<script setup>
  //
</script>
