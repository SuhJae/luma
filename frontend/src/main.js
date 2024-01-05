import './style.css' // Critical CSS
import { createApp } from 'vue'
import App from './App.vue'

createApp(App).mount('#app')

// Asynchronously load non-critical CSS
function loadNonCriticalCSS() {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = './font.css';
    document.head.appendChild(link);
}

// You might want to run this after your Vue app is mounted, or after initial data requests
document.addEventListener('DOMContentLoaded', loadNonCriticalCSS);
