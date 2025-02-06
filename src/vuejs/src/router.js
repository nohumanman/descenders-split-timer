import { createRouter, createWebHistory } from 'vue-router';
import Home from './views/Home.vue';
import Leaderboard from './views/Leaderboard.vue';
import LiveRacing from './views/LiveRacing.vue';
import TimeDatabase from './views/TimeDatabase.vue';

const routes = [
  { path: '/', name: 'Home', component: Home, inHomeBar: false },
  { path: '/leaderboard', name: 'Leaderboard', component: Leaderboard, inHomeBar: true },
  { path: '/time-database', name: 'Time Database', component: TimeDatabase, inHomeBar: true },
  { path: '/live-racing', name: 'Live Racing', component: LiveRacing, inHomeBar: true },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
export { routes }; // Export routes for use in the App.vue component
