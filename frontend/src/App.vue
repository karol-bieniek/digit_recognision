<script setup lang="ts">
import DigitPredicter from './components/DigitPredicter.vue'
</script>

<template>
  <header>
    <div class="wrapper">
      <DigitPredicter />
    </div>
  </header>

</template>

<style>
/* ==================== ZMIENNE GLOBALNE ==================== */
:root {
  --primary-color: #3b82f6;
  --success-color: #10b981;
  --warning-color: #f59e0b;
  --danger-color: #ef4444;
  --bg-light: #f3f4f6;
  --bg-white: #ffffff;
  --text-dark: #1f2937;
  --text-muted: #6b7280;
  --border-color: #e5e7eb;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
  --radius: 8px;
  --transition: all 0.3s ease;
}

/* ==================== STYLE GLOBALNE ==================== */
* {
  box-sizing: border-box;
}

body,
html {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
    Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: var(--bg-light);
  color: var(--text-dark);
}

#app {
  width: 100%;
  min-height: 100vh;
}
</style>

<style scoped>
header {
  width: 100%;
  line-height: 1.5;
  background-color: var(--bg-white);
  box-shadow: var(--shadow-sm);
  border-bottom: 1px solid var(--border-color);
}

.wrapper {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

@media (max-width: 768px) {
  .wrapper {
    padding: 1rem;
  }
}
</style>
