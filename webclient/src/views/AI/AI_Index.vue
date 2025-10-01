<template>
  <div class="page-wrapper">
    
    <div class="logo-wrapper animated-item">
      <img src="/NeuroBerry_horizontal.png" alt="NeuroBerry Logo" class="logo-image" />
    </div>

    <div v-if="!isOnChildRoute">
      <section v-if="authLoading" class="loading-section">
        <h1 class="loading-text">Verificando autenticación...</h1>
      </section>

      <div v-if="!authLoading" class="main-content">
        <section class="content-section animated-item" style="animation-delay: 0.1s;">
          <h1 class="section-title">Centro de IA</h1>
          <p class="section-text">
            Bienvenido al centro de inteligencia artificial de NeuroBerry. Aquí puedes analizar imágenes de frambuesas y entrenar modelos de IA.
          </p>
          
          <div v-if="isLoggedIn && user?.name" class="user-status status-logged-in">
            Conectado como: <strong>{{ user.name }} {{ user.lastName }}</strong>
          </div>
          <div v-else-if="!isLoggedIn" class="user-status status-logged-out">
            No has iniciado sesión
          </div>
        </section>

        <section class="action-buttons-container">
          <router-link
            v-if="isAdmin"
            to="/AI/train"
            class="action-btn btn-admin animated-item"
            style="animation-delay: 0.2s;"
          >
            <span>🧠</span>
            <span>Entrenar IA</span>
          </router-link>
          
          <router-link
            v-if="isLoggedIn"
            to="/AI/inference"
            class="action-btn btn-user animated-item"
            style="animation-delay: 0.3s;"
          >
            <span>🔍</span>
            <span>Analizar Imagen</span>
          </router-link>
          
          <router-link
            v-if="!isLoggedIn"
            to="/login"
            class="action-btn btn-login animated-item"
            style="animation-delay: 0.2s;"
          >
            <span>🔐</span>
            <span>Iniciar Sesión</span>
          </router-link>
        </section>

        <section v-if="!isLoggedIn" class="features-grid">
          <div class="feature-card animated-item" style="animation-delay: 0.3s;">
            <div class="feature-icon">🔍</div>
            <h3 class="feature-title">Análisis de Imágenes</h3>
            <p class="feature-text">Analiza imágenes de frambuesas con nuestra IA avanzada para obtener información detallada.</p>
          </div>
          
          <div class="feature-card animated-item" style="animation-delay: 0.4s;">
            <div class="feature-icon">🧠</div>
            <h3 class="feature-title">Entrenamiento IA</h3>
            <p class="feature-text">Funcionalidad avanzada para administradores para entrenar y mejorar los modelos de IA.</p>
          </div>
          
          <div class="feature-card animated-item" style="animation-delay: 0.5s;">
            <div class="feature-icon">⚡</div>
            <h3 class="feature-title">Resultados Rápidos</h3>
            <p class="feature-text">Obtén análisis precisos y rápidos de tus imágenes en cuestión de segundos.</p>
          </div>
        </section>
      </div>
    </div>
    
    <router-view v-slot="{ Component }">
      <transition name="fade-router" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from '../../composables/use_auth.js'

const { isLoggedIn, isAdmin, user, loading: authLoading, checkAuthStatus } = useAuth()
const route = useRoute()
const isOnChildRoute = computed(() => route.path !== '/AI')

onMounted(() => {
  checkAuthStatus()
})
</script>

<style scoped>

.page-wrapper {
  width: 100%;
  min-height: 100vh;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Poppins', sans-serif;
  color: #333;
  display: flex;
  flex-direction: column;
  gap: 3rem;
  text-align: center;
  background-color: #fff;
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 3rem;
}

.logo-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
  margin-bottom: 1rem;
}

.logo-image {
  max-width: 500px;
  width: 90%;
  height: auto;
  animation: fadeInUp 0.8s ease-out;
}

.content-section {
  background-color: #fff;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.08);
  padding: 2rem 2.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.section-title {
  font-size: 2.5rem;
  font-weight: 800;
  color: #b22222;
}

.section-text {
  max-width: 800px;
  font-size: 1.1rem;
  line-height: 1.7;
  color: #555;
}

.loading-section {
  padding: 4rem;
}
.loading-text {
  font-size: 1.5rem;
  font-weight: 600;
  color: #888;
  animation: pulsate 1.5s ease-in-out infinite;
}

.user-status {
  padding: 0.5rem 1.25rem;
  border-radius: 20px;
  font-weight: 500;
  border: 1px solid transparent;
}
.status-logged-in {
  background-color: #e6f7f0;
  color: #0d8a4f;
  border-color: #a3e9c9;
}
.status-logged-out {
  background-color: #fff8e1;
  color: #e6a700;
  border-color: #ffecb3;
}

.action-buttons-container {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  justify-content: center;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 0.8rem 2rem;
  border-radius: 25px;
  color: white;
  border: none;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  text-decoration: none;
}
.action-btn:hover {
  transform: translateY(-4px) scale(1.03);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}
.btn-admin { background: linear-gradient(45deg, #4f46e5, #7c3aed); }
.btn-user { background: linear-gradient(45deg, #16a34a, #059669); }
.btn-login { background: linear-gradient(45deg, #dc2626, #c026d3); }


.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  margin-top: 1rem;
}

.feature-card {
  background-color: #f9fafb;
  padding: 2rem;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.08);
}
.feature-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}
.feature-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 0.5rem;
}
.feature-text {
  font-size: 1rem;
  line-height: 1.6;
  color: #666;
}

.animated-item {
  opacity: 0;
  animation: fadeInUp 0.7s ease-out forwards;
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes pulsate {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.fade-router-enter-active,
.fade-router-leave-active {
  transition: opacity 0.3s ease;
}
.fade-router-enter-from,
.fade-router-leave-to {
  opacity: 0;
}
</style>