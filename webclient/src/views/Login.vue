<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-800 via-red-700 to-red-600 p-4 relative overflow-hidden">
    <!-- Animated background elements -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-red-500/20 to-orange-500/20 rounded-full blur-3xl animate-pulse"></div>
      <div class="absolute -bottom-40 -left-40 w-96 h-96 bg-gradient-to-tr from-red-600/20 to-pink-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
      <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-60 h-60 bg-gradient-to-r from-red-400/10 to-orange-400/10 rounded-full blur-2xl animate-ping delay-500"></div>
    </div>
    
    <div class="bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl shadow-red-900/20 p-8 w-full max-w-md transition-all duration-700 hover:shadow-3xl hover:shadow-red-900/30 hover:bg-white relative z-10 border border-white/20 group">
      <!-- Logo section with subtle animation -->
      <div class="text-center mb-8 transition-all duration-500">
        <div class="relative inline-block">
          <img src="/NeuroBerry_Logo.png" alt="NeuroBerry" class="h-16 mx-auto mb-3 drop-shadow-lg transition-all duration-700 group-hover:drop-shadow-2xl group-hover:brightness-110" />
          <div class="absolute inset-0 bg-gradient-to-r from-red-500 to-orange-500 rounded-full blur-xl opacity-20 animate-pulse transition-opacity duration-700 group-hover:opacity-30"></div>
        </div>
        <h1 class="text-3xl font-bold bg-gradient-to-r from-red-700 via-red-600 to-orange-600 bg-clip-text text-transparent animate-gradient-x bg-300% drop-shadow-sm transition-all duration-500 group-hover:from-red-600 group-hover:via-red-500 group-hover:to-orange-500">
          NeuroBerry
        </h1>
        <p class="text-gray-600 text-sm mt-2 opacity-80 transition-all duration-500 group-hover:opacity-100 group-hover:text-gray-700">Plataforma de Cosecha Inteligente</p>
      </div>

      <!-- Animated tabs with subtle hover effects -->
      <div class="flex bg-gradient-to-r from-gray-50 to-gray-100 rounded-2xl p-1.5 mb-8 shadow-inner">
        <button 
          :class="[
            'flex-1 py-3 px-6 rounded-xl font-bold text-sm transition-all duration-300 relative overflow-hidden',
            activeTab === 'login' 
              ? 'bg-gradient-to-r from-red-600 to-red-700 text-white shadow-lg shadow-red-500/30' 
              : 'text-gray-600 hover:text-red-700 hover:bg-white/70 hover:shadow-md'
          ]"
          @click="activeTab = 'login'"
        >
          <span class="relative z-10 transition-all duration-200">Iniciar Sesión</span>
          <div v-if="activeTab === 'login'" class="absolute inset-0 bg-gradient-to-r from-red-500/20 to-red-600/20 animate-pulse"></div>
        </button>
        <button 
          :class="[
            'flex-1 py-3 px-6 rounded-xl font-bold text-sm transition-all duration-300 relative overflow-hidden',
            activeTab === 'register' 
              ? 'bg-gradient-to-r from-red-600 to-red-700 text-white shadow-lg shadow-red-500/30' 
              : 'text-gray-600 hover:text-red-700 hover:bg-white/70 hover:shadow-md'
          ]"
          @click="activeTab = 'register'"
        >
          <span class="relative z-10 transition-all duration-200">Registrarse</span>
          <div v-if="activeTab === 'register'" class="absolute inset-0 bg-gradient-to-r from-red-500/20 to-red-600/20 animate-pulse"></div>
        </button>
      </div>

      <!-- Login Form -->
      <form v-if="activeTab === 'login'" class="space-y-6 transform transition-all duration-500 ease-out" @submit.prevent="handleLogin">
        <div class="text-center mb-6">
          <h2 class="text-2xl font-bold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent mb-2">¡Bienvenido de vuelta!</h2>
          <p class="text-gray-500 text-sm">Ingresa tus credenciales para continuar</p>
        </div>
        
        <div v-if="loginError" class="bg-gradient-to-r from-red-50 to-pink-50 border-l-4 border-red-500 p-4 rounded-r-2xl shadow-lg transition-all duration-300 hover:shadow-xl hover:border-l-6 animate-shake">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center animate-bounce">
                <span class="text-white text-sm font-bold">!</span>
              </div>
            </div>
            <p class="ml-3 text-red-700 font-medium">{{ loginError }}</p>
          </div>
        </div>
        
        <div class="space-y-2 group">
          <label for="login-email" class="block text-sm font-bold text-gray-700 group-focus-within:text-red-600 transition-colors duration-200">
            Correo Electrónico
          </label>
          <div class="relative">
            <input 
              id="login-email"
              type="email" 
              v-model="loginEmail" 
              placeholder="ejemplo@correo.com" 
              required 
              :disabled="loginLoading"
              class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-red-500 focus:ring-4 focus:ring-red-100 transition-all duration-300 disabled:bg-gray-50 hover:border-red-300 group bg-gradient-to-r from-white to-gray-50 shadow-inner"
            />
            <div class="absolute inset-0 rounded-xl bg-gradient-to-r from-red-500/5 to-orange-500/5 opacity-0 group-focus-within:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
          </div>
        </div>

        <div class="space-y-2 group">
          <label for="login-password" class="block text-sm font-bold text-gray-700 group-focus-within:text-red-600 transition-colors duration-200">
            Contraseña
          </label>
          <div class="relative">
            <input 
              id="login-password"
              type="password" 
              v-model="loginPassword" 
              placeholder="Tu contraseña segura" 
              required 
              :disabled="loginLoading"
              class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-red-500 focus:ring-4 focus:ring-red-100 transition-all duration-300 disabled:bg-gray-50 hover:border-red-300 group bg-gradient-to-r from-white to-gray-50 shadow-inner"
            />
            <div class="absolute inset-0 rounded-xl bg-gradient-to-r from-red-500/5 to-orange-500/5 opacity-0 group-focus-within:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
          </div>
        </div>

        <button 
          type="submit" 
          :disabled="loginLoading" 
          class="w-full bg-gradient-to-r from-red-600 via-red-700 to-red-800 hover:from-red-700 hover:via-red-800 hover:to-red-900 text-white py-4 px-6 rounded-xl font-bold text-lg shadow-lg shadow-red-500/30 hover:shadow-xl hover:shadow-red-500/50 focus:ring-4 focus:ring-red-200 disabled:opacity-70 disabled:cursor-not-allowed transition-all duration-300 disabled:hover:shadow-lg relative overflow-hidden group"
        >
          <div class="absolute inset-0 bg-gradient-to-r from-red-500 to-orange-500 opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
          <div class="relative flex items-center justify-center gap-3">
            <span v-if="loginLoading" class="w-6 h-6 border-3 border-white/30 border-t-white rounded-full animate-spin"></span>
            <span>{{ loginLoading ? 'Verificando...' : 'Iniciar Sesión' }}</span>
            <div v-if="!loginLoading" class="transform transition-transform duration-300 group-hover:translate-x-1">
              →
            </div>
          </div>
        </button>
        
        <div class="text-center pt-4">
          <p class="text-gray-600 text-sm hover:text-red-700 cursor-pointer transition-all duration-200 inline-block">
            ¿Olvidaste tu contraseña? 
            <span class="font-semibold underline decoration-red-300 hover:decoration-red-500 hover:decoration-2">Recupérala aquí</span>
          </p>
        </div>
      </form>

      <!-- Registration Form -->
      <form v-if="activeTab === 'register'" class="space-y-5 transform transition-all duration-500 ease-out" @submit.prevent="handleRegister">
        <div class="text-center mb-6">
          <h2 class="text-2xl font-bold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent mb-2">¡Únete a nosotros!</h2>
          <p class="text-gray-500 text-sm">Crea tu cuenta para comenzar la experiencia</p>
        </div>
        
        <div v-if="registerError" class="bg-gradient-to-r from-red-50 to-pink-50 border-l-4 border-red-500 p-4 rounded-r-2xl shadow-lg transition-all duration-300 hover:shadow-xl hover:border-l-6 animate-shake">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center animate-bounce">
                <span class="text-white text-sm font-bold">!</span>
              </div>
            </div>
            <p class="ml-3 text-red-700 font-medium">{{ registerError }}</p>
          </div>
        </div>
        
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div class="space-y-2 group">
            <label for="register-name" class="block text-sm font-bold text-gray-700 group-focus-within:text-red-600 transition-colors duration-200">
              Nombre
            </label>
            <div class="relative">
              <input 
                id="register-name"
                type="text" 
                v-model="registerName" 
                placeholder="Tu nombre" 
                required 
                :disabled="registerLoading"
                class="w-full px-3 py-3 border-2 border-gray-200 rounded-xl focus:border-red-500 focus:ring-4 focus:ring-red-100 transition-all duration-300 disabled:bg-gray-50 hover:border-red-300 bg-gradient-to-r from-white to-gray-50 shadow-inner"
              />
              <div class="absolute inset-0 rounded-xl bg-gradient-to-r from-red-500/5 to-orange-500/5 opacity-0 group-focus-within:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
            </div>
          </div>
          
          <div class="space-y-2 group">
            <label for="register-lastname" class="block text-sm font-bold text-gray-700 group-focus-within:text-red-600 transition-colors duration-200">
              Apellido
            </label>
            <div class="relative">
              <input 
                id="register-lastname"
                type="text" 
                v-model="registerLastName" 
                placeholder="Tu apellido" 
                required 
                :disabled="registerLoading"
                class="w-full px-3 py-3 border-2 border-gray-200 rounded-xl focus:border-red-500 focus:ring-4 focus:ring-red-100 transition-all duration-300 disabled:bg-gray-50 hover:border-red-300 bg-gradient-to-r from-white to-gray-50 shadow-inner"
              />
              <div class="absolute inset-0 rounded-xl bg-gradient-to-r from-red-500/5 to-orange-500/5 opacity-0 group-focus-within:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
            </div>
          </div>
        </div>

        <div class="space-y-2 group">
          <label for="register-email" class="block text-sm font-bold text-gray-700 group-focus-within:text-red-600 transition-colors duration-200">
            Correo Electrónico
          </label>
          <div class="relative">
            <input 
              id="register-email"
              type="email" 
              v-model="registerEmail" 
              placeholder="ejemplo@correo.com" 
              required 
              :disabled="registerLoading"
              class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-red-500 focus:ring-4 focus:ring-red-100 transition-all duration-300 disabled:bg-gray-50 hover:border-red-300 bg-gradient-to-r from-white to-gray-50 shadow-inner"
            />
            <div class="absolute inset-0 rounded-xl bg-gradient-to-r from-red-500/5 to-orange-500/5 opacity-0 group-focus-within:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
          </div>
        </div>

        <div class="space-y-2 group">
          <label for="register-password" class="block text-sm font-bold text-gray-700 group-focus-within:text-red-600 transition-colors duration-200">
            Contraseña
          </label>
          <div class="relative">
            <input 
              id="register-password"
              type="password" 
              v-model="registerPassword" 
              placeholder="Mínimo 8 caracteres, con letras y números" 
              required 
              :disabled="registerLoading"
              class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-red-500 focus:ring-4 focus:ring-red-100 transition-all duration-300 disabled:bg-gray-50 hover:border-red-300 bg-gradient-to-r from-white to-gray-50 shadow-inner"
            />
            <div class="absolute inset-0 rounded-xl bg-gradient-to-r from-red-500/5 to-orange-500/5 opacity-0 group-focus-within:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
          </div>
          <small class="text-gray-600 text-xs flex items-center gap-2">
            <span class="w-4 h-4 bg-gradient-to-r from-green-400 to-green-500 rounded-full flex items-center justify-center">
              <span class="text-white text-xs">✓</span>
            </span>
            Debe contener al menos 8 caracteres, una letra y un número
          </small>
        </div>

        <div class="space-y-2 group">
          <label for="register-confirm" class="block text-sm font-bold text-gray-700 group-focus-within:text-red-600 transition-colors duration-200">
            Confirmar Contraseña
          </label>
          <div class="relative">
            <input 
              id="register-confirm"
              type="password" 
              v-model="registerConfirm" 
              placeholder="Repite tu contraseña" 
              required 
              :disabled="registerLoading"
              class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-red-500 focus:ring-4 focus:ring-red-100 transition-all duration-300 disabled:bg-gray-50 hover:border-red-300 bg-gradient-to-r from-white to-gray-50 shadow-inner"
            />
            <div class="absolute inset-0 rounded-xl bg-gradient-to-r from-red-500/5 to-orange-500/5 opacity-0 group-focus-within:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
          </div>
        </div>

        <button 
          type="submit" 
          :disabled="registerLoading" 
          class="w-full bg-gradient-to-r from-red-600 via-red-700 to-red-800 hover:from-red-700 hover:via-red-800 hover:to-red-900 text-white py-4 px-6 rounded-xl font-bold text-lg shadow-lg shadow-red-500/30 hover:shadow-xl hover:shadow-red-500/50 focus:ring-4 focus:ring-red-200 disabled:opacity-70 disabled:cursor-not-allowed transition-all duration-300 disabled:hover:shadow-lg relative overflow-hidden group mt-6"
        >
          <div class="absolute inset-0 bg-gradient-to-r from-red-500 to-orange-500 opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
          <div class="relative flex items-center justify-center gap-3">
            <span v-if="registerLoading" class="w-6 h-6 border-3 border-white/30 border-t-white rounded-full animate-spin"></span>
            <span>{{ registerLoading ? 'Creando cuenta...' : 'Crear Cuenta' }}</span>
            <div v-if="!registerLoading" class="transform transition-transform duration-300 group-hover:translate-x-1">
              →
            </div>
          </div>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useCSRF } from '../composables/use_csrf.js'
import { useToast } from "vue-toastification"

const APIurl = import.meta.env.VITE_API_BASE_URL
const { makeSecureRequest } = useCSRF()
const toast = useToast()

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
      credentials: 'include'
    })
    
    if (!response.ok) {
      const errorData = await response.text()
      let errorMessage = 'Error al iniciar sesión'
      
      if (response.status === 401) {
        errorMessage = 'Email o contraseña incorrectos'
      } else if (response.status === 400) {
        errorMessage = 'Por favor verifica tu email y contraseña'
      } else {
        errorMessage = `Error del servidor: ${response.status}`
      }
      
      throw new Error(errorMessage)
    }
    
    const data = await response.json()
    
    if (data.loggedIn) {
      window.location.href = '/'
    } else {
      throw new Error('Error al iniciar sesión - respuesta inválida')
    }
    
  } catch (error) {
    loginError.value = error.message
  } finally {
    loginLoading.value = false
  }
}

// Register state
const registerName = ref('')
const registerLastName = ref('')
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
  if (!registerName.value || registerName.value.trim().length < 2) {
    registerError.value = 'El nombre debe tener al menos 2 caracteres'
    registerLoading.value = false
    return
  }

  if (!registerLastName.value || registerLastName.value.trim().length < 2) {
    registerError.value = 'El apellido debe tener al menos 2 caracteres'
    registerLoading.value = false
    return
  }
  
  if (registerPassword.value !== registerConfirm.value) {
    registerError.value = 'Las contraseñas no coinciden'
    registerLoading.value = false
    return
  }
  
  if (registerPassword.value.length < 8) {
    registerError.value = 'La contraseña debe tener al menos 8 caracteres'
    registerLoading.value = false
    return
  }
  
  try {
    const response = await makeSecureRequest(`${APIurl}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name: registerName.value.trim(),
        lastName: registerLastName.value.trim(),
        email: registerEmail.value,
        password: registerPassword.value
      })
    })
    
    if (response.ok) {
      const data = await response.json()
      
      // Clear form
      registerName.value = ''
      registerLastName.value = ''
      registerEmail.value = ''
      registerPassword.value = ''
      registerConfirm.value = ''
      
      // Show success message and switch to login
      toast.success(data.message || '¡Registro exitoso! Por favor inicia sesión.')
      activeTab.value = 'login'
      
    } else {
      let errorMessage = 'Error en el registro'
      
      try {
        const errorData = await response.json()
        errorMessage = errorData.message || errorData.error || `Error del servidor: ${response.status}`
      } catch (jsonError) {
        try {
          const errorText = await response.text()
          errorMessage = errorText || `Error del servidor: ${response.status}`
        } catch (textError) {
          errorMessage = `Error del servidor: ${response.status}`
        }
      }
      
      registerError.value = errorMessage
    }
    
  } catch (error) {
    let errorMessage = 'Error en el registro'
    
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      errorMessage = 'Error de conexión - por favor verifica tu conexión'
    } else if (error.message) {
      errorMessage = error.message
    }
    
    registerError.value = errorMessage
  } finally {
    registerLoading.value = false
  }
}
</script>

<style scoped>
/* Custom animations and enhanced styles */

/* Gradient animation for title */
@keyframes gradient-x {
  0%, 100% {
    background-size: 200% 200%;
    background-position: left center;
  }
  50% {
    background-size: 200% 200%;
    background-position: right center;
  }
}

.animate-gradient-x {
  animation: gradient-x 3s ease-in-out infinite;
}

.bg-300\% {
  background-size: 300%;
}

/* Shake animation for error messages */
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-2px); }
  20%, 40%, 60%, 80% { transform: translateX(2px); }
}

.animate-shake {
  animation: shake 0.6s ease-in-out;
}

/* Subtle hover effects instead of scaling */
.hover\:border-l-6:hover {
  border-left-width: 6px;
}

.hover\:decoration-2:hover {
  text-decoration-thickness: 2px;
}

/* Enhanced shadow effects */
.hover\:shadow-3xl:hover {
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

/* Enhanced border utilities */
.border-3 {
  border-width: 3px;
}

/* Custom focus ring sizes */
.focus\:ring-4:focus {
  --tw-ring-offset-shadow: var(--tw-ring-inset) 0 0 0 var(--tw-ring-offset-width) var(--tw-ring-offset-color);
  --tw-ring-shadow: var(--tw-ring-inset) 0 0 0 calc(4px + var(--tw-ring-offset-width)) var(--tw-ring-color);
  box-shadow: var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow, 0 0 #0000);
}

/* Improved group hover effects */
.group:hover .group-hover\:translate-x-1 {
  transform: translateX(0.25rem);
}

.group:hover .group-hover\:opacity-30 {
  opacity: 0.3;
}

.group:hover .group-hover\:opacity-100 {
  opacity: 1;
}

.group:hover .group-hover\:text-gray-700 {
  color: rgb(55 65 81);
}

.group:hover .group-hover\:from-red-600 {
  --tw-gradient-from: rgb(220 38 38);
}

.group:hover .group-hover\:via-red-500 {
  --tw-gradient-via: rgb(239 68 68);
}

.group:hover .group-hover\:to-orange-500 {
  --tw-gradient-to: rgb(249 115 22);
}

.group:hover .group-hover\:brightness-110 {
  filter: brightness(1.1);
}

.group:hover .group-hover\:drop-shadow-2xl {
  filter: drop-shadow(0 25px 25px rgb(0 0 0 / 0.15));
}

/* Animation delays */
.delay-500 {
  animation-delay: 500ms;
}

.delay-1000 {
  animation-delay: 1000ms;
}

/* Enhanced backdrop blur */
.backdrop-blur-xl {
  backdrop-filter: blur(24px);
}
</style>
