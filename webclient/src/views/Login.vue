<template>
  <div class="page-wrapper">

    <!-- Logo superior -->
    <div class="logo-wrapper">
      <img src="/NeuroBerry_horizontal.png" alt="NeuroBerry Logo" class="logo-image" />
    </div>

    <!-- Card del formulario con animación -->
    <transition name="fade" mode="out-in">
      <div class="auth-card" :key="activeTab">
        <!-- Pestañas Login/Register -->
        <div class="auth-tabs">
          <button 
            :class="{ active: activeTab === 'login' }" 
            @click="activeTab = 'login'"
          >
            Login
          </button>
          <button 
            :class="{ active: activeTab === 'register' }" 
            @click="activeTab = 'register'"
          >
            Register
          </button>
        </div>

        <!-- Formulario Login -->
        <form v-if="activeTab === 'login'" class="auth-form" @submit.prevent="handleLogin">
          <h2 class="form-title">Iniciar Sesión</h2>
          <input type="email" v-model="loginEmail" placeholder="Correo electrónico" required />
          <input type="password" v-model="loginPassword" placeholder="Contraseña" required />
          <button type="submit">Ingresar</button>
          <p class="forgot-password">¿Olvidaste tu contraseña?</p>
        </form>

        <!-- Formulario Register -->
        <form v-if="activeTab === 'register'" class="auth-form" @submit.prevent="handleRegister">
          <h2 class="form-title">Crear Cuenta</h2>
          <input type="text" v-model="registerName" placeholder="Nombre completo" required />
          <input type="email" v-model="registerEmail" placeholder="Correo electrónico" required />
          <input type="password" v-model="registerPassword" placeholder="Contraseña" required />
          <input type="password" v-model="registerConfirm" placeholder="Confirmar contraseña" required />
          <button type="submit">Registrarse</button>
        </form>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref } from 'vue'

const activeTab = ref('login')

// Login
const loginEmail = ref('')
const loginPassword = ref('')
const handleLogin = () => {
  alert(`Login con: ${loginEmail.value} / ${loginPassword.value}`)
}

// Register
const registerName = ref('')
const registerEmail = ref('')
const registerPassword = ref('')
const registerConfirm = ref('')
const handleRegister = () => {
  if(registerPassword.value !== registerConfirm.value) {
    alert('Las contraseñas no coinciden')
    return
  }
  alert(`Registro con: ${registerName.value}, ${registerEmail.value}`)
}
</script>

<style scoped>
.page-wrapper {
  width: 100%;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  font-family: 'Poppins', sans-serif;
  color: #333;
  padding: 2rem;
  background: #fefefe; /* Página limpia */
  flex-direction: column;
}

.logo-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: 1rem;
}

.logo-image {
  max-width: 400px;
  width: 90%;
  height: auto;
  border-radius: 10px;
}

/* Card */
.auth-card {
  background: white;
  border-radius: 20px;
  padding: 3rem 2.5rem;
  box-shadow: 0 20px 40px rgba(0,0,0,0.15);
  display: flex;
  flex-direction: column;
  gap: 2rem;
  width: 100%;
  max-width: 450px;
  transition: all 0.4s ease;
}

/* Pestañas */
.auth-tabs {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 2rem;
  border-radius: 15px;
  overflow: hidden;
  background: #f4f4f4;
}

.auth-tabs button {
  flex: 1;
  padding: 0.8rem 0;
  border: none;
  font-weight: 600;
  cursor: pointer;
  background-color: transparent;
  color: #b22222;
  font-size: 1.05rem;
  transition: all 0.3s ease;
}

.auth-tabs button.active {
  background-color: #b22222;
  color: white;
  box-shadow: 0 5px 15px rgba(178,34,34,0.3);
}

.auth-tabs button:hover {
  transform: scale(1.05);
}

/* Formularios */
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  animation: slide-up 0.5s ease;
}

.form-title {
  font-size: 2rem;
  font-weight: 800;
  color: #b22222;
  text-align: center;
}

/* Inputs grandes */
.auth-form input {
  padding: 0.8rem 1rem;
  border-radius: 12px;
  border: 2px solid #ddd;
  font-size: 1.1rem;
  outline: none;
  transition: all 0.3s ease;
}

.auth-form input:focus {
  border-color: #b22222;
  box-shadow: 0 0 12px rgba(178,34,34,0.35);
  transform: scale(1.02);
}

/* Botones grandes */
.auth-form button {
  padding: 0.8rem 1rem;
  border-radius: 12px;
  border: none;
  background: #b22222;
  color: white;
  font-weight: 700;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.auth-form button:hover {
  background: #8B0000;
  transform: translateY(-3px) scale(1.02);
  box-shadow: 0 8px 25px rgba(178,34,34,0.45);
}

/* Forgot password */
.forgot-password {
  font-size: 0.95rem;
  color: #b22222;
  text-decoration: underline;
  cursor: pointer;
  text-align: center;
  margin-top: 0.5rem;
}

/* Animaciones */
@keyframes slide-up {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.4s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* Responsive */
@media (max-width: 500px) {
  .auth-card {
    padding: 2rem;
  }

  .auth-form input, .auth-form button {
    font-size: 1rem;
  }

  .logo-image {
    max-width: 300px;
  }
}
</style>