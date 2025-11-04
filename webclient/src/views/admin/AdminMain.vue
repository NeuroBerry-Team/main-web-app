<template>
  <div class="page-wrapper">
    
    <header class="admin-header animated-item">
      <img src="/NeuroBerry_horizontal.png" alt="NeuroBerry Logo" class="header-logo" />
      <div class="header-text">
        <h1 class="header-title">Panel de Administración</h1>
        <p class="header-subtitle">Gestión de entrenamientos y usuarios.</p>
      </div>
    </header>

    <nav class="tabs-container animated-item" style="animation-delay: 0.1s;">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        class="tab-btn"
        :class="{ 'active': activeTab === tab.id }"
      >
        {{ tab.icon }} {{ tab.label }}
      </button>
    </nav>

    <main class="tab-content-card animated-item" style="animation-delay: 0.2s;">
      <transition name="fade" mode="out-in">
        <div v-if="activeTab === 'training'">
          <TrainingManager />
        </div>

        <div v-else-if="activeTab === 'users'">
          <UserManagement />
        </div>
      </transition>
    </main>
    
  </div>
</template>

<script setup>
// --- LÓGICA DEL COMPONENTE (SIN CAMBIOS) ---
import { ref, onMounted } from 'vue';
import { useAuth } from '../../composables/use_auth.js';
import TrainingManager from './TrainingManager.vue';
import UserManagement from './UserManagement.vue';

const { user, checkAuthStatus } = useAuth();
const activeTab = ref('training');

const tabs = ref([
  { id: 'training', label: 'Entrenamientos', icon: '🔄' },
  { id: 'users', label: 'Usuarios', icon: '👥' }
]);

onMounted(async () => {
  await checkAuthStatus();
});
</script>

<style scoped>
/* --- ESTILO GENERAL DE LA PÁGINA --- */
.page-wrapper {
  width: 100%;
  min-height: 100vh;
  padding: 2rem;
  padding-top: 7rem; /* Espacio para la navbar fija */
  font-family: 'Poppins', sans-serif;
  color: #333;
  background-color: #fff; /* Fondo blanco */
}

/* --- Encabezado con Logo (Ahora centrado y con contorno) --- */
.admin-header {
  max-width: 1200px;
  margin: 0 auto 2.5rem auto;
  display: flex;
  flex-direction: column; /* Coloca el logo arriba del texto */
  align-items: center;
  gap: 1.5rem;
  padding: 1.5rem 2rem;
  background-color: #fff; /* Fondo blanco para el encabezado */
  border-radius: 12px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.05); /* Sombra sutil */
  border: 1px solid #e0e0e0; /* Contorno sutil */
}
.header-logo {
  height: 60px;
  width: auto;
}
.header-text {
  text-align: center; /* Centra el texto del encabezado */
  color: #333; /* Color de texto oscuro para fondo blanco */
}
.header-title {
  font-size: 2.5rem;
  font-weight: 800;
  color: #b91c1c; /* Título en rojo corporativo */
  text-shadow: none; /* Sin sombra de texto en fondo blanco */
}
.header-subtitle {
  font-size: 1.1rem;
  color: #666; /* Subtítulo en gris oscuro */
}

/* --- Contenedor de Pestañas (con contorno) --- */
.tabs-container {
  max-width: 1200px;
  margin: 0 auto 1.5rem auto;
  display: flex;
  justify-content: center; /* Centra las pestañas */
  gap: 0.75rem;
  padding: 0.5rem;
  background-color: #f8fafc; /* Fondo ligeramente gris para la barra de pestañas */
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.04);
  border: 1px solid #e0e0e0;
}
.tab-btn {
  padding: 0.7rem 1.5rem;
  font-weight: 600;
  font-size: 1rem;
  color: #b91c1c; /* Color de texto rojo para pestañas inactivas */
  background: transparent;
  border: none;
  border-radius: 9999px;
  cursor: pointer;
  transition: all 0.25s ease;
  text-shadow: none; /* Sin sombra de texto */
}
.tab-btn:hover {
  background-color: rgba(185, 28, 28, 0.08); /* Rojo muy claro al pasar el mouse */
  color: #b91c1c;
}
.tab-btn.active {
  background-color: #b91c1c; /* Fondo rojo para la pestaña activa */
  color: #fff; /* Texto blanco para la pestaña activa */
  box-shadow: 0 4px 15px rgba(185, 28, 28, 0.3); /* Sombra más pronunciada para la activa */
}

/* --- Tarjeta de Contenido Principal (con contorno) --- */
.tab-content-card {
  max-width: 1200px;
  margin: 0 auto;
  background-color: #fff;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
  border: 1px solid #e0e0e0;
  color: #333;
  padding: 2.5rem;
}

/* --- Animaciones --- */
.animated-item {
  opacity: 0;
  animation: fadeInUp 0.7s ease-out forwards;
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* --- Responsividad --- */
@media (max-width: 768px) {
  .page-wrapper {
    padding-top: 6rem;
  }
  .admin-header {
    gap: 1rem;
    padding: 1rem;
  }
  .header-logo {
    height: 50px;
  }
  .header-title {
    font-size: 2rem;
  }
  .tabs-container {
    flex-wrap: wrap; /* Permite que las pestañas se envuelvan en pantallas pequeñas */
    gap: 0.5rem;
    padding: 0.4rem;
  }
  .tab-btn {
    padding: 0.6rem 1rem;
    font-size: 0.9rem;
  }
  .tab-content-card {
    padding: 1.5rem;
  }
}
</style>