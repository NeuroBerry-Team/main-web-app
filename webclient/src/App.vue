<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div id="app">
    <header>
      <div class="header-content">

        <!-- MENU -->
        <nav>
          <RouterLink to="/" class="nav-button">Inicio</RouterLink>
          <RouterLink to="/about" class="nav-button">Proyecto</RouterLink>
          <RouterLink to="/database" class="nav-button">Database</RouterLink>
          <RouterLink to="/etiquetado" class="nav-button">Etiquetado</RouterLink>
          <RouterLink to="/iatest" class="nav-button">Aplicación</RouterLink>
          <RouterLink to="/login" class="nav-button">Login</RouterLink>
        </nav>
      </div>
    </header>

    <main class="view-container">
      <RouterView />
    </main>
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap');

#app {
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  font-family: 'Poppins', sans-serif;
}

header {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  background-color: #c0392b;
  color: white;
  padding: 1rem 0;
  display: flex;
  justify-content: center;
  box-shadow: 0 6px 15px rgba(0,0,0,0.2);
  z-index: 1000;
  transition: background-color 0.3s ease;
}

header:hover {
  background-color: #e74c3c;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2rem;
  width: 100%;
  max-width: 1200px;
}

nav {
  display: flex;
  gap: 1rem;
  flex: 1;
  justify-content: center;
  flex-wrap: wrap;
}

.nav-button {
  padding: 0.8rem 2rem;
  border-radius: 50px;
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
  font-weight: 500;
  text-decoration: none;
  font-size: 1.05rem;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
  text-align: center;
}

.nav-button:hover {
  background-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 4px 12px rgba(0,0,0,0.25);
}

.nav-button.router-link-exact-active {
  background-color: rgba(255, 255, 255, 0.4);
}

.view-container {
  width: 100%;
  min-height: 100vh;
  margin-top: 90px;
  padding: 2rem;
  box-sizing: border-box;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 0.5rem;
  }
  nav {
    gap: 0.5rem;
    flex-direction: column;
    justify-content: center;
  }
  .nav-button {
    width: 100%;
  }
}
</style>