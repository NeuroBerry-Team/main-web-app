<template>
    <br>
  <div class="w-full min-h-screen max-w-4xl mx-auto p-3 sm:p-6 lg:p-8 font-sans text-gray-800 bg-gradient-to-br from-slate-50 to-slate-200">
    
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between mb-6 sm:mb-8 gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900">Configuración de Cuenta</h1>
        <p class="text-gray-600 mt-1 sm:mt-2 text-sm sm:text-base">Gestiona tu información personal y configuración de cuenta</p>
      </div>
      <router-link to="/profile" 
                   class="bg-gray-500 hover:bg-gray-600 text-white px-3 sm:px-4 py-2 rounded-lg transition-all duration-200 flex items-center gap-2 hover:scale-105 active:scale-95 text-sm sm:text-base w-fit">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
        </svg>
        <span class="hidden sm:inline">Volver al Perfil</span>
        <span class="sm:hidden">Volver</span>
      </router-link>
    </div>

    <!-- Settings Sections -->
    <div class="space-y-6">
      
      <!-- Personal Information Section -->
      <section class="bg-white rounded-xl sm:rounded-2xl shadow-lg p-4 sm:p-6 hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between mb-4 sm:mb-6 gap-3 sm:gap-0">
          <div class="flex-1">
            <h2 class="text-lg sm:text-xl font-semibold text-gray-900">Información Personal</h2>
            <p class="text-gray-600 text-xs sm:text-sm">Actualiza tu información de perfil</p>
            <div class="mt-2 p-2 bg-green-50 border-l-4 border-green-400 rounded-r-lg">
              <p class="text-xs text-green-700">Los cambios se guardarán y la página se recargará automáticamente.</p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <span class="px-2 sm:px-3 py-1 text-xs font-medium rounded-full"
                  :class="getRoleBadgeClass(user?.role)">
              {{ user?.role || 'Usuario' }}
            </span>
          </div>
        </div>

        <form @submit.prevent="updatePersonalInfo" class="space-y-4 sm:space-y-5">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
            <div class="space-y-2">
              <label for="firstName" class="block text-sm font-medium text-gray-700">
                Nombre *
              </label>
              <input
                id="firstName"
                v-model="personalForm.name"
                type="text"
                required
                :class="[
                  'w-full px-3 py-2 sm:py-3 border rounded-lg transition-all duration-200',
                  'focus:ring-2 focus:ring-red-500 focus:border-transparent',
                  'hover:border-gray-400',
                  personalFormErrors.name ? 'border-red-300 bg-red-50' : 'border-gray-300'
                ]"
                placeholder="Tu nombre"
                @input="clearFieldError('personal', 'name')"
              />
              <p v-if="personalFormErrors.name" class="text-xs text-red-600 animate-pulse">
                {{ personalFormErrors.name }}
              </p>
            </div>
            <div class="space-y-2">
              <label for="lastName" class="block text-sm font-medium text-gray-700">
                Apellido *
              </label>
              <input
                id="lastName"
                v-model="personalForm.lastName"
                type="text"
                required
                :class="[
                  'w-full px-3 py-2 sm:py-3 border rounded-lg transition-all duration-200',
                  'focus:ring-2 focus:ring-red-500 focus:border-transparent',
                  'hover:border-gray-400',
                  personalFormErrors.lastName ? 'border-red-300 bg-red-50' : 'border-gray-300'
                ]"
                placeholder="Tu apellido"
                @input="clearFieldError('personal', 'lastName')"
              />
              <p v-if="personalFormErrors.lastName" class="text-xs text-red-600 animate-pulse">
                {{ personalFormErrors.lastName }}
              </p>
            </div>
          </div>
          
          <div class="space-y-2 sm:col-span-2">
            <label for="email" class="block text-sm font-medium text-gray-700">
              Correo Electrónico *
            </label>
            <input
              id="email"
              v-model="personalForm.email"
              type="email"
              required
              :class="[
                'w-full px-3 py-2 sm:py-3 border rounded-lg transition-all duration-200',
                'focus:ring-2 focus:ring-red-500 focus:border-transparent',
                'hover:border-gray-400',
                personalFormErrors.email ? 'border-red-300 bg-red-50' : 'border-gray-300'
              ]"
              placeholder="tu@email.com"
              @input="clearFieldError('personal', 'email')"
            />
            <p v-if="personalFormErrors.email" class="text-xs text-red-600 animate-pulse">
              {{ personalFormErrors.email }}
            </p>
          </div>

          <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between pt-4 gap-3">
            <div class="text-xs sm:text-sm text-gray-500">
              <span class="text-red-500">*</span> Campos requeridos
            </div>
            <button
              type="submit"
              :disabled="personalFormLoading"
              class="w-full sm:w-auto bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white px-4 sm:px-6 py-2 sm:py-3 rounded-lg transition-all duration-200 flex items-center justify-center gap-2 hover:scale-105 active:scale-95 disabled:hover:scale-100"
            >
              <svg v-if="personalFormLoading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 0 1 4 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
              </svg>
              {{ personalFormLoading ? 'Guardando...' : 'Guardar Cambios' }}
            </button>
          </div>
        </form>
      </section>

      <!-- Password Change Section -->
      <section class="bg-white rounded-xl sm:rounded-2xl shadow-lg p-4 sm:p-6 hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
        <div class="mb-4 sm:mb-6">
          <h2 class="text-lg sm:text-xl font-semibold text-gray-900">Cambiar Contraseña</h2>
          <p class="text-gray-600 text-xs sm:text-sm">Actualiza tu contraseña para mantener tu cuenta segura</p>
          <div class="mt-2 p-3 bg-blue-50 border-l-4 border-blue-400 rounded-r-lg">
            <p class="text-xs sm:text-sm text-blue-700">
              <svg class="w-4 h-4 inline mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
              </svg>
              Después de cambiar tu contraseña, la página se recargará automáticamente.
            </p>
          </div>
        </div>

        <form @submit.prevent="changePassword" class="space-y-4 sm:space-y-5">
          <div class="space-y-2">
            <label for="currentPassword" class="block text-sm font-medium text-gray-700">
              Contraseña Actual *
            </label>
            <input
              id="currentPassword"
              v-model="passwordForm.currentPassword"
              type="password"
              required
              :class="[
                'w-full px-3 py-2 sm:py-3 border rounded-lg transition-all duration-200',
                'focus:ring-2 focus:ring-red-500 focus:border-transparent',
                'hover:border-gray-400',
                passwordFormErrors.currentPassword ? 'border-red-300 bg-red-50' : 'border-gray-300'
              ]"
              placeholder="Tu contraseña actual"
              @input="clearFieldError('password', 'currentPassword')"
            />
            <p v-if="passwordFormErrors.currentPassword" class="text-xs text-red-600 animate-pulse">
              {{ passwordFormErrors.currentPassword }}
            </p>
          </div>
          
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
            <div class="space-y-2">
              <label for="newPassword" class="block text-sm font-medium text-gray-700">
                Nueva Contraseña *
              </label>
              <input
                id="newPassword"
                v-model="passwordForm.newPassword"
                type="password"
                required
                :class="[
                  'w-full px-3 py-2 sm:py-3 border rounded-lg transition-all duration-200',
                  'focus:ring-2 focus:ring-red-500 focus:border-transparent',
                  'hover:border-gray-400',
                  passwordFormErrors.newPassword ? 'border-red-300 bg-red-50' : 'border-gray-300'
                ]"
                placeholder="Nueva contraseña"
                @input="clearFieldError('password', 'newPassword')"
              />
              <p v-if="passwordFormErrors.newPassword" class="text-xs text-red-600 animate-pulse">
                {{ passwordFormErrors.newPassword }}
              </p>
            </div>
            <div class="space-y-2">
              <label for="confirmPassword" class="block text-sm font-medium text-gray-700">
                Confirmar Nueva Contraseña *
              </label>
              <input
                id="confirmPassword"
                v-model="passwordForm.confirmPassword"
                type="password"
                required
                :class="[
                  'w-full px-3 py-2 sm:py-3 border rounded-lg transition-all duration-200',
                  'focus:ring-2 focus:ring-red-500 focus:border-transparent',
                  'hover:border-gray-400',
                  passwordFormErrors.confirmPassword ? 'border-red-300 bg-red-50' : 'border-gray-300'
                ]"
                placeholder="Confirma la nueva contraseña"
                @input="clearFieldError('password', 'confirmPassword')"
              />
              <p v-if="passwordFormErrors.confirmPassword" class="text-xs text-red-600 animate-pulse">
                {{ passwordFormErrors.confirmPassword }}
              </p>
            </div>
          </div>

          <!-- Password Requirements -->
          <div class="bg-gray-50 p-3 sm:p-4 rounded-lg border">
            <h4 class="text-sm font-medium text-gray-700 mb-2">Requisitos de contraseña:</h4>
            <ul class="text-xs sm:text-sm text-gray-600 space-y-1 sm:space-y-2">
              <li class="flex items-center gap-2">
                <svg class="w-3 h-3 sm:w-4 sm:h-4 text-green-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
                Mínimo 8 caracteres
              </li>
              <li class="flex items-center gap-2">
                <svg class="w-3 h-3 sm:w-4 sm:h-4 text-green-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
                Al menos una letra y un número
              </li>
            </ul>
          </div>

          <div class="flex justify-end pt-4">
            <button
              type="submit"
              :disabled="passwordFormLoading"
              class="w-full sm:w-auto bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 sm:px-6 py-2 sm:py-3 rounded-lg transition-all duration-200 flex items-center justify-center gap-2 hover:scale-105 active:scale-95 disabled:hover:scale-100"
            >
              <svg v-if="passwordFormLoading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 0 1 4 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
              </svg>
              {{ passwordFormLoading ? 'Cambiando...' : 'Cambiar Contraseña' }}
            </button>
          </div>
        </form>
      </section>
        
      <br>

      <!-- Account Security Section -->
      <section class="bg-white rounded-2xl shadow-lg p-4 sm:p-6 transition-all duration-200 hover:-translate-y-1 hover:shadow-xl">
        <div class="mb-4 sm:mb-6">
          <h2 class="text-lg sm:text-xl font-semibold text-gray-900">Seguridad de la Cuenta</h2>
          <p class="text-gray-600 text-sm">Gestiona la seguridad y sesiones de tu cuenta</p>
        </div>

        <div class="space-y-4">
          <!-- Account Status -->
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between p-4 bg-green-50 border border-green-200 rounded-lg gap-3 sm:gap-0 transition-all duration-200 hover:bg-green-100">
            <div class="flex items-center gap-3">
              <div class="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
              <div>
                <p class="font-medium text-green-800">Cuenta Activa</p>
                <p class="text-sm text-green-600">Tu cuenta está verificada y activa</p>
              </div>
            </div>
            <span class="text-xs text-green-600 font-medium bg-green-200 px-2 py-1 rounded-full w-fit">VERIFICADO</span>
          </div>

          <!-- Session Management -->
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between p-4 border border-gray-200 rounded-lg gap-3 sm:gap-0 transition-all duration-200 hover:bg-gray-50">
            <div class="flex-1">
              <p class="font-medium text-gray-900">Cerrar Otras Sesiones</p>
              <p class="text-sm text-gray-600">Cierra todas las sesiones activas en otros dispositivos</p>
            </div>
            <button
              @click="logoutAllSessions"
              :disabled="sessionLoading"
              class="w-full sm:w-auto bg-orange-600 hover:bg-orange-700 disabled:bg-gray-400 text-white px-4 py-2 sm:py-3 rounded-lg transition-all duration-200 text-sm flex items-center justify-center gap-2 hover:scale-105 active:scale-95 disabled:hover:scale-100"
            >
              <svg v-if="sessionLoading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 0 1 4 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
              </svg>
              {{ sessionLoading ? 'Cerrando...' : 'Cerrar Sesiones' }}
            </button>
          </div>
        </div>
      </section>

      <br>

      <!-- Danger Zone -->
      <section class="bg-white border-2 border-red-200 hover:border-red-300 rounded-2xl shadow-lg p-4 sm:p-6 transition-all duration-200 hover:-translate-y-1 hover:shadow-xl">
        <div class="mb-4 sm:mb-6">
          <h2 class="text-lg sm:text-xl font-semibold text-red-900">Zona de Peligro</h2>
          <p class="text-red-600 text-sm">Acciones irreversibles que afectan tu cuenta</p>
        </div>

        <div class="space-y-4">
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between p-4 bg-red-50 border border-red-200 rounded-lg gap-3 sm:gap-0 transition-all duration-200 hover:bg-red-100">
            <div class="flex-1">
              <p class="font-medium text-red-900">Eliminar Cuenta</p>
              <p class="text-sm text-red-600">Esta acción eliminará permanentemente tu cuenta y todos tus datos</p>
            </div>
            <button
              @click="showDeleteConfirmation = true"
              class="w-full sm:w-auto bg-red-600 hover:bg-red-700 text-white px-4 py-2 sm:py-3 rounded-lg transition-all duration-200 text-sm flex items-center justify-center gap-2 hover:scale-105 active:scale-95 font-medium"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
              </svg>
              Eliminar Cuenta
            </button>
          </div>
        </div>
      </section>
    </div>

    <!-- Delete Confirmation Modal -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div v-if="showDeleteConfirmation" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Transition
            enter-active-class="transition-all duration-300 ease-out delay-100"
            enter-from-class="opacity-0 scale-95 translate-y-4"
            enter-to-class="opacity-100 scale-100 translate-y-0"
            leave-active-class="transition-all duration-200 ease-in"
            leave-from-class="opacity-100 scale-100 translate-y-0"
            leave-to-class="opacity-0 scale-95 translate-y-4"
          >
            <div v-if="showDeleteConfirmation" class="bg-white rounded-2xl shadow-xl max-w-md w-full p-4 sm:p-6">
              <div class="text-center">
                <div class="mx-auto flex items-center justify-center w-12 h-12 rounded-full bg-red-100 mb-4">
                  <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"/>
                  </svg>
                </div>
                <h3 class="text-lg font-semibold text-gray-900 mb-2">¿Estás seguro?</h3>
                <p class="text-gray-600 mb-6 text-sm sm:text-base">
                  Esta acción eliminará permanentemente tu cuenta y todos los datos asociados. 
                  No podrás recuperar esta información.
                </p>
                <div class="flex flex-col sm:flex-row gap-3 justify-center">
                  <button
                    @click="showDeleteConfirmation = false"
                    class="order-2 sm:order-1 w-full sm:w-auto px-4 py-2 sm:py-3 bg-gray-500 hover:bg-gray-600 text-white rounded-lg transition-all duration-200 hover:scale-105 active:scale-95"
                  >
                    Cancelar
                  </button>
                  <button
                    @click="deleteAccount"
                    :disabled="deleteLoading"
                    class="order-1 sm:order-2 w-full sm:w-auto px-4 py-2 sm:py-3 bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white rounded-lg transition-all duration-200 flex items-center justify-center gap-2 hover:scale-105 active:scale-95 disabled:hover:scale-100"
                  >
                    <svg v-if="deleteLoading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 0 1 4 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                    </svg>
                    {{ deleteLoading ? 'Eliminando...' : 'Sí, Eliminar' }}
                  </button>
                </div>
              </div>
            </div>
          </Transition>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/use_auth.js'
import { useCSRF } from '@/composables/use_csrf.js'
import { useToast } from "vue-toastification"

// Composables
const router = useRouter()
const { user, checkAuthStatus } = useAuth()
const { makeSecureRequest } = useCSRF()
const toast = useToast()

// API URL
const apiUrl = import.meta.env.VITE_API_BASE_URL

// Reactive state
const personalForm = reactive({
  name: '',
  lastName: '',
  email: ''
})

const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// Loading states
const personalFormLoading = ref(false)
const passwordFormLoading = ref(false)
const sessionLoading = ref(false)
const deleteLoading = ref(false)

// Error states
const personalFormErrors = reactive({
  name: '',
  lastName: '',
  email: ''
})

const passwordFormErrors = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// UI state
const showDeleteConfirmation = ref(false)

// Initialize form data when user data is available
onMounted(async () => {
  await checkAuthStatus()
  if (user.value) {
    personalForm.name = user.value.name || ''
    personalForm.lastName = user.value.lastName || ''
    personalForm.email = user.value.email || ''
  }
})

// Computed
const getRoleBadgeClass = (role) => {
  switch(role) {
    case 'SUPERADMIN':
      return 'bg-purple-100 text-purple-800 border border-purple-200'
    case 'ADMIN':
      return 'bg-blue-100 text-blue-800 border border-blue-200'
    case 'AI_USER':
      return 'bg-green-100 text-green-800 border border-green-200'
    default:
      return 'bg-gray-100 text-gray-800 border border-gray-200'
  }
}

// Methods


const clearPersonalErrors = () => {
  personalFormErrors.name = ''
  personalFormErrors.lastName = ''
  personalFormErrors.email = ''
}

const clearPasswordErrors = () => {
  passwordFormErrors.currentPassword = ''
  passwordFormErrors.newPassword = ''
  passwordFormErrors.confirmPassword = ''
}

// Clear individual field errors on input
const clearFieldError = (formType, field) => {
  if (formType === 'personal') {
    personalFormErrors[field] = ''
  } else if (formType === 'password') {
    passwordFormErrors[field] = ''
  }
}

const validatePersonalForm = () => {
  clearPersonalErrors()
  let isValid = true
  
  if (!personalForm.name.trim()) {
    personalFormErrors.name = 'El nombre es requerido'
    isValid = false
  }
  if (!personalForm.lastName.trim()) {
    personalFormErrors.lastName = 'El apellido es requerido'
    isValid = false
  }
  if (!personalForm.email.trim()) {
    personalFormErrors.email = 'El email es requerido'
    isValid = false
  } else {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(personalForm.email)) {
      personalFormErrors.email = 'Ingresa un email válido'
      isValid = false
    }
  }
  
  return isValid
}

const validatePasswordForm = () => {
  clearPasswordErrors()
  let isValid = true
  
  if (!passwordForm.currentPassword) {
    passwordFormErrors.currentPassword = 'La contraseña actual es requerida'
    isValid = false
  }
  
  if (!passwordForm.newPassword) {
    passwordFormErrors.newPassword = 'La nueva contraseña es requerida'
    isValid = false
  } else {
    if (passwordForm.newPassword.length < 8) {
      passwordFormErrors.newPassword = 'La nueva contraseña debe tener al menos 8 caracteres'
      isValid = false
    }
  }
  
  if (!passwordForm.confirmPassword) {
    passwordFormErrors.confirmPassword = 'Confirma tu nueva contraseña'
    isValid = false
  } else if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    passwordFormErrors.confirmPassword = 'Las contraseñas no coinciden'
    isValid = false
  }
  
  return isValid
}

const updatePersonalInfo = async () => {
  if (!validatePersonalForm()) return
  
  personalFormLoading.value = true
  
  try {
    const response = await makeSecureRequest(`${apiUrl}/users/update-profile`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name: personalForm.name.trim(),
        lastName: personalForm.lastName.trim(),
        email: personalForm.email.trim()
      })
    })
    
    if (response.ok) {
      // Update local user data
      if (user.value) {
        user.value.name = personalForm.name.trim()
        user.value.lastName = personalForm.lastName.trim()
        user.value.email = personalForm.email.trim()
      }
      clearPersonalErrors()
      toast.success('Información actualizada correctamente. La página se recargará en unos segundos...')
      
      // Reload page after short delay to show success message and refresh data
      setTimeout(() => {
        window.location.reload()
      }, 2000)
    } else {
      const errorData = await response.json()
      
      // Handle validation errors from server
      if (errorData.errors) {
        if (errorData.errors.name) personalFormErrors.name = errorData.errors.name
        if (errorData.errors.lastName) personalFormErrors.lastName = errorData.errors.lastName
        if (errorData.errors.email) personalFormErrors.email = errorData.errors.email
      }
      
      toast.error(errorData.message || 'No se pudo actualizar la información. Verifica los datos e intenta nuevamente.')
    }
  } catch (error) {
    console.error('Error updating personal info:', error)
    toast.error('Error de conexión. Verifica tu conexión a internet e intenta nuevamente.')
  } finally {
    personalFormLoading.value = false
  }
}

const changePassword = async () => {
  if (!validatePasswordForm()) return
  
  passwordFormLoading.value = true
  
  try {
    const response = await makeSecureRequest(`${apiUrl}/users/change-password`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        currentPassword: passwordForm.currentPassword,
        newPassword: passwordForm.newPassword
      })
    })
    
    if (response.ok) {
      toast.success('Contraseña cambiada correctamente. La página se recargará en unos segundos...')
      
      // Clear password form and errors
      passwordForm.currentPassword = ''
      passwordForm.newPassword = ''
      passwordForm.confirmPassword = ''
      clearPasswordErrors()
      
      // Reload page after short delay to show success message
      setTimeout(() => {
        window.location.reload()
      }, 2000)
    } else {
      const errorData = await response.json()
      
      // Handle validation errors from server
      if (errorData.errors) {
        if (errorData.errors.currentPassword) passwordFormErrors.currentPassword = errorData.errors.currentPassword
        if (errorData.errors.newPassword) passwordFormErrors.newPassword = errorData.errors.newPassword
        if (errorData.errors.confirmPassword) passwordFormErrors.confirmPassword = errorData.errors.confirmPassword
      }
      
      toast.error(errorData.message || 'No se pudo cambiar la contraseña. Verifica que la contraseña actual sea correcta.')
    }
  } catch (error) {
    console.error('Error changing password:', error)
    toast.error('Error de conexión. Verifica tu conexión a internet e intenta nuevamente.')
  } finally {
    passwordFormLoading.value = false
  }
}

const logoutAllSessions = async () => {
  sessionLoading.value = true
  
  try {
    const response = await makeSecureRequest(`${apiUrl}/auth/logout-all-sessions`, {
      method: 'POST'
    })
    
    if (response.ok) {
      toast.success('Todas las sesiones han sido cerradas correctamente. Serás redirigido al login...')
      
      // Redirect to login after closing all sessions
      setTimeout(() => {
        router.push('/login')
      }, 2000)
    } else {
      toast.error('No se pudieron cerrar todas las sesiones. Intenta nuevamente.')
    }
  } catch (error) {
    console.error('Error logging out sessions:', error)
    toast.error('Error de conexión. Verifica tu conexión a internet e intenta nuevamente.')
  } finally {
    sessionLoading.value = false
  }
}

const deleteAccount = async () => {
  deleteLoading.value = true
  
  try {
    const response = await makeSecureRequest(`${apiUrl}/users/delete-account`, {
      method: 'DELETE'
    })
    
    if (response.ok) {
      toast.success('Tu cuenta ha sido eliminada permanentemente. Serás redirigido al inicio...')
      
      // Clear user session and redirect to home
      setTimeout(() => {
        // Clear any auth tokens/session data
        localStorage.clear()
        sessionStorage.clear()
        router.push('/')
      }, 2500)
    } else {
      const errorData = await response.json()
      toast.error(errorData.message || 'No se pudo eliminar la cuenta. Intenta nuevamente más tarde.')
    }
  } catch (error) {
    console.error('Error deleting account:', error)
    toast.error('Error de conexión. Verifica tu conexión a internet e intenta nuevamente.')
  } finally {
    deleteLoading.value = false
    showDeleteConfirmation.value = false
  }
}
</script>

<style scoped>
/* Modal transition */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

/* Custom focus styles */
input:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

/* Loading button animation */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* Custom scrollbar for better UX */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .grid-cols-1.md\\:grid-cols-2 {
    grid-template-columns: 1fr;
  }
}
</style>