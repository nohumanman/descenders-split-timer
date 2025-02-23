<template>
    <!-- Overlay that shows time info -->
    <v-overlay v-model="overlay" class="d-flex justify-center align-center">
      <v-card
        v-if="timeInfo != null"
        min-width="500px">
        <v-card-title class="text-center">
          {{ timeInfo.name }} {{ timeInfo.time }}
        </v-card-title>
        <v-card-subtitle class="text-center">
          {{ timeInfo.time_id }} - {{ timeInfo.version }}
        </v-card-subtitle>
        <v-card-text class="text-center">
          <!-- table of deleted, name, starting_speed, submission_timestamp, time, time_id, verified, version, bike -->
          <v-simple-table>
            <tbody>
              <tr>
                <td>Deleted</td>
                <td>{{ timeInfo.deleted }}</td>
              </tr>
              <tr>
                <td>Name</td>
                <td>{{ timeInfo.name }}</td>
              </tr>
              <tr>
                <td>Starting Speed</td>
                <td>{{ timeInfo.starting_speed }}</td>
              </tr>
              <tr>
                <td>Submission Timestamp</td>
                <td>{{ timeInfo.submission_timestamp }}</td>
              </tr>
              <tr>
                <td>Time</td>
                <td>{{ timeInfo.time }}</td>
              </tr>
              <tr>
                <td>Time ID</td>
                <td>{{ timeInfo.time_id }}</td>
              </tr>
              <tr>
                <td>Verified</td>
                <td>{{ timeInfo.verified }}</td>
              </tr>
              <tr>
                <td>Version</td>
                <td>{{ timeInfo.version }}</td>
              </tr>
              <tr>
                <td>Bike</td>
                <td>{{ timeInfo.bike }}</td>
              </tr>
            </tbody>
          </v-simple-table>
        </v-card-text>
        <!-- Image carousel of the invalid parts -->
         <v-container max-width="400">
          In the future, below will contain images where the user went off-track, for now, please enjoy pictures of cats because this feature isn't a priority
        </v-container>
        <v-carousel>
          <v-carousel-item
            v-for="(image, i) in catImages"
            :key="i"
          >
            <v-img
              :src="image"
              aspect-ratio="1"
              contain
            ></v-img>
          </v-carousel-item>
        </v-carousel>
        <v-card-actions>
          <!-- report button on top right-->
          <v-btn disabled @click="report = !report" icon class="position-absolute top-0 right-0" color="orange" v-bind="attrs" v-on="on"><v-icon>mdi-flag</v-icon></v-btn>
          <v-btn @click="clearTime();">Close</v-btn>
          <v-spacer></v-spacer>
          <v-btn :href="'/api/download-replay/' + timeInfo.time_id"><v-icon>mdi-download-circle</v-icon>Replay</v-btn>
        </v-card-actions>
      </v-card>
    </v-overlay>
    <v-overlay z-index="3000" v-model="report" class="d-flex justify-center align-center">
      <v-card>
        <v-card-title class="text-center">Report Issue</v-card-title>
        <v-card-text>
          <v-form>
            <v-text-field
              v-model="reportDetails"
              label="Details"
              type="text"
              required
            ></v-text-field>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-btn @click="submitReport">Submit</v-btn>
          <v-btn @click="report = false">Cancel</v-btn>
        </v-card-actions>
      </v-card>
    </v-overlay>
</template>

<script>
export default {
    props: {
        timeInfo: Object,
    },
    emits: ["update:timeInfo"],
    data : () => ({
        report: false,
        catImages: [
          "https://cdn2.thecatapi.com/images/1.jpg",
          "https://cdn2.thecatapi.com/images/2.jpg",
          "https://cdn2.thecatapi.com/images/3.jpg",
          "https://cdn2.thecatapi.com/images/4.jpg",
          "https://cdn2.thecatapi.com/images/5.jpg"
        ]
    }),
    computed: {
        overlay() {
            return this.timeInfo != null;
        }
    },
    methods: {
      clearTime(){
        this.$emit('update:timeInfo', null)
      }
    }
}
</script>
  
