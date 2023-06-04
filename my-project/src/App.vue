<template>
  <div id="app" class="container mt-4">
    <h1 class="text-center mb-5">My Track Watchlist</h1>

    <div v-if="!loggedIn">
      <div class="card mb-4">
        <div class="card-header">Register</div>
        <div class="card-body">
          <form @submit.prevent="register">
            <div class="form-group">
              <label for="username">Username:</label>
              <input v-model="username" type="text" id="username" class="form-control" required>
            </div>
            <div class="form-group">
              <label for="password">Password:</label>
              <input v-model="password" type="password" id="password" class="form-control" required>
            </div>
            <button type="submit" class="btn btn-primary">Register</button>
          </form>
        </div>
      </div>

      <div class="card">
        <div class="card-header">Login</div>
        <div class="card-body">
          <form @submit.prevent="login">
            <div class="form-group">
              <label for="loginUsername">Username:</label>
              <input v-model="loginUsername" type="text" id="loginUsername" class="form-control" required>
            </div>
            <div class="form-group">
              <label for="loginPassword">Password:</label>
              <input v-model="loginPassword" type="password" id="loginPassword" class="form-control" required>
            </div>
            <button type="submit" class="btn btn-primary">Login</button>
          </form>
        </div>
      </div>
    </div>

    <div v-else>
      <ul class="list-group mb-4">
        <li v-for="track in tracks" :key="track.id" class="list-group-item bg-dark text-white">
          {{ track.name }}

          <button @click="deleteTrack(track.id)" class="btn btn-danger ml-2">Delete</button>
        </li>
      </ul>

      <input v-model="newTrack" type="text" class="form-control mb-3" placeholder="Add new track">
      <button @click="addTrack" class="btn btn-primary">Add Track</button>
    </div>
  </div>

  <div v-if="editingTrack" class="card mb-4">
      <div class="card-header">Edit Track</div>
      <div class="card-body">
        <form @submit.prevent="updateTrack">
          <div class="form-group">
            <label for="editTrackName">Track Name:</label>
            <input v-model="editingTrack.name" type="text" id="editTrackName" class="form-control" required>
          </div>
          <button type="submit" class="btn btn-primary">Update Track</button>
        </form>
      </div>
    </div>
</template>

<script>
import axios from 'axios';

axios.defaults.withCredentials = true;

export default {
  data() {
    return {
      tracks: [],
      newTrack: '',
      loggedIn: false,
      username: '',
      password: '',
      loginUsername: '',
      loginPassword: ''
    };
  },
  methods: {
    async register() {
      try {
        await axios.post('http://localhost:5000/register', {
          username: this.username,
          password: this.password
        });
        this.username = '';
        this.password = '';
      } catch (error) {
        console.log(error);
      }
    },
    async login() {
      try {
        await axios.post('http://localhost:5000/login', {
          username: this.loginUsername,
          password: this.loginPassword
        });
        this.loggedIn = true;
        this.loginUsername = '';
        this.loginPassword = '';
        const response = await axios.get('http://localhost:5000/api/track');
        this.tracks = response.data;
      } catch (error) {
        console.log(error);
      }
    },
    async logout() {
      try {
        await axios.post('/logout');
        this.loggedIn = false;
        this.user = null;
      } catch (error) {
        console.error(error);
      }
    },
    async addTrack() {
      const response = await axios.post('http://localhost:5000/api/track', { name: this.newTrack });
      this.tracks.push(response.data);
      this.newTrack = '';
    },
    async editTrack(track) {
      this.editingTrack = Object.assign({}, track);
    },
    async updateTrack() {
      if (!this.editingTrack.name) return;

      try {
        await axios.put(`http://localhost:5000/api/track/${this.editingTrack.id}`, { name: this.editingTrack.name });
        this.fetchTracks();
        this.editingTrack = null;
      } catch (error) {
        console.error(error);
      }
    },
    async deleteTrack(id) {
      try {
        await axios.delete(`http://localhost:5000/api/track/${id}`);
        this.tracks = this.tracks.filter(track => track.id !== id);
      } catch (error) {
        console.error('Error deleting track:', error);
      }
    }
  }
};
</script>

<style>
#app {
  text-align: center;
  margin-top: 60px;
}

ul {
  list-style-type: none;
  padding: 0;
}

input {
  margin-right: 10px;
}
</style>