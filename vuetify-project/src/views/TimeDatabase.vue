<template>
  <v-container fluid width="100%"
  height="90%">
  <v-text-field
        v-model="search"
        append-icon="mdi-magnify"
        label="Search"
        single-line
        hide-details
        class="mb-4"
      />
  <v-container
    fluid
    width="100%"
    height="100%"
    class="d-flex justify-center d-sm-flex"
  >      
      
      <v-data-table-server
          width="100%"
          height="100%"
          v-model:items-per-page="itemsPerPage"
          :headers="headers"
          :items="serverItems"
          :items-length="totalItems"
          :loading="loading"
          :search="search"
          item-value="name"
          @update:options="loadItems"
        >
        <template v-slot:item.verified="{ item }">
          <v-icon v-if="item.verified" color="success">mdi-check</v-icon>
          <v-icon v-else color="error">mdi-close</v-icon>
        </template>
        <template v-slot:item.submission_timestamp="{ item }">
          {{ new Date(item.submission_timestamp * 1000).toLocaleString() }}
        </template>
        <template v-slot:item.time_id="{ item }">
          <v-btn target="_blank" :href="'/time/' + item.time_id">
            <v-icon>mdi-open-in-new</v-icon>
          </v-btn>
        </template>
      </v-data-table-server>
    </v-container>
  </v-container>
  </template>  

  <script>
  const desserts = [
      {
        place: 2,
        starting_speed: 3,
        "name": "JOe Mama",
        "bike": "enduro",
        "version": "1.34",
        "verified": true,
        "time_id": 67876567876545678,
        "time": 2,
        "submission_timestamp": 1737854835,
    }
  ]

  const FakeAPI = {
    async fetch ({ page, itemsPerPage, sortBy }) {
      return new Promise(resolve => {
        setTimeout(() => {
          const start = (page - 1) * itemsPerPage
          const end = start + itemsPerPage
          const items = desserts.slice()

          if (sortBy.length) {
            const sortKey = sortBy[0].key
            const sortOrder = sortBy[0].order
            items.sort((a, b) => {
              const aValue = a[sortKey]
              const bValue = b[sortKey]
              return sortOrder === 'desc' ? bValue - aValue : aValue - bValue
            })
          }

          const paginated = items.slice(start, end)

          resolve({ items: paginated, total: items.length })
        }, 500)
      })
    },
  }

  export default {
    data: () => ({
      itemsPerPage: 30,
      headers: [
        { title: 'Player Name', key: 'name', align: 'start', },
        { title: 'Bike Type', key: 'bike', align: 'end' },
        { title: 'Verified', key: 'verified', align: 'end' },
        { title: 'Modkit Version', key: 'version', align: 'end' },
        { title: 'Game Version', key: 'game_version', align: 'end' },
        { title: 'Time', key: 'time', align: 'center' },
        { title: 'Submission Date', key: 'submission_timestamp', align: 'end' },
        { title: '', key: 'time_id', align: 'end' },
      ],
      search: '',
      serverItems: [],
      loading: true,
      totalItems: 0,
    }),
    methods: {
      loadItems ({ page, itemsPerPage, sortBy }) {
        this.loading = true
        FakeAPI.fetch({ page, itemsPerPage, sortBy }).then(({ items, total }) => {
          this.serverItems = items
          this.totalItems = total
          this.loading = false
        })
      },
    },
  }
</script>