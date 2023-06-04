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