<template>
  <div class="page-wrapper">
    
    <div class="logo-wrapper animated-item">
      <img src="/NeuroBerry_horizontal.png" alt="NeuroBerry Logo" class="logo-image" />
    </div>

    <section v-if="authLoading" class="content-section animated-item">
      <h1 class="section-title">Cargando perfil...</h1>
    </section>

    <div v-else-if="isLoggedIn" class="main-content">
      <section class="hero-section animated-item" style="animation-delay: 0.1s;">
        <h1 class="hero-title">Mi Perfil</h1>
        <div class="role-badge" :class="getRoleBadgeClass(user?.role)">
          {{ user?.role || 'Usuario' }}
        </div>
        <p class="hero-text">
          <span v-if="user?.name">Bienvenido de nuevo, {{ user.name }}.</span>
          Desde aquí puedes gestionar tu actividad y acceder a todas las funciones de NeuroBerry.
        </p>
      </section>

      <section class="content-section animated-item" style="animation-delay: 0.2s;">
        <h2 class="section-title">Acceso Rápido</h2>
        <div class="card-grid">
          <router-link to="/AI/inference" class="feature-card animated-item" style="animation-delay: 0.3s;">
            <div class="feature-icon">🔍</div>
            <h3 class="feature-title">Analizar Imagen</h3>
            <p class="feature-text">Sube una imagen y obtén un análisis detallado de su estado de madurez.</p>
          </router-link>
          <router-link v-if="isAdmin" to="/AI/train" class="feature-card animated-item" style="animation-delay: 0.4s;">
            <div class="feature-icon">🧠</div>
            <h3 class="feature-title">Entrenar IA</h3>
            <p class="feature-text">Entrena y mejora los modelos de IA con nuevos datasets.</p>
          </router-link>
          <router-link v-if="isAdmin" to="/database" class="feature-card animated-item" style="animation-delay: 0.5s;">
            <div class="feature-icon">📊</div>
            <h3 class="feature-title">Base de Datos</h3>
            <p class="feature-text">Explora nuestra colección de imágenes organizadas en 5 clases de madurez.</p>
          </router-link>
        </div>
      </section>

      <section class="content-section animated-item" style="animation-delay: 0.3s;">
        <h2 class="section-title">Gestión de Perfil</h2>
        <div class="card-grid">
          <router-link to="/profile/activity" class="feature-card animated-item" style="animation-delay: 0.4s;">
            <div class="feature-icon">📈</div>
            <h3 class="feature-title">Mi Actividad</h3>
            <p class="feature-text">Revisa tu historial de análisis, métricas de uso y logs de actividad.</p>
          </router-link>
          <router-link to="/profile/settings" class="feature-card animated-item" style="animation-delay: 0.5s;">
            <div class="feature-icon">⚙️</div>
            <h3 class="feature-title">Configuración</h3>
            <p class="feature-text">Modifica tu información personal y preferencias de la cuenta.</p>
          </router-link>
        </div>
      </section>

      <section v-if="isAdmin" class="content-section admin-section animated-item" style="animation-delay: 0.4s;">
        <h2 class="section-title">Panel de Administración</h2>
         <p class="section-text">Tienes permisos especiales para gestionar usuarios y funciones avanzadas.</p>
        <router-link to="/admin" class="action-btn btn-secondary">
          Ir al Panel de Admin
        </router-link>
      </section>
    </div>

    <section v-else class="content-section animated-item">
      <h1 class="section-title">Acceso Requerido</h1>
      <p class="section-text">
        Para acceder a tu perfil y utilizar las funciones de NeuroBerry, necesitas iniciar sesión.
      </p>
      <router-link to="/login" class="action-btn btn-primary">
        Iniciar Sesión
      </router-link>
    </section>

    <div class="nested-view-wrapper">
      <router-view />
    </div>
  </div>
</template>

<script setup>
// --- LÓGICA DEL COMPONENTE (SIN CAMBIOS) ---
import { onMounted } from 'vue'
import { useAuth } from '../../composables/use_auth.js'

const { isLoggedIn, user, loading: authLoading, checkAuthStatus, isAdmin } = useAuth()

const getRoleBadgeClass = (role) => {
  switch(role) {
    case 'ADMIN':
    case 'SUPERADMIN':
      return 'role-admin'
    case 'AI_USER':
      return 'role-ai-user'
    default:
      return 'role-default'
  }
}

onMounted(() => {
  checkAuthStatus()
})
</script>

<style scoped>
/* --- ESTILOS VISUALES COHERENTES --- */
.page-wrapper {
  width: 100%;
  min-height: 100vh;
  padding: 1rem;
  padding-top: 7rem;
  font-family: 'Poppins', sans-serif;
  color: #333;
  background-color: #fff;
  overflow-x: hidden;
}
@media (min-width: 640px) {
  .page-wrapper {
    padding: 2rem;
    padding-top: 7rem;
  }
}
.main-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}
@media (min-width: 768px) {
  .main-content {
    gap: 3rem;
  }
}

/* --- Estilo para centrar el logo --- */
.logo-wrapper {
  display: flex;
  flex-direction: column;
  /* Esta propiedad centra horizontalmente el contenido del div */
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
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  background-color: #fff;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.07);
  padding: 1.5rem;
  text-align: center;
  border: 1px solid #e5e7eb;
  overflow-x: hidden;
  word-wrap: break-word;
}
@media (min-width: 768px) {
  .content-section {
    padding: 2.5rem;
  }
}
.section-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: #b22222;
  margin-bottom: 1.5rem;
  word-wrap: break-word;
  overflow-wrap: break-word;
  hyphens: auto;
}
@media (min-width: 640px) {
  .section-title {
    font-size: 1.8rem;
  }
}
@media (min-width: 768px) {
  .section-title {
    font-size: 2.2rem;
  }
}
.section-text {
  max-width: 800px;
  margin: -1rem auto 1.5rem auto;
  font-size: 0.95rem;
  line-height: 1.7;
  color: #555;
  word-wrap: break-word;
  overflow-wrap: break-word;
}
@media (min-width: 640px) {
  .section-text {
    font-size: 1rem;
  }
}
@media (min-width: 768px) {
  .section-text {
    font-size: 1.1rem;
  }
}

/* --- Sección Hero (Bienvenida) --- */
.hero-section {
  background: linear-gradient(45deg, #b91c1c, #7f1d1d);
  color: white;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(185, 28, 28, 0.25);
  overflow-x: hidden;
}
@media (min-width: 768px) {
  .hero-section {
    padding: 3rem;
  }
}
.hero-title {
  font-size: 1.8rem;
  font-weight: 800;
  color: #fff;
  margin-bottom: 1.5rem;
  text-shadow: 0 2px 4px rgba(0,0,0,0.2);
  word-wrap: break-word;
}
@media (min-width: 640px) {
  .hero-title {
    font-size: 2.2rem;
  }
}
@media (min-width: 768px) {
  .hero-title {
    font-size: 2.8rem;
  }
}
.hero-text {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1rem;
  margin-top: 1rem;
  word-wrap: break-word;
  overflow-wrap: break-word;
}
@media (min-width: 768px) {
  .hero-text {
    font-size: 1.2rem;
  }
}
.role-badge {
  display: inline-block;
  padding: 0.5rem 1.25rem;
  border-radius: 9999px;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.8rem;
  letter-spacing: 0.5px;
}
.role-admin { background: linear-gradient(45deg, #f59e0b, #f97316); color: #fff; }
.role-ai-user { background: linear-gradient(45deg, #3b82f6, #2563eb); color: #fff; }
.role-default { background: linear-gradient(45deg, #10b981, #059669); color: #fff; }


/* --- Tarjetas Interactivas --- */
.card-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  text-align: left;
}
@media (min-width: 640px) {
  .card-grid {
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 280px), 1fr));
    gap: 2rem;
  }
}
.feature-card {
  background-color: #f9fafb;
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  text-decoration: none;
  color: inherit;
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
  word-wrap: break-word;
  min-width: 0;
}
@media (min-width: 768px) {
  .feature-card {
    padding: 2rem;
  }
}
.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 15px 30px -5px rgba(0,0,0,0.1);
}
.feature-icon {
  font-size: 2rem;
  margin-bottom: 1rem;
}
@media (min-width: 768px) {
  .feature-icon {
    font-size: 2.5rem;
  }
}
.feature-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 0.75rem;
  word-wrap: break-word;
  overflow-wrap: break-word;
  hyphens: auto;
}
@media (min-width: 768px) {
  .feature-title {
    font-size: 1.4rem;
  }
}
.feature-text {
  font-size: 0.9rem;
  line-height: 1.6;
  color: #666;
  flex-grow: 1;
  word-wrap: break-word;
  overflow-wrap: break-word;
}
@media (min-width: 768px) {
  .feature-text {
    font-size: 1rem;
  }
}

/* --- Sección de Admin --- */
.admin-section {
  background-color: #fffbeb;
  border: 1px solid #fde68a;
}
.admin-section .section-title {
  color: #b45309;
}

/* --- Botones de Acción --- */
.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.7rem 1.5rem;
  border-radius: 25px;
  color: white;
  border: none;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  text-decoration: none;
  word-wrap: break-word;
  text-align: center;
  max-width: 100%;
}
@media (min-width: 768px) {
  .action-btn {
    gap: 0.75rem;
    padding: 0.8rem 2rem;
    font-size: 1.1rem;
  }
}
.action-btn:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}
.btn-primary { background: linear-gradient(45deg, #b91c1c, #991b1b); }
.btn-secondary { background: linear-gradient(45deg, #16a34a, #059669); }

/* --- Animaciones --- */
.animated-item {
  opacity: 0;
  animation: fadeInUp 0.7s ease-out forwards;
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* --- Wrapper para Vistas Anidadas --- */
.nested-view-wrapper {
  margin-top: 1rem;
}
</style>