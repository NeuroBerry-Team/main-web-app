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
          
          <!-- Error message -->
          <div v-if="loginError" class="error-message">
            {{ loginError }}
          </div>
          
          <input 
            type="email" 
            v-model="loginEmail" 
            placeholder="Correo electrónico" 
            required 
            :disabled="loginLoading"
          />
          <input 
            type="password" 
            v-model="loginPassword" 
            placeholder="Contraseña" 
            required 
            :disabled="loginLoading"
          />
          <button type="submit" :disabled="loginLoading">
            {{ loginLoading ? 'Iniciando sesión...' : 'Ingresar' }}
          </button>
          <p class="forgot-password">¿Olvidaste tu contraseña?</p>
        </form>

        <!-- Formulario Register -->
        <form v-if="activeTab === 'register'" class="auth-form" @submit.prevent="handleRegister">
          <h2 class="form-title">Crear Cuenta</h2>
          
          <!-- Error message -->
          <div v-if="registerError" class="error-message">
            {{ registerError }}
          </div>
          
          <input 
            type="text" 
            v-model="registerName" 
            placeholder="Nombre completo" 
            required 
            :disabled="registerLoading"
          />
          <input 
            type="email" 
            v-model="registerEmail" 
            placeholder="Correo electrónico" 
            required 
            :disabled="registerLoading"
          />
          <input 
            type="password" 
            v-model="registerPassword" 
            placeholder="Contraseña" 
            required 
            :disabled="registerLoading"
          />
          <input 
            type="password" 
            v-model="registerConfirm" 
            placeholder="Confirmar contraseña" 
            required 
            :disabled="registerLoading"
          />
          <button type="submit" :disabled="registerLoading">
            {{ registerLoading ? 'Creando cuenta...' : 'Registrarse' }}
          </button>
        </form>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref } from 'vue'
const APIurl = import.meta.env.VITE_API_BASE_URL

const activeTab = ref('login')

// Login state
const loginEmail = ref('')
const loginPassword = ref('')
const loginLoading = ref(false)
const loginError = ref('')

const handleLogin = async () => {
  if (loginLoading.value) return
  
  loginLoading.value = true
  loginError.value = ''
  
  try {
    const response = await fetch(`${APIurl}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email: loginEmail.value,
        passwd: loginPassword.value
      }),
      credentials: 'include'  // This ensures cookies are sent and received
    })
    
    if (!response.ok) {
      const errorData = await response.text()
      let errorMessage = 'Login failed'
      
      if (response.status === 401) {
        errorMessage = 'Invalid email or password'
      } else if (response.status === 400) {
        errorMessage = 'Please check your email and password'
      } else {
        errorMessage = `Server error: ${response.status}`
      }
      
      throw new Error(errorMessage)
    }
    
    const data = await response.json()
    
    if (data.loggedIn) {
      // Successfully logged in, redirect to home
      window.location.href = '/'
    } else {
      throw new Error('Login failed - invalid response')
    }
    
  } catch (error) {
    loginError.value = error.message
    console.error('Login error:', error)
  } finally {
    loginLoading.value = false
  }
}

// Register state
const registerName = ref('')
const registerEmail = ref('')
const registerPassword = ref('')
const registerConfirm = ref('')
const registerLoading = ref(false)
const registerError = ref('')

const handleRegister = async () => {
  if (registerLoading.value) return
  
  registerLoading.value = true
  registerError.value = ''
  
  // Basic validation
  if (registerPassword.value !== registerConfirm.value) {
    registerError.value = 'Passwords do not match'
    registerLoading.value = false
    return
  }
  
  if (registerPassword.value.length < 6) {
    registerError.value = 'Password must be at least 6 characters'
    registerLoading.value = false
    return
  }
  
  try {
    // Note: You'll need to implement a public registration endpoint
    // or handle user creation through an admin interface
    registerError.value = 'Registration is not yet implemented. Please contact an administrator.'
  } catch (error) {
    registerError.value = error.message
    console.error('Registration error:', error)
  } finally {
    registerLoading.value = false
  }
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

/* Error messages */
.error-message {
  background: #ffe6e6;
  border: 1px solid #ff9999;
  color: #cc0000;
  padding: 0.8rem;
  border-radius: 8px;
  font-size: 0.9rem;
  margin-bottom: 1rem;
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

.auth-form input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
  opacity: 0.7;
}

.auth-form input:focus:not(:disabled) {
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

.auth-form button:disabled {
  background: #999;
  cursor: not-allowed;
  transform: none;
}

.auth-form button:hover:not(:disabled) {
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