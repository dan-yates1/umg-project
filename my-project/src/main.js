import axios from 'axios';
import { BASE_URL } from './config';

axios.defaults.baseURL = BASE_URL;

const originalConsoleError = console.error;
console.error = (message) => {
  if (message && message.indexOf('ResizeObserver loop limit exceeded') > -1) {
    // Ignore ResizeObserver warning
  } else {
    originalConsoleError(message);
  }
};

import { createApp } from 'vue'
import App from './App.vue'

createApp(App).mount('#app')