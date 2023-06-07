<template>
  <div id="app" class="container mt-5">
    <h1 class="text-center text-success mb-4">My Track Watchlist</h1>
    <div v-if="!loggedIn">
      <div class="row">
        <div class="col-md-6">
          <h2 class="text-success mb-3">Register</h2>
          <form @submit.prevent="register" class="mb-4">
            <div class="form-group">
              <input v-model="username" type="text" id="username" class="form-control" placeholder="Username" required>
            </div>
            <div class="form-group">
              <input v-model="password" type="password" id="password" class="form-control" placeholder="Password" required>
            </div>
            <button type="submit" class="btn btn-success btn-block">Register</button>
          </form>
        </div>

        <div class="col-md-6">
          <h2 class="text-success mb-3">Login</h2>
          <form @submit.prevent="login">
            <div class="form-group">
              <input v-model="loginUsername" type="text" id="loginUsername" class="form-control" placeholder="Username" required>
            </div>
            <div class="form-group">
              <input v-model="loginPassword" type="password" id="loginPassword" class="form-control" placeholder="Password" required>
            </div>
            <button type="submit" class="btn btn-success btn-block">Login</button>
          </form>
        </div>
      </div>
    </div>

    <div v-else>
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h2 class="text-success">Welcome, {{ username }}!</h2>
        <button @click="logout" class="btn btn-outline-danger">Logout</button>
      </div>
      <div class="form-group">
        <input v-model="newTrack" type="text" class="form-control mb-2" placeholder="Add new track">
        <button @click="addTrack" class="btn btn-success btn-block">Add Track</button>
      </div>
      <form @submit.prevent="searchTracks(searchQuery)" class="mb-4">
        <div class="input-group">
          <input v-model="searchQuery" type="text" placeholder="Search tracks..." class="form-control">
          <div class="input-group-append">
            <button type="submit" class="btn btn-outline-success">Search</button>
            <button type="button" class="btn btn-outline-danger" @click="resetTracks">Reset</button>
          </div>
        </div>
      </form>
      <ul class="list-group mb-4">
        <li v-for="track in tracks" :key="track.id" class="list-group-item d-flex justify-content-between align-items-center bg-dark">
          {{ track.name }}
          <div>
            <button @click="editTrack(track)" class="btn btn-outline-success mr-2">Edit</button>
            <button @click="deleteTrack(track.id)" class="btn btn-outline-danger">Delete</button>
          </div>
        </li>
        <p v-if="tracks.length === 0" class="text-muted">You don't have any tracks in your list. Start by adding a new one!</p>
      </ul>
    </div>
    
    <div v-if="editingTrack">
      <h2 class="text-success mb-3">Edit Track</h2>
      <form @submit.prevent="updateTrack(editingTrack.id, editingTrack)">
        <div class="form-group">
          <input v-model="editingTrack.name" type="text" id="editTrackName" class="form-control" placeholder="Track Name" required>
        </div>
        <button type="submit" class="btn btn-success btn-block">Update Track</button>
      </form>
    </div>

    <div v-if="popupMessage" class="alert alert-success alert-dismissible fade show" role="alert">
      {{ popupMessage }}
      <button type="button" class="close" @click="popupMessage = null" aria-label="Close">
        <span aria-hidden="true">&times;</span>
      </button>
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
      userId: null,
      loginUsername: '',
      loginPassword: '',
      editingTrack: null,
      searchInput: '',
      isHovered: false,
      isClicked: false,
      searchQuery: '',
      originalTracks: [],
      popupMessage: null
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
        const response = await axios.post('http://localhost:5000/login', {
          username: this.loginUsername,
          password: this.loginPassword
        });
        this.loggedIn = true;
        this.username = this.loginUsername;
        this.loginUsername = '';
        this.loginPassword = '';
        localStorage.setItem('access_token', response.data.access_token);
        this.userId = response.data.user_id;
        console.log(response.data);
        await this.getTracks();
      } catch (error) {
        console.log(error);
      }
    },

    async getTracks() {
      try {
        const token = localStorage.getItem('access_token');
        const response = await axios.get('http://localhost:5000/api/tracks', {
          headers: { Authorization: `Bearer ${token}` }
        });
        const userId = this.userId;
        this.tracks = response.data.filter(track => track.user_id === userId);
      } catch (error) {
        console.error('Error getting tracks:', error);
      }
    },

    async logout() {
      try {
        localStorage.removeItem('access_token');
        this.loggedIn = false;
        this.user = null;
      } catch (error) {
        console.error(error);
      }
    },

    async addTrack() {
      try {
        const token = localStorage.getItem('access_token');
        const response = await axios.post('http://localhost:5000/api/tracks', {
          name: this.newTrack
        }, {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.tracks.push(response.data);
        this.newTrack = '';
      } catch (error) {
        console.error('Error adding track:', error);
      }
    },


    async editTrack(track) {
      this.editingTrack = Object.assign({}, track);
    },
 
    async updateTrack(id, updatedData) {
      try {
          const token = localStorage.getItem('access_token');
          const response = await axios.put(`http://localhost:5000/api/tracks/${id}`, updatedData, {
              headers: { Authorization: `Bearer ${token}` }
          });
          if (response.status === 200) {
              const index = this.tracks.findIndex(track => track.id === id);
              if (index !== -1) {
                  this.tracks.splice(index, 1, updatedData);
              }
              this.editingTrack = null;
              this.popupMessage = 'Track updated successfully';
              setTimeout(() => { this.popupMessage = null }, 3000);
          }
      } catch (error) {
          console.error('Error updating track:', error);
    }
  },

    async deleteTrack(id) {
      try {
          const token = localStorage.getItem('access_token');
          const response = await axios.delete(`http://localhost:5000/api/tracks/${id}`, {
              headers: { Authorization: `Bearer ${token}` }
          });
          if (response.status === 200) {
              this.tracks = this.tracks.filter(track => track.id !== id);
              this.popupMessage = 'Track deleted successfully';
              setTimeout(() => { this.popupMessage = null }, 3000);
          }
      } catch (error) {
        console.error('Error deleting track:', error);
      }
    },

    async searchTracks(query) {
        try {
            const token = localStorage.getItem('access_token');
            const response = await axios.get(`http://localhost:5000/api/tracks/search?query=${query}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            if (response.status === 200) {
                this.originalTracks = [...this.tracks]; 
                this.tracks = response.data;
            }
        } catch (error) {
            console.error('Error searching tracks:', error);
        }

    },
    resetTracks() {
        this.tracks = [...this.originalTracks];
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
