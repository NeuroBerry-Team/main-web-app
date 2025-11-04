<template>
  <div class="page-wrapper">
    
    <div class="login-card animated-item">
      <div class="header-section">
        <img src="/NeuroBerry_horizontal.png" alt="NeuroBerry Logo" class="logo-image" />
        <p class="subtitle">Plataforma de Cosecha Inteligente</p>
      </div>

      <nav class="tabs-container">
        <button class="tab-btn" :class="{ 'active': activeTab === 'login' }" @click="activeTab = 'login'">
          Iniciar Sesión
        </button>
        <button class="tab-btn" :class="{ 'active': activeTab === 'register' }" @click="activeTab = 'register'">
          Registrarse
        </button>
      </nav>

      <div class="form-content">
        <transition name="form-fade" mode="out-in">
          <form v-if="activeTab === 'login'" class="form-wrapper" @submit.prevent="handleLogin" key="login">
            <div v-if="loginError" class="alert alert-error">
              <p>{{ loginError }}</p>
            </div>
            <div class="form-group">
              <label for="login-email" class="form-label">Correo Electrónico</label>
              <input id="login-email" type="email" v-model="loginEmail" required :disabled="loginLoading" class="form-input" />
            </div>
            <div class="form-group">
              <label for="login-password" class="form-label">Contraseña</label>
              <input id="login-password" type="password" v-model="loginPassword" required :disabled="loginLoading" class="form-input" />
            </div>
            <button type="submit" :disabled="loginLoading" class="action-btn btn-primary">
              <span v-if="loginLoading" class="spinner"></span>
              <span>{{ loginLoading ? 'Verificando...' : 'Iniciar Sesión' }}</span>
              <span v-if="!loginLoading" class="arrow-icon">→</span>
            </button>
          </form>

          <form v-else class="form-wrapper" @submit.prevent="handleRegister" key="register">
             <div v-if="registerError" class="alert alert-error">
              <p>{{ registerError }}</p>
            </div>
            <div class="form-grid">
              <div class="form-group">
                <label for="register-name" class="form-label">Nombre</label>
                <input id="register-name" type="text" v-model="registerName" required :disabled="registerLoading" class="form-input" />
              </div>
              <div class="form-group">
                <label for="register-lastname" class="form-label">Apellido</label>
                <input id="register-lastname" type="text" v-model="registerLastName" required :disabled="registerLoading" class="form-input" />
              </div>
            </div>
            <div class="form-group">
              <label for="register-email" class="form-label">Correo Electrónico</label>
              <input id="register-email" type="email" v-model="registerEmail" required :disabled="registerLoading" class="form-input" />
            </div>
            <div class="form-group">
              <label for="register-password" class="form-label">Contraseña</label>
              <input id="register-password" type="password" v-model="registerPassword" required :disabled="registerLoading" class="form-input" />
            </div>
             <div class="form-group">
              <label for="register-confirm" class="form-label">Confirmar Contraseña</label>
              <input id="register-confirm" type="password" v-model="registerConfirm" required :disabled="registerLoading" class="form-input" />
            </div>
            <button type="submit" :disabled="registerLoading" class="action-btn btn-primary">
              <span v-if="registerLoading" class="spinner"></span>
              <span>{{ registerLoading ? 'Creando cuenta...' : 'Crear Cuenta' }}</span>
              <span v-if="!registerLoading" class="arrow-icon">→</span>
            </button>
          </form>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup>
// --- LÓGICA DEL COMPONENTE (SIN CAMBIOS) ---
import { ref } from 'vue';
import { useCSRF } from '../composables/use_csrf.js';
import { useToast } from "vue-toastification";

const APIurl = import.meta.env.VITE_API_BASE_URL;
const { makeSecureRequest } = useCSRF();
const toast = useToast();
const activeTab = ref('login');
const loginEmail = ref('');
const loginPassword = ref('');
const loginLoading = ref(false);
const loginError = ref('');
const registerName = ref('');
const registerLastName = ref('');
const registerEmail = ref('');
const registerPassword = ref('');
const registerConfirm = ref('');
const registerLoading = ref(false);
const registerError = ref('');

const handleLogin = async () => {
  if (loginLoading.value) return;
  loginLoading.value = true;
  loginError.value = '';
  try {
    const response = await fetch(`${APIurl}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: loginEmail.value, passwd: loginPassword.value }),
      credentials: 'include'
    });
    if (!response.ok) {
      let errorMessage = 'Error al iniciar sesión';
      if (response.status === 401) errorMessage = 'Email o contraseña incorrectos';
      else if (response.status === 400) errorMessage = 'Por favor verifica tu email y contraseña';
      else errorMessage = `Error del servidor: ${response.status}`;
      throw new Error(errorMessage);
    }
    const data = await response.json();
    if (data.loggedIn) {
      window.location.href = '/';
    } else {
      throw new Error('Error al iniciar sesión - respuesta inválida');
    }
  } catch (error) {
    loginError.value = error.message;
  } finally {
    loginLoading.value = false;
  }
};
const handleRegister = async () => {
  if (registerLoading.value) return;
  registerLoading.value = true;
  registerError.value = '';
  if (registerPassword.value !== registerConfirm.value) {
    registerError.value = 'Las contraseñas no coinciden';
    registerLoading.value = false;
    return;
  }
  try {
    const response = await makeSecureRequest(`${APIurl}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: registerName.value,
        lastName: registerLastName.value,
        email: registerEmail.value,
        password: registerPassword.value
      })
    });
    const data = await response.json();
    if (response.ok) {
      registerName.value = '';
      registerLastName.value = '';
      registerEmail.value = '';
      registerPassword.value = '';
      registerConfirm.value = '';
      toast.success(data.message || '¡Registro exitoso! Por favor inicia sesión.');
      activeTab.value = 'login';
    } else {
      registerError.value = data.message || data.error || `Error del servidor: ${response.status}`;
    }
  } catch (error) {
    registerError.value = error.message || 'Error en el registro';
  } finally {
    registerLoading.value = false;
  }
};
</script>

<style scoped>
/* --- Estilo de Página --- */
.page-wrapper {
  width: 100%;
  min-height: 100vh;
  padding: 1rem;
  padding-top: 6rem;
  font-family: 'Poppins', sans-serif;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  background-color: #fff;
  overflow-x: hidden;
}
@media (min-width: 640px) {
  .page-wrapper {
    padding: 2rem;
    padding-top: 8rem;
  }
}

/* --- Tarjeta Principal --- */
.login-card {
  width: 100%;
  max-width: 500px;
  background-color: #fff;
  border-radius: 24px;
  box-shadow: 0 20px 50px rgba(0,0,0,0.1);
  border: 1px solid #e5e7eb;
  padding: 1.5rem;
}
@media (min-width: 640px) {
  .login-card {
    padding: 2.5rem;
  }
}

/* --- Encabezado --- */
.header-section { text-align: center; margin-bottom: 1.5rem; }
@media (min-width: 640px) {
  .header-section { margin-bottom: 2rem; }
}
.logo-image { 
  height: 40px; 
  width: auto; 
  margin: 0 auto 0.75rem auto;
}
@media (min-width: 640px) {
  .logo-image {
    height: 50px;
    margin: 0 auto 1rem auto;
  }
}
.subtitle { 
  color: #b91c1c; 
  font-weight: 500;
  font-size: 0.9rem;
}
@media (min-width: 640px) {
  .subtitle {
    font-size: 1rem;
  }
}

/* --- Pestañas --- */
.tabs-container {
  display: flex;
  gap: 0.5rem;
  padding: 0.5rem;
  background-color: #f3f4f6;
  border-radius: 12px;
  margin-bottom: 1.5rem;
}
@media (min-width: 640px) {
  .tabs-container {
    margin-bottom: 2rem;
  }
}
.tab-btn {
  flex: 1;
  padding: 0.6rem;
  font-weight: 600;
  font-size: 0.9rem;
  color: #4b5563;
  background: transparent;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.25s ease;
  word-wrap: break-word;
  overflow-wrap: break-word;
  hyphens: auto;
}
@media (min-width: 640px) {
  .tab-btn {
    padding: 0.75rem;
    font-size: 1rem;
  }
}
.tab-btn:hover { background-color: #e5e7eb; }
.tab-btn.active {
  background: linear-gradient(45deg, #b91c1c, #991b1b);
  color: #fff;
  box-shadow: 0 4px 15px rgba(185, 28, 28, 0.3);
}

/* --- Formularios --- */
.form-content { margin-top: 1.5rem; }
.form-wrapper { display: flex; flex-direction: column; gap: 1.25rem; }
@media (min-width: 640px) {
  .form-wrapper { gap: 1.5rem; }
}
.form-grid { 
  display: grid; 
  grid-template-columns: 1fr; 
  gap: 1rem;
}
@media (min-width: 640px) {
  .form-grid { 
    grid-template-columns: 1fr 1fr;
  }
}
.form-group { 
  display: flex; 
  flex-direction: column; 
  gap: 0.5rem; 
  text-align: left;
  min-width: 0;
}
.form-label { 
  font-weight: 600; 
  font-size: 0.85rem; 
  color: #444;
  word-wrap: break-word;
}
@media (min-width: 640px) {
  .form-label {
    font-size: 0.9rem;
  }
}
.form-input {
  width: 100%;
  padding: 0.7rem 0.9rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  transition: all 0.2s ease;
  font-size: 0.95rem;
  background-color: #f9fafb;
  box-sizing: border-box;
}
@media (min-width: 640px) {
  .form-input {
    padding: 0.8rem 1rem;
    font-size: 1rem;
  }
}
.form-input:focus {
  outline: none;
  border-color: #b91c1c;
  box-shadow: 0 0 0 3px rgba(178, 34, 34, 0.1);
  background-color: #fff;
}

/* --- Alertas y Botones --- */
.alert { 
  padding: 0.85rem; 
  border-radius: 8px; 
  text-align: center; 
  border-left: 5px solid; 
  font-weight: 500; 
  animation: shake 0.5s ease;
  word-wrap: break-word;
  overflow-wrap: break-word;
  font-size: 0.9rem;
}
@media (min-width: 640px) {
  .alert {
    padding: 1rem;
    font-size: 1rem;
  }
}
.alert-error { background-color: #fef2f2; border-color: #ef4444; color: #991b1b; }
.action-btn {
  display: flex; 
  align-items: center; 
  justify-content: center; 
  gap: 0.5rem;
  padding: 0.85rem 1.5rem; 
  border-radius: 12px; 
  color: white;
  border: none; 
  font-size: 1rem; 
  font-weight: 700;
  cursor: pointer; 
  transition: all 0.3s ease; 
  text-decoration: none;
  background: linear-gradient(45deg, #b91c1c, #991b1b);
  box-shadow: 0 10px 20px -5px rgba(185, 28, 28, 0.4);
  word-wrap: break-word;
  text-align: center;
}
@media (min-width: 640px) {
  .action-btn {
    gap: 0.75rem;
    padding: 1rem 2rem;
    font-size: 1.1rem;
  }
}
.action-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 25px -5px rgba(185, 28, 28, 0.5);
}
.action-btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
.arrow-icon { transition: transform 0.3s ease; }
.action-btn:hover .arrow-icon { transform: translateX(4px); }

/* --- Animaciones --- */
.animated-item { opacity: 0; animation: fadeInUp 0.7s ease-out forwards; }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.form-fade-enter-active, .form-fade-leave-active { transition: all 0.4s ease; }
.form-fade-enter-from { opacity: 0; transform: translateX(20px); }
.form-fade-leave-to { opacity: 0; transform: translateX(-20px); }
.spinner { width: 1.25rem; height: 1.25rem; border: 2px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes shake {
  10%, 90% { transform: translateX(-1px); }
  20%, 80% { transform: translateX(2px); }
  30%, 50%, 70% { transform: translateX(-4px); }
  40%, 60% { transform: translateX(4px); }
}
</style>