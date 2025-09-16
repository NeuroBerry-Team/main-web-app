<template>
  <!-- Gallery Modal -->
  <Teleport to="body" v-if="!selectedInference">
    <div class="modal-overlay" @click.self="goBack">
      <div class="modal-container" @click.stop>
        <div class="bg-gradient-to-r from-red-600 via-red-700 to-red-800 text-white p-6 flex items-center justify-between relative overflow-hidden">
          <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent transform -skew-x-12"></div>
          
          <div class="relative z-10 flex items-center space-x-3">
            <div class="text-2xl">📊</div>
            <h2 class="text-2xl font-bold">Galería de Análisis</h2>
          </div>
          
          <div class="relative z-10 flex items-center space-x-3">
            <router-link 
              to="/AI/inference"
              class="px-4 py-2 bg-white/20 text-white rounded-lg hover:bg-white/30 transition-colors duration-200 text-sm"
            >
              Nuevo análisis
            </router-link>
            <button 
              @click="goBack" 
              class="text-white hover:text-red-200 text-3xl font-light w-10 h-10 flex items-center justify-center rounded-full hover:bg-white hover:bg-opacity-20 transition-all duration-200 hover:rotate-90 transform"
              title="Cerrar ventana (ESC)"
            >
              ×
            </button>
          </div>
        </div>

        <div class="flex-1 p-8 overflow-y-auto bg-gray-50">
          <!-- Gallery Content -->
          <div class="space-y-6">
            <div v-if="loading" class="text-center py-12">
              <div class="text-4xl mb-4">⏳</div>
              <p class="text-gray-500">Cargando galería...</p>
            </div>
            
            <div v-else-if="error" class="text-center py-12">
              <div class="text-4xl mb-4">❌</div>
              <p class="text-red-500 mb-4">Error al cargar los análisis</p>
              <button 
                @click="loadInferences"
                class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors duration-200"
              >
                Intentar de nuevo
              </button>
            </div>
            
            <div v-else-if="!inferences.length" class="text-center py-12">
              <div class="text-6xl mb-6">📊</div>
              <h3 class="text-xl font-semibold text-gray-700 mb-2">No tienes análisis aún</h3>
              <p class="text-gray-500 mb-6">Comienza analizando tu primera imagen de frambuesa</p>
              <router-link 
                to="/AI/inference"
                class="inline-flex items-center px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors duration-200"
              >
                Crear primer análisis
                <span class="ml-2">→</span>
              </router-link>
            </div>
            
            <!-- Gallery Grid -->
            <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
              <div
                v-for="inference in inferencesWithConfidence"
                :key="inference.id"
                @click="() => openInferenceDetail(inference)"
                :class="['gallery-item group cursor-pointer bg-white rounded-xl shadow-md overflow-hidden transition-all duration-200', 
                         openingInference ? 'opacity-75 pointer-events-none' : 'hover:shadow-lg']"
              >
                <!-- Loading overlay for when opening inference -->
                <div v-if="openingInference" class="absolute inset-0 bg-black bg-opacity-20 flex items-center justify-center z-10 rounded-xl">
                  <div class="text-white text-sm bg-black bg-opacity-50 px-3 py-1 rounded-full">
                    Cargando...
                  </div>
                </div>
                
                <!-- Image Thumbnail -->
                <div class="aspect-square bg-gray-100 relative overflow-hidden">
                  <img 
                    v-if="inference.baseImageUrl"
                    :src="getCachedImageUrl(inference.baseImageUrl)"
                    :alt="inference.result"
                    class="w-full h-full object-cover transition-opacity duration-300"
                    @error="handleImageError"
                    @load="onImageLoad(inference)"
                    loading="lazy"
                    decoding="async"
                  />
                  
                  <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                    <span class="text-3xl">🍓</span>
                  </div>
                  
                  <!-- Overlay with confidence -->
                  <div v-if="inference.confidence" class="absolute top-2 right-2 bg-black bg-opacity-60 text-white text-xs px-2 py-1 rounded-full">
                    {{ Math.round(inference.confidence * 100) }}%
                  </div>
                  
                  <!-- Analysis result overlay -->
                  <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-3">
                    <p class="text-white text-sm font-medium truncate">{{ inference.result }}</p>
                  </div>
                </div>
                
                <!-- Info Section -->
                <div class="p-3">
                  <div class="flex justify-between items-center text-xs text-gray-500">
                    <span>{{ formatActivityTime(inference.createdOn) }}</span>
                    <span class="font-mono">#{{ inference.id }}</span>
                  </div>
                  <div class="text-xs text-gray-400 mt-1">
                    {{ formatTime(inference.createdOn) }}
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Load More Button -->
            <div v-if="hasMore && !loading" class="text-center mt-8">
              <button
                @click="loadMoreInferences"
                class="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors duration-200"
              >
                Cargar más análisis
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>

  <!-- Individual Inference Detail Modal -->
  <Teleport to="body" v-if="selectedInference">
    <div class="modal-overlay" @click.self="closeInferenceDetail">
      <div class="modal-container" style="max-width: 80rem;" @click.stop>
        <div class="bg-gradient-to-r from-purple-500 to-pink-500 p-6 flex items-center justify-between relative overflow-hidden">
          <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent transform -skew-x-12"></div>
          
          <div class="relative z-10 flex items-center space-x-3">
            <div class="text-2xl">🔍</div>
            <div>
              <h2 class="text-2xl font-bold text-white">Detalle del Análisis</h2>
              <p class="text-purple-100 mt-1">Información completa del análisis realizado</p>
            </div>
          </div>
          
          <div class="relative z-10 flex items-center space-x-3">
            <button
              @click="backToGallery"
              class="px-4 py-2 bg-white/20 text-white rounded-lg hover:bg-white/30 transition-colors duration-200 text-sm"
            >
              ← Volver a la galería
            </button>
            <button 
              @click="closeInferenceDetail"
              class="text-white hover:text-purple-200 text-3xl font-light w-10 h-10 flex items-center justify-center rounded-full hover:bg-white hover:bg-opacity-20 transition-all duration-200 hover:rotate-90 transform"
              title="Cerrar ventana (ESC)"
            >
              ×
            </button>
          </div>
        </div>
        
        <div class="flex-1 p-6 overflow-y-auto bg-gray-50">
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <!-- Images Section -->
            <div class="space-y-4">
              <div>
                <h3 class="text-lg font-semibold text-gray-700 mb-3">Imagen Original</h3>
                <div class="relative">
                  <img 
                    v-if="selectedInference.baseImageUrl"
                    :src="selectedInference.baseImageUrl"
                    :alt="selectedInference.name || 'Imagen original'"
                    class="w-full h-64 object-contain rounded-lg transition-all duration-300 bg-gray-50"
                    @error="handleImageError"
                    loading="lazy"
                  />
                  <div v-else class="w-full h-64 flex items-center justify-center text-gray-500 bg-gray-50 rounded-lg">
                    <span>Imagen no disponible</span>
                  </div>
                </div>
              </div>
              
              <div>
                <div class="flex items-center justify-between mb-3">
                  <h3 class="text-lg font-semibold text-gray-700">Resultado del Análisis</h3>
                  
                  <!-- Box Controls Toggle -->
                  <button
                    @click="toggleBoxControls"
                    :class="['flex items-center space-x-2 px-3 py-2 rounded-lg transition-all duration-200 text-sm', 
                             showBoxControls ? 'bg-purple-100 text-purple-700 border border-purple-300' : 'bg-gray-100 text-gray-600 hover:bg-gray-200']"
                  >
                    <span>{{ showBoxControls ? '🔧' : '📦' }}</span>
                    <span>{{ showBoxControls ? 'Ocultar controles' : 'Gestionar cajas' }}</span>
                  </button>
                </div>
                
                <!-- Box Controls Panel (Collapsible) -->
                <div v-if="showBoxControls" class="mb-4 bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
                  <div class="flex items-center justify-between mb-3">
                    <h4 class="text-sm font-medium text-gray-700">Control de Detecciones</h4>
                    <div class="flex items-center space-x-2 text-xs text-gray-500">
                      <button
                        @click="toggleAllBoxes(true)"
                        class="px-2 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200 transition-colors"
                      >
                        Mostrar todas
                      </button>
                      <button
                        @click="toggleAllBoxes(false)"
                        class="px-2 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                      >
                        Ocultar todas
                      </button>
                    </div>
                  </div>
                  
                  <!-- Individual Box Controls -->
                  <div class="space-y-2 max-h-32 overflow-y-auto">
                    <div
                      v-for="(box, index) in detectedBoxes"
                      :key="`box-${index}`"
                      :class="[
                        'flex items-center justify-between py-2 px-3 rounded-lg transition-all duration-200 cursor-pointer',
                        selectedBox === box 
                          ? 'bg-purple-100 border-2 border-purple-300 ring-1 ring-purple-200' 
                          : 'bg-gray-50 hover:bg-gray-100 border-2 border-transparent'
                      ]"
                      @click="selectBox(box)"
                    >
                      <div class="flex items-center space-x-3">
                        <!-- Color indicator -->
                        <div 
                          :class="[
                            'w-3 h-3 rounded-full border transition-all duration-200',
                            selectedBox === box 
                              ? 'border-purple-400 ring-2 ring-purple-200' 
                              : 'border-gray-300'
                          ]"
                          :style="{ backgroundColor: box.color }"
                        ></div>
                        
                        <!-- Box info -->
                        <div>
                          <span 
                            :class="[
                              'text-sm font-medium transition-colors duration-200',
                              selectedBox === box ? 'text-purple-800' : 'text-gray-700'
                            ]"
                          >
                            {{ box.label }}
                          </span>
                          <span 
                            :class="[
                              'text-xs ml-2 transition-colors duration-200',
                              selectedBox === box ? 'text-purple-600' : 'text-gray-500'
                            ]"
                          >
                            {{ Math.round(box.confidence * 100) }}%
                          </span>
                        </div>
                      </div>
                      
                      <!-- Toggle switch -->
                      <label class="relative inline-flex items-center cursor-pointer" @click.stop>
                        <input 
                          type="checkbox" 
                          v-model="box.visible" 
                          class="sr-only peer"
                          @change="updateImageWithBoxes"
                        >
                        <div class="w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-purple-500"></div>
                      </label>
                    </div>
                  </div>
                  
                  <!-- Magnifying glass controls -->
                  <div v-if="detectedBoxes.length > 0" class="mt-4 pt-4 border-t border-gray-200">
                    <div class="flex items-center justify-between mb-3">
                      <h5 class="text-sm font-medium text-gray-700">Lupa de Precisión</h5>
                      <button
                        @click="toggleMagnifyingGlass"
                        :class="[
                          'flex items-center space-x-2 px-3 py-2 rounded-lg transition-all duration-200 text-sm',
                          magnifyingGlassActive 
                            ? 'bg-purple-100 text-purple-700 border border-purple-300' 
                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                        ]"
                      >
                        <span>{{ magnifyingGlassActive ? '🔍' : '🔍' }}</span>
                        <span>{{ magnifyingGlassActive ? 'Desactivar' : 'Activar' }}</span>
                      </button>
                    </div>
                    
                    <!-- Zoom and size controls when magnifying glass is active -->
                    <div v-if="magnifyingGlassActive" class="space-y-3">
                      <!-- Zoom controls -->
                      <div class="flex items-center justify-between">
                        <span class="text-xs text-gray-600">Zoom:</span>
                        <div class="flex gap-2">
                          <button 
                            @click="magnifyingGlassZoom = Math.max(1.0, magnifyingGlassZoom - 0.1)"
                            class="px-2 py-1 bg-gray-600 text-white text-xs font-bold rounded hover:bg-gray-700 transition-all duration-300"
                            :disabled="magnifyingGlassZoom <= 1.0"
                          >
                            🔍-
                          </button>
                          <span class="px-2 py-1 bg-gray-100 text-gray-800 text-xs font-medium rounded flex items-center min-w-[50px] justify-center">
                            {{ magnifyingGlassZoom.toFixed(1) }}x
                          </span>
                          <button 
                            @click="magnifyingGlassZoom = Math.min(5.0, magnifyingGlassZoom + 0.1)"
                            class="px-2 py-1 bg-gray-600 text-white text-xs font-bold rounded hover:bg-gray-700 transition-all duration-300"
                            :disabled="magnifyingGlassZoom >= 5.0"
                          >
                            🔍+
                          </button>
                        </div>
                      </div>
                      
                      <!-- Size controls -->
                      <div class="flex items-center justify-between">
                        <span class="text-xs text-gray-600">Tamaño:</span>
                        <div class="flex gap-2">
                          <button 
                            @click="magnifyingGlassRadius = Math.max(30, magnifyingGlassRadius - 10)"
                            class="px-2 py-1 bg-indigo-600 text-white text-xs font-bold rounded hover:bg-indigo-700 transition-all duration-300"
                            :disabled="magnifyingGlassRadius <= 30"
                          >
                            ◯-
                          </button>
                          <span class="px-2 py-1 bg-gray-100 text-gray-800 text-xs font-medium rounded flex items-center min-w-[50px] justify-center">
                            {{ Math.round(adaptiveMagnifyingGlassRadius) }}px
                          </span>
                          <button 
                            @click="magnifyingGlassRadius = Math.min(80, magnifyingGlassRadius + 10)"
                            class="px-2 py-1 bg-indigo-600 text-white text-xs font-bold rounded hover:bg-indigo-700 transition-all duration-300"
                            :disabled="magnifyingGlassRadius >= 80"
                          >
                            ◯+
                          </button>
                        </div>
                      </div>
                      
                      <!-- Help text -->
                      <p class="text-xs text-purple-600 text-center">
                        Mueve el mouse sobre la imagen para usar la lupa
                      </p>
                    </div>
                  </div>
                </div>
                
                <div class="bg-gray-100 rounded-lg p-4 relative">
                  <div class="relative">
                    <!-- Hidden image for canvas processing -->
                    <img 
                      v-if="selectedInference.generatedImageUrl"
                      ref="hiddenImage"
                      :src="currentResultImage"
                      :alt="showBoxControls ? 'Imagen original para control manual' : 'Análisis: ' + selectedInference.result"
                      class="hidden"
                      @load="onImageLoad"
                      @error="handleImageError"
                    />
                    
                    <!-- Canvas for drawing boxes -->
                    <canvas 
                      v-if="selectedInference.generatedImageUrl && showBoxControls"
                      ref="imageCanvas"
                      class="w-full max-h-[600px] mx-auto rounded-lg border border-gray-200 bg-gray-50 object-contain"
                      :class="{ 
                        'cursor-crosshair': !magnifyingGlassActive, 
                        'cursor-none': magnifyingGlassActive 
                      }"
                      @click="handleCanvasClick"
                      @dblclick="handleCanvasDoubleClick"
                      @mousemove="handleCanvasMouseMove"
                      @mouseleave="handleCanvasMouseLeave"
                    ></canvas>
                    
                    <!-- Regular image when not in box control mode -->
                    <img 
                      v-else-if="selectedInference.generatedImageUrl"
                      :src="currentResultImage"
                      :alt="'Análisis: ' + selectedInference.result"
                      class="w-full max-h-[600px] mx-auto rounded-lg object-contain bg-gray-50"
                      @error="handleImageError"
                    />
                    
                    <div v-else class="w-full h-64 flex items-center justify-center text-gray-500">
                      <span>Resultado no disponible</span>
                    </div>
                    
                    <!-- Image mode indicator -->
                    <div 
                      v-if="showBoxControls" 
                      class="absolute top-2 left-2 bg-blue-500 text-white text-xs px-2 py-1 rounded-full shadow-sm"
                    >
                      📐 Modo edición
                    </div>
                    
                    <!-- Box count indicator -->
                    <div 
                      v-if="showBoxControls && detectedBoxes.length > 0"
                      class="absolute top-2 right-2 bg-green-500 text-white text-xs px-2 py-1 rounded-full shadow-sm"
                    >
                      {{ detectedBoxes.filter(box => box.visible).length }}/{{ detectedBoxes.length }} cajas
                    </div>
                    
                    <!-- Selected box indicator -->
                    <div 
                      v-if="showBoxControls && selectedBox"
                      class="absolute bottom-2 left-2 bg-purple-600 text-white text-xs px-3 py-1 rounded-full shadow-sm flex items-center space-x-1"
                    >
                      <div 
                        class="w-2 h-2 rounded-full"
                        :style="{ backgroundColor: selectedBox.color }"
                      ></div>
                      <span>{{ selectedBox.label }} seleccionado</span>
                    </div>
                    
                    <!-- Instructions -->
                    <div 
                      v-if="showBoxControls && detectedBoxes.length > 0 && !magnifyingGlassActive"
                      class="absolute top-2 left-2 bg-black bg-opacity-70 text-white text-xs px-2 py-1 rounded shadow-sm"
                    >
                      Click: seleccionar • Doble-click: mostrar/ocultar
                    </div>
                    
                    <!-- Loading overlay -->
                    <div v-if="imageLoading" class="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center rounded-lg">
                      <div class="text-white text-center">
                        <div class="animate-spin text-2xl mb-2">⚙️</div>
                        <p class="text-sm">Actualizando vista...</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Details Section -->
            <div class="space-y-6">
              <div>
                <h3 class="text-lg font-semibold text-gray-700 mb-3">Información del Análisis</h3>
                <div class="space-y-4">
                  <div class="flex justify-between items-center py-2 border-b border-gray-200">
                    <span class="text-gray-600">ID del Análisis</span>
                    <span class="font-mono text-sm text-gray-800">#{{ selectedInference.id }}</span>
                  </div>
                  <div class="flex justify-between items-center py-2 border-b border-gray-200">
                    <span class="text-gray-600">Resultado</span>
                    <span class="font-semibold text-gray-800">{{ selectedInference.result }}</span>
                  </div>
                  <div class="flex justify-between items-center py-2 border-b border-gray-200">
                    <span class="text-gray-600">Fecha de Análisis</span>
                    <span class="text-gray-800">{{ formatDate(selectedInference.createdOn) }}</span>
                  </div>
                  <div class="flex justify-between items-center py-2 border-b border-gray-200">
                    <span class="text-gray-600">Hora</span>
                    <span class="text-gray-800">{{ formatTime(selectedInference.createdOn) }}</span>
                  </div>
                  <div v-if="getCachedConfidence(selectedInference.id)" class="flex justify-between items-center py-2 border-b border-gray-200">
                    <span class="text-gray-600">Confianza Promedio</span>
                    <span class="font-semibold text-green-600">{{ Math.round(getCachedConfidence(selectedInference.id) * 100) }}%</span>
                  </div>
                  <div v-if="selectedInference.name" class="flex justify-between items-center py-2 border-b border-gray-200">
                    <span class="text-gray-600">Nombre</span>
                    <span class="text-gray-800">{{ selectedInference.name }}</span>
                  </div>
                  <!-- Class Count Section -->
                  <div v-if="selectedInference" class="py-2 border-b border-gray-200">
                    <div class="flex flex-col space-y-2">
                      <span class="text-gray-600">Conteo por Clase:</span>
                      
                      <!-- Loading state -->
                      <div v-if="!isMetadataLoaded(selectedInference.id)" class="pl-4 flex items-center space-x-2 text-sm text-gray-500">
                        <div class="animate-spin text-xs">⚙️</div>
                        <span>Calculando conteos...</span>
                      </div>
                      
                      <!-- Class counts -->
                      <div v-else-if="classCountSummary && Object.keys(classCountSummary).length > 0" class="pl-4 grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
                        <div v-for="(count, className) in classCountSummary" :key="className" 
                            class="flex justify-between bg-gray-50 px-3 py-1 rounded">
                          <span class="text-gray-700">{{ className }}:</span>
                          <span class="font-medium text-gray-900">{{ count }}</span>
                        </div>
                      </div>
                      
                      <!-- Show all classes with 0 count when no detections -->
                      <div v-else class="pl-4 grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
                        <div v-for="(label, classId) in getAllClassLabels()" :key="classId" 
                            class="flex justify-between bg-gray-50 px-3 py-1 rounded">
                          <span class="text-gray-700">{{ label }}:</span>
                          <span class="font-medium text-gray-900">0</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <!-- Model Information Section -->
                  <div class="py-2 border-b border-gray-200">
                    <div class="flex justify-between items-center">
                      <span class="text-gray-600">Modelo</span>
                      <div class="flex items-center space-x-2">
                        <span class="text-gray-800">
                          {{ selectedInference.modelId ? `#${selectedInference.modelId}` : (selectedInference.model || 'N/A') }}
                        </span>
                        <button
                          @click="toggleModelDetails"
                          :class="[
                            'text-xs px-2 py-1 rounded transition-colors duration-200',
                            showModelDetails ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                          ]"
                          :disabled="!selectedInference.modelId"
                        >
                          {{ showModelDetails ? 'Ocultar' : 'Detalles' }}
                        </button>
                      </div>
                    </div>
                    
                    <!-- Expanded Model Details -->
                    <div v-if="showModelDetails" class="mt-3 pl-4 border-l-2 border-blue-200 bg-blue-50 rounded-r-lg p-3">
                      <div v-if="getModelDetails(selectedInference.modelId)" class="space-y-2 text-sm">
                        <div class="flex justify-between">
                          <span class="text-blue-600 font-medium">Nombre:</span>
                          <span class="text-blue-800">{{ getModelDetails(selectedInference.modelId).name }}</span>
                        </div>
                        <div class="flex justify-between">
                          <span class="text-blue-600 font-medium">Versión:</span>
                          <span class="text-blue-800">{{ getModelDetails(selectedInference.modelId).version }}</span>
                        </div>
                        <div class="flex justify-between">
                          <span class="text-blue-600 font-medium">Tipo:</span>
                          <span class="text-blue-800">{{ getModelDetails(selectedInference.modelId).modelType }}</span>
                        </div>
                        <div v-if="getModelDetails(selectedInference.modelId).description" class="pt-2 border-t border-blue-200">
                          <span class="text-blue-600 font-medium">Descripción:</span>
                          <p class="text-blue-800 mt-1 text-xs leading-relaxed">{{ getModelDetails(selectedInference.modelId).description }}</p>
                        </div>
                        <div class="flex justify-between text-xs text-blue-500 pt-2 border-t border-blue-200">
                          <span>Creado:</span>
                          <span>{{ formatDate(getModelDetails(selectedInference.modelId).createdOn) }}</span>
                        </div>
                      </div>
                      
                      <!-- Loading state -->
                      <div v-else-if="selectedInference.modelId" class="flex items-center justify-center py-4">
                        <div class="animate-spin text-blue-500 mr-2">⚙️</div>
                        <span class="text-blue-600 text-sm">Cargando detalles del modelo...</span>
                      </div>
                      
                      <!-- No model ID available -->
                      <div v-else class="text-blue-600 text-sm py-2">
                        <span>ℹ️ ID del modelo no disponible</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="pt-4">
                <button
                  @click="downloadResults"
                  class="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200"
                >
                  Descargar Resultados
                </button>
              </div>

              <div class="pt-4">
                <button @click="deleteInference"
                  class="w-full px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors duration-200">
                  Eliminar Análisis
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useMinioMetadata } from '../../composables/use_minio_metadata.js'
import { useCSRF } from '../../composables/use_csrf.js'

const router = useRouter()
const route = useRoute()

const { makeSecureRequest } = useCSRF()

// Minio metadata composable
const {
  detectedBoxes,
  classCountSummary,
  fetchMetadata,
  getCachedConfidence,
  isMetadataLoaded,
  clearMetadata,
  getClassLabel,
  getAllClassLabels,
  getBoxColor,
  normalizeCoordinates
} = useMinioMetadata()

const inferences = ref([])
const selectedInference = ref(null)
const loading = ref(true)
const error = ref(null)
const hasMore = ref(false)
const currentPage = ref(1)

// Box controls variables
const showBoxControls = ref(false)
const imageLoading = ref(false)
const selectedBox = ref(null) // Track which box is currently selected/highlighted

// Magnifying glass controls
const magnifyingGlassActive = ref(false)
const magnifyingGlassRadius = ref(50) // Smaller default radius
const magnifyingGlassPosition = ref({ x: 0, y: 0 })
const magnifyingGlassZoom = ref(1.0) // Zoom factor
const magnifyingGlassBoxes = ref([]) // Boxes within magnifying glass area

// Computed magnifying glass radius based on image size and zoom
const adaptiveMagnifyingGlassRadius = computed(() => {
  if (!canvasImageBounds.value || !imageCanvas.value) {
    return magnifyingGlassRadius.value
  }
  
  const bounds = canvasImageBounds.value
  const canvas = imageCanvas.value
  
  // Calculate a base radius that's proportional to the smaller dimension of the displayed image
  const imageDisplayWidth = bounds.drawWidth
  const imageDisplayHeight = bounds.drawHeight
  const smallerDimension = Math.min(imageDisplayWidth, imageDisplayHeight)
  
  // Base radius is 8-15% of the smaller dimension, adjusted by user setting
  const baseRadius = (smallerDimension * 0.12) * (magnifyingGlassRadius.value / 50)
  
  // Inverse relationship with zoom - higher zoom = smaller radius for precision
  const zoomAdjustedRadius = baseRadius * (1.5 / magnifyingGlassZoom.value)
  
  // Ensure minimum and maximum bounds
  return Math.max(25, Math.min(zoomAdjustedRadius, 120))
})

// Computed property to get confidence values efficiently
const inferencesWithConfidence = computed(() => {
  // Use a more stable reference to avoid unnecessary re-renders
  return inferences.value.map(inference => {
    const confidence = getCachedConfidence(inference.id) || null
    // Only add confidence if it's different from what's already there
    if (inference.confidence === confidence) {
      return inference
    }
    return {
      ...inference,
      confidence
    }
  })
})

// Model details cache and toggle state
const modelDetailsCache = ref(new Map())
const showModelDetails = ref(false)

// Canvas refs and variables
const imageCanvas = ref(null)
const hiddenImage = ref(null)
const canvasContext = ref(null)
const canvasImageBounds = ref(null) // Store image drawing bounds for coordinate conversion

const goBack = () => {
  router.push('/profile') // Always return to the main profile page
}

// Close modal on Escape key
const handleKeydown = (event) => {
  if (event.key === 'Escape') {
    if (selectedInference.value) {
      closeInferenceDetail()
    } else {
      goBack()
    }
  }
}

// Add and remove keyboard event listeners
onMounted(async () => {
  document.addEventListener('keydown', handleKeydown)
  window.addEventListener('resize', handleResize)
  await loadInferences()
  
  // Check if there's an inference ID in the URL after loading
  const inferenceId = route.query.id
  if (inferenceId && inferences.value.length > 0) {
    const inference = inferences.value.find(i => i.id == inferenceId)
    if (inference) {
      await openInferenceDetail(inference)
    }
  }
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
  window.removeEventListener('resize', handleResize)
  
  // Clear preloaded images set
  preloadedImages.value.clear()
  
  // Clear metadata cache and tracking
  clearMetadata()
})

const formatActivityTime = (timestamp) => {
  try {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMinutes = Math.floor(diffMs / (1000 * 60))
    const diffHours = Math.floor(diffMinutes / 60)
    const diffDays = Math.floor(diffHours / 24)
    
    if (diffMinutes < 1) return 'Ahora mismo'
    if (diffMinutes < 60) return `Hace ${diffMinutes}m`
    if (diffHours < 24) return `Hace ${diffHours}h`
    if (diffDays === 1) return 'Ayer'
    if (diffDays < 7) return `Hace ${diffDays} días`
    
    return date.toLocaleDateString('es-ES')
  } catch (error) {
    return 'Fecha inválida'
  }
}

const formatDate = (timestamp) => {
  try {
    return new Date(timestamp).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  } catch (error) {
    return 'Fecha inválida'
  }
}

const formatTime = (timestamp) => {
  try {
    return new Date(timestamp).toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    return 'Hora inválida'
  }
}

const loadInferences = async (page = 1) => {
  try {
    loading.value = true
    error.value = null
    
    const apiUrl = import.meta.env.VITE_API_BASE_URL
    const response = await fetch(`${apiUrl}/users/inferences?page=${page}&limit=20`, {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      }
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    
    if (data.success && data.inferences) {
      if (page === 1) {
        inferences.value = data.inferences
      } else {
        inferences.value = [...inferences.value, ...data.inferences]
      }
      hasMore.value = data.pagination?.has_next || false
      
      // Preload images after a short delay to avoid conflicts with initial render
      nextTick(() => {
        setTimeout(() => {
          preloadGalleryImages()
        }, 500)
      })
    } else {
      throw new Error(data.error || 'Failed to fetch inferences')
    }
  } catch (err) {
    console.error('Error fetching inferences:', err)
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const loadMoreInferences = async () => {
  if (loading.value || !hasMore.value) return
  
  currentPage.value += 1
  await loadInferences(currentPage.value)
}

// Add a loading state for opening inference details
const openingInference = ref(false)

const openInferenceDetail = async (inference) => {
  // Prevent multiple rapid clicks
  if (openingInference.value) return
  
  openingInference.value = true
  
  try {
    selectedInference.value = inference
    // Reset model details toggle state
    showModelDetails.value = false
    
    // Always fetch metadata when opening inference detail
    try {
      await fetchMetadata(inference.id)
    } catch (error) {
      console.error('Error fetching metadata for inference:', inference.id, error)
    }
    
    // Update URL after metadata is loaded to avoid race conditions
    router.replace({ query: { ...route.query, id: inference.id } })
  } catch (error) {
    console.error('Error opening inference detail:', error)
  } finally {
    openingInference.value = false
  }
}

const closeInferenceDetail = () => {
  selectedInference.value = null
  showModelDetails.value = false
  // Reset box control state
  showBoxControls.value = false
  detectedBoxes.value = []
  selectedBox.value = null
  // Remove ID from URL and go back to profile
  router.push('/profile')
}

const backToGallery = () => {
  selectedInference.value = null
  showModelDetails.value = false
  // Reset box control state
  showBoxControls.value = false
  detectedBoxes.value = []
  selectedBox.value = null
  // Remove ID from URL but stay in gallery
  const { id, ...queryWithoutId } = route.query
  router.replace({ query: queryWithoutId })
}

const downloadResults = async () => {
  if (!selectedInference.value?.id) {
    console.error('No inference ID available for download')
    alert('No hay resultados disponibles para descargar')
    return
  }
  
  const apiUrl = import.meta.env.VITE_API_BASE_URL
  const inferenceId = selectedInference.value.id

  try {
    const response = await fetch(`${apiUrl}/inferences/${inferenceId}/download`, {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Accept': 'application/zip, */*'
      }
    })
    
    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`Server error ${response.status}: ${errorText}`)
    }

    const contentType = response.headers.get('Content-Type')
    
    if (contentType && contentType.includes('text/html')) {
      const errorText = await response.text()
      if (errorText.includes('<div id="app"></div>') || errorText.includes('@vite/client')) {
        throw new Error('API backend is not accessible. Please check if the backend server is running on the correct port.')
      } else {
        throw new Error('Server returned an error page instead of the download file')
      }
    }
    
    if (contentType && contentType.includes('application/json')) {
      const errorData = await response.json()
      throw new Error(errorData.message || 'Server error occurred')
    }
    
    if (!contentType || (!contentType.includes('application/zip') && !contentType.includes('application/octet-stream'))) {
      throw new Error(`Unexpected response type: ${contentType}. Expected ZIP file.`)
    }

    const blob = await response.blob()
    
    if (blob.size === 0) {
      throw new Error('Downloaded file is empty')
    }

    const url = window.URL.createObjectURL(new Blob([blob], { type: 'application/zip' }))
    
    let filename = `inference_${inferenceId}_results.zip`
    const contentDisposition = response.headers.get('Content-Disposition')
    
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/i)
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1].replace(/['"]/g, '')
      }
    }
    
    if (!filename.toLowerCase().endsWith('.zip')) {
      filename += '.zip'
    }

    const downloadLink = document.createElement('a')
    downloadLink.href = url
    downloadLink.download = filename
    downloadLink.style.display = 'none'
    
    document.body.appendChild(downloadLink)
    downloadLink.click()
    
    setTimeout(() => {
      document.body.removeChild(downloadLink)
      window.URL.revokeObjectURL(url)
    }, 100)
    
    alert('Descarga iniciada correctamente. El archivo se guardará en tu carpeta de descargas.')
    
  } catch (error) {
    alert('Error al descargar los resultados. Por favor, inténtalo de nuevo.')
  }
}

const deleteInference = async () => {
  if (!selectedInference.value?.id) {
    console.error('No inference ID available for deletion')
    alert('No hay análisis seleccionado para eliminar')
    return
  }
  
  const confirmation = confirm('¿Estás seguro de que deseas eliminar este análisis? Esta acción no se puede deshacer.')
  if (!confirmation) return
  
  const apiUrl = import.meta.env.VITE_API_BASE_URL
  const inferenceId = selectedInference.value.id

  try {
    const response = await makeSecureRequest(`${apiUrl}/inferences/${inferenceId}`, {
      method: 'DELETE',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      }
    })
    
    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`Server error ${response.status}: ${errorText}`)
    }

    const data = await response.json()
    
    if (data.success) {
      // Remove from local list
      inferences.value = inferences.value.filter(i => i.id !== inferenceId)
      // Clear metadata cache for this inference
      clearMetadata(inferenceId)
      // Close detail view
      closeInferenceDetail()
      alert('Análisis eliminado correctamente.')
    } else {
      throw new Error(data.error || 'Failed to delete inference')
    }
    
  } catch (error) {
    console.error('Error deleting inference:', error)
    alert('Error al eliminar el análisis. Por favor, inténtalo de nuevo.')
  }
}

// Computed property for the current image with selected boxes
const currentResultImage = computed(() => {
  if (!selectedInference.value) return null
  
  // If controls are hidden, show the normal results image with boxes already drawn
  if (!showBoxControls.value) {
    return selectedInference.value.generatedImageUrl
  }
  
  // If controls are visible, show the original image (without boxes)
  // so we can draw boxes manually on canvas using metadata from Minio
  return selectedInference.value.baseImageUrl
})

// Image caching functions
const preloadedImages = ref(new Set()) // Track which images have been preloaded

const getCachedImageUrl = (originalUrl) => {
  // For now, just return the original URL and let CSS handle the resizing
  // This is not ideal but avoids the double download issue
  // TODO: Implement server-side thumbnail generation
  return originalUrl
}

const preloadImage = async (imageUrl) => {
  if (!imageUrl || preloadedImages.value.has(imageUrl)) {
    return
  }

  try {
    // Create a hidden image element to trigger browser caching
    const img = new Image()
    img.crossOrigin = 'use-credentials'
    
    await new Promise((resolve, reject) => {
      img.onload = () => {
        preloadedImages.value.add(imageUrl)
        resolve()
      }
      img.onerror = reject
      img.src = imageUrl
    })
  } catch (error) {
    console.warn('Failed to preload image:', imageUrl, error)
  }
}

const preloadGalleryImages = async () => {
  // Preload first few images to improve performance
  const visibleInferences = inferences.value.slice(0, 10)
  
  for (const inference of visibleInferences) {
    if (inference.baseImageUrl) {
      try {
        await preloadImage(inference.baseImageUrl)
        // Small delay between each image
        await new Promise(resolve => setTimeout(resolve, 100))
      } catch (error) {
        console.warn('Failed to preload image:', inference.baseImageUrl, error)
      }
    }
  }
}

// Model details functions
const getModelDetails = (modelId) => {
  if (!modelId) return null
  
  // Check if we have it cached
  if (modelDetailsCache.value.has(modelId)) {
    return modelDetailsCache.value.get(modelId)
  }
  
  // Return null for now, will be loaded when requested
  return null
}

const fetchModelDetails = async (modelId) => {
  if (!modelId || modelDetailsCache.value.has(modelId)) {
    return modelDetailsCache.value.get(modelId)
  }
  
  try {
    const apiUrl = import.meta.env.VITE_API_BASE_URL
    const response = await fetch(`${apiUrl}/models/`, {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      if (data.success && data.models) {
        // Cache all models for future use
        data.models.forEach(model => {
          modelDetailsCache.value.set(model.id, {
            id: model.id,
            name: model.name,
            version: model.version,
            description: model.description,
            modelType: model.modelType,
            createdOn: model.createdOn,
            updatedOn: model.updatedOn
          })
        })
        
        return modelDetailsCache.value.get(modelId)
      }
    }
  } catch (error) {
    console.error('Error fetching model details:', error)
    // Cache null to avoid repeated failed requests
    modelDetailsCache.value.set(modelId, null)
  }
  
  return null
}

const toggleModelDetails = async () => {
  showModelDetails.value = !showModelDetails.value
  
  // Load model details if showing and not already loaded
  if (showModelDetails.value && selectedInference.value?.modelId) {
    await fetchModelDetails(selectedInference.value.modelId)
  }
}

const toggleBoxControls = async () => {
  imageLoading.value = true
  
  try {
    // Add a small delay to show the loading state during image transition
    await new Promise(resolve => setTimeout(resolve, 300))
    
    showBoxControls.value = !showBoxControls.value
    
    // If we're entering box control mode and don't have metadata, fetch it
    if (showBoxControls.value) {
      if (!isMetadataLoaded(selectedInference.value.id)) {
        await fetchMetadata(selectedInference.value.id)
      }
      
      // Try to setup canvas after metadata is loaded
      nextTick(() => {
        if (imageCanvas.value && hiddenImage.value && detectedBoxes.value.length > 0) {
          setupCanvas()
          drawImageWithBoxes()
        }
      })
    } else {
      // Clear selection when exiting edit mode but keep detectedBoxes for class counts
      selectedBox.value = null
      if (canvasContext.value) {
        canvasContext.value.clearRect(0, 0, imageCanvas.value.width, imageCanvas.value.height)
      }
    }
  } catch (error) {
    console.error('Error toggling box controls:', error)
  } finally {
    imageLoading.value = false
  }
}

const updateImageWithBoxes = () => {
  if (showBoxControls.value && canvasContext.value) {
    drawImageWithBoxes()
  }
  
  const visibleBoxes = detectedBoxes.value.filter(box => box.visible)
}

// Canvas setup and drawing functions
const onImageLoad = (inference) => {
  // Handle canvas setup for box drawing
  if (showBoxControls.value && imageCanvas.value && hiddenImage.value && detectedBoxes.value.length > 0) {
    nextTick(() => {
      setupCanvas()
      drawImageWithBoxes()
    })
  }
}

const setupCanvas = () => {
  if (!imageCanvas.value || !hiddenImage.value) {
    console.warn('Canvas setup failed: missing canvas or image', {
      canvas: !!imageCanvas.value,
      image: !!hiddenImage.value
    })
    return
  }
  
  const canvas = imageCanvas.value
  const img = hiddenImage.value
  const ctx = canvas.getContext('2d')
  canvasContext.value = ctx

  // Get the actual display size from the parent container
  const containerRect = canvas.parentElement.getBoundingClientRect()
  const containerWidth = containerRect.width
  
  // Calculate the actual display size based on max-h-[600px] and object-contain
  const maxHeight = 600
  const imageAspectRatio = img.naturalWidth / img.naturalHeight
  
  let displayWidth, displayHeight
  
  // Calculate actual display dimensions using object-contain logic
  if (containerWidth / maxHeight > imageAspectRatio) {
    // Height is the limiting factor
    displayHeight = Math.min(maxHeight, img.naturalHeight)
    displayWidth = displayHeight * imageAspectRatio
  } else {
    // Width is the limiting factor
    displayWidth = containerWidth
    displayHeight = displayWidth / imageAspectRatio
    if (displayHeight > maxHeight) {
      displayHeight = maxHeight
      displayWidth = displayHeight * imageAspectRatio
    }
  }
  
  // Set canvas size to match the actual displayed image size
  canvas.width = displayWidth
  canvas.height = displayHeight
  canvas.style.width = `${displayWidth}px`
  canvas.style.height = `${displayHeight}px`

  // Configure canvas context for better rendering
  ctx.imageSmoothingEnabled = true
  ctx.imageSmoothingQuality = 'high'

  // Store bounds for use in drawing and hit-testing (canvas fills exactly the image area)
  canvasImageBounds.value = {
    drawX: 0,
    drawY: 0,
    drawWidth: displayWidth,
    drawHeight: displayHeight,
    scaleX: displayWidth / img.naturalWidth,
    scaleY: displayHeight / img.naturalHeight
  }
}

const drawImageWithBoxes = () => {
  if (!canvasContext.value || !hiddenImage.value || !canvasImageBounds.value) {
    console.warn('Cannot draw: missing context, image, or bounds', {
      context: !!canvasContext.value,
      image: !!hiddenImage.value,
      bounds: !!canvasImageBounds.value
    })
    return
  }
  
  const ctx = canvasContext.value
  const canvas = imageCanvas.value
  const img = hiddenImage.value
  const bounds = canvasImageBounds.value
  
  // Clear canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  
  // Draw the image to fill the entire canvas (since canvas size matches display size)
  ctx.drawImage(img, bounds.drawX, bounds.drawY, bounds.drawWidth, bounds.drawHeight)

  // Only draw bounding boxes if magnifying glass is not active
  if (!magnifyingGlassActive.value) {
    // Get visible boxes with normalized coordinates
    const visibleBoxes = detectedBoxes.value.filter(box => box.visible && box.bbox_normalized)
    
    if (visibleBoxes.length > 0) {
      // Draw non-selected boxes first, then selected box on top
      const nonSelectedBoxes = visibleBoxes.filter(box => box !== selectedBox.value)
      const selectedBoxToDrawLast = visibleBoxes.find(box => box === selectedBox.value)
      
      // Reset line dash before drawing
      ctx.setLineDash([])
      
      // Draw non-selected boxes
      nonSelectedBoxes.forEach((box) => {
        drawBoundingBox(ctx, box)
      })
      
      // Draw selected box on top
      if (selectedBoxToDrawLast) {
        drawBoundingBox(ctx, selectedBoxToDrawLast)
      }
    }
  } else {
    // Draw magnifying glass
    drawMagnifyingGlass(ctx)
  }
}

const drawBoundingBox = (ctx, box) => {
  const { bbox_normalized, color, label, confidence } = box
  
  if (!bbox_normalized || typeof bbox_normalized !== 'object') {
    console.warn('Missing or invalid normalized coordinates for box:', box.label, bbox_normalized)
    return
  }
  
  // Validate normalized coordinates are in 0-1 range
  const { x1, y1, x2, y2 } = bbox_normalized
  if (x1 < 0 || x1 > 1 || y1 < 0 || y1 > 1 || x2 < 0 || x2 > 1 || y2 < 0 || y2 > 1) {
    console.warn('Normalized coordinates out of range (0-1):', bbox_normalized, 'for box:', box.label)
  }
  
  // Get canvas and image bounds
  const canvas = imageCanvas.value
  const bounds = canvasImageBounds.value
  
  if (!bounds) {
    console.warn('Canvas image bounds not available for coordinate conversion')
    return
  }
  
  // Convert normalized coordinates (0-1) to image pixel coordinates, then to canvas coordinates
  const imagePixelX1 = x1 * hiddenImage.value.naturalWidth
  const imagePixelY1 = y1 * hiddenImage.value.naturalHeight
  const imagePixelX2 = x2 * hiddenImage.value.naturalWidth
  const imagePixelY2 = y2 * hiddenImage.value.naturalHeight
  
  // Scale to canvas image size and add offsets for letterboxing
  const canvasX1 = Math.round(imagePixelX1 * bounds.scaleX + bounds.drawX)
  const canvasY1 = Math.round(imagePixelY1 * bounds.scaleY + bounds.drawY)
  const canvasX2 = Math.round(imagePixelX2 * bounds.scaleX + bounds.drawX)
  const canvasY2 = Math.round(imagePixelY2 * bounds.scaleY + bounds.drawY)
  
  // Calculate rectangle position and dimensions (ensuring positive dimensions)
  const x = Math.min(canvasX1, canvasX2)
  const y = Math.min(canvasY1, canvasY2)
  const width = Math.abs(canvasX2 - canvasX1)
  const height = Math.abs(canvasY2 - canvasY1)
  
  // Ensure we have valid dimensions
  if (width <= 0 || height <= 0) {
    console.warn('Invalid box dimensions:', { width, height, box: box.label, normalized: bbox_normalized })
    return
  }
  
  // Check if this box is selected for highlighting
  const isSelected = selectedBox.value === box
  
  // Draw box outline with highlighting
  ctx.strokeStyle = color
  ctx.lineWidth = isSelected ? 4 : 2  // Thicker line for selected box
  ctx.setLineDash(isSelected ? [5, 5] : [])  // Dashed line for selected box
  ctx.strokeRect(x, y, width, height)
  
  // Draw highlight background for selected box
  if (isSelected) {
    ctx.fillStyle = color + '20'  // Semi-transparent background
    ctx.fillRect(x, y, width, height)
    
    // Draw outer glow effect
    ctx.shadowColor = color
    ctx.shadowBlur = 10
    ctx.strokeStyle = color
    ctx.lineWidth = 2
    ctx.setLineDash([])
    ctx.strokeRect(x - 2, y - 2, width + 4, height + 4)
    
    // Reset shadow
    ctx.shadowColor = 'transparent'
    ctx.shadowBlur = 0
  }
  
  // Draw filled background for label
  const labelText = `${label} ${Math.round(confidence * 100)}%`
  ctx.font = isSelected ? 'bold 12px Inter, system-ui, sans-serif' : '12px Inter, system-ui, sans-serif'
  const textMetrics = ctx.measureText(labelText)
  const labelWidth = textMetrics.width + 8
  const labelHeight = 20
  
  // Position label above the box, but inside if near top edge
  const labelY = y > labelHeight ? y - labelHeight : y + labelHeight
  
  // Use brighter color for selected box label
  ctx.fillStyle = isSelected ? '#7C3AED' : color  // Purple for selected, original color otherwise
  ctx.fillRect(x, labelY, labelWidth, labelHeight)
  
  // Draw label text
  ctx.fillStyle = 'white'
  ctx.textAlign = 'left'
  ctx.textBaseline = 'middle'
  ctx.fillText(labelText, x + 4, labelY + labelHeight / 2)
}

const handleCanvasClick = (event) => {
  if (!showBoxControls.value || !canvasContext.value) return
  
  if (magnifyingGlassActive.value) return // Don't handle clicks when magnifying glass is active
  
  const canvas = imageCanvas.value
  const rect = canvas.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top
  
  // Find clicked box
  const clickedBox = findBoxAtPosition(x, y)
  if (clickedBox) {
    // Select the clicked box (or deselect if already selected)
    selectBox(clickedBox === selectedBox.value ? null : clickedBox)
  } else {
    // Clicked on empty area, deselect any selected box
    selectBox(null)
  }
}

const handleCanvasDoubleClick = (event) => {
  if (!showBoxControls.value || !canvasContext.value) return
  
  if (magnifyingGlassActive.value) return // Don't handle double clicks when magnifying glass is active
  
  const canvas = imageCanvas.value
  const rect = canvas.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top
  
  // Find double-clicked box
  const clickedBox = findBoxAtPosition(x, y)
  if (clickedBox) {
    // Toggle box visibility on double-click
    clickedBox.visible = !clickedBox.visible
    // Force reactivity update for the controls list
    detectedBoxes.value = [...detectedBoxes.value]
    updateImageWithBoxes()
  }
}

const handleCanvasMouseMove = (event) => {
  if (magnifyingGlassActive.value) {
    updateMagnifyingGlassPosition(event)
  }
}

const handleCanvasMouseLeave = () => {
  if (magnifyingGlassActive.value) {
    magnifyingGlassBoxes.value = []
    updateImageWithBoxes()
  }
}

const findBoxAtPosition = (x, y) => {
  const canvas = imageCanvas.value
  const bounds = canvasImageBounds.value
  
  if (!bounds) {
    return null // Can't find boxes without bounds
  }
  
  // Check boxes in reverse order (last drawn on top)
  for (let i = detectedBoxes.value.length - 1; i >= 0; i--) {
    const box = detectedBoxes.value[i]
    if (!box.visible || !box.bbox_normalized) continue
    
    // Convert normalized coordinates to canvas pixels (same logic as drawBoundingBox)
    const { x1, y1, x2, y2 } = box.bbox_normalized
    
    // Convert normalized coordinates to image pixel coordinates, then to canvas coordinates
    const imagePixelX1 = x1 * hiddenImage.value.naturalWidth
    const imagePixelY1 = y1 * hiddenImage.value.naturalHeight
    const imagePixelX2 = x2 * hiddenImage.value.naturalWidth
    const imagePixelY2 = y2 * hiddenImage.value.naturalHeight
    
    // Scale to canvas image size and add offsets for letterboxing
    const canvasX1 = Math.round(imagePixelX1 * bounds.scaleX + bounds.drawX)
    const canvasY1 = Math.round(imagePixelY1 * bounds.scaleY + bounds.drawY)
    const canvasX2 = Math.round(imagePixelX2 * bounds.scaleX + bounds.drawX)
    const canvasY2 = Math.round(imagePixelY2 * bounds.scaleY + bounds.drawY)
    
    // Calculate rectangle bounds (ensuring positive dimensions)
    const boxX = Math.min(canvasX1, canvasX2)
    const boxY = Math.min(canvasY1, canvasY2)
    const boxWidth = Math.abs(canvasX2 - canvasX1)
    const boxHeight = Math.abs(canvasY2 - canvasY1)
    
    if (x >= boxX && x <= boxX + boxWidth && y >= boxY && y <= boxY + boxHeight) {
      return box
    }
  }
  return null
}

// Window resize handler to adjust canvas
const handleResize = () => {
  if (showBoxControls.value && imageCanvas.value) {
    nextTick(() => {
      setupCanvas()
      drawImageWithBoxes()
    })
  }
}

const handleImageError = (event) => {
  event.target.src = '/frambuesas_1.jpg' // Fallback image
}

const selectBox = (box) => {
  selectedBox.value = selectedBox.value === box ? null : box
  
  // Redraw canvas to show selection highlighting
  if (showBoxControls.value) {
    updateImageWithBoxes()
  }
}

const toggleAllBoxes = (visible) => {
  detectedBoxes.value.forEach(box => {
    box.visible = visible
  })
  updateImageWithBoxes()
}

// Magnifying glass functions
const toggleMagnifyingGlass = () => {
  magnifyingGlassActive.value = !magnifyingGlassActive.value
  if (magnifyingGlassActive.value) {
    // Set initial position to center of canvas
    if (imageCanvas.value) {
      const rect = imageCanvas.value.getBoundingClientRect()
      magnifyingGlassPosition.value = {
        x: rect.width / 2,
        y: rect.height / 2
      }
    }
  }
  updateImageWithBoxes()
}

const updateMagnifyingGlassPosition = (event) => {
  if (!magnifyingGlassActive.value || !imageCanvas.value) return
  
  const canvas = imageCanvas.value
  const rect = canvas.getBoundingClientRect()
  const x = (event.clientX - rect.left) * (canvas.width / rect.width)
  const y = (event.clientY - rect.top) * (canvas.height / rect.height)
  
  magnifyingGlassPosition.value = { x, y }
  
  // Find boxes within magnifying glass area
  findBoxesInMagnifyingGlass(x, y)
  
  updateImageWithBoxes()
}

const findBoxesInMagnifyingGlass = (centerX, centerY) => {
  const bounds = canvasImageBounds.value
  
  if (!bounds) {
    magnifyingGlassBoxes.value = []
    return
  }
  

  const boxDistances = detectedBoxes.value
    .filter(box => box.visible && box.bbox_normalized)
    .map(box => {
      const { x1, y1, x2, y2 } = box.bbox_normalized
      
      // Convert normalized coordinates to canvas coordinates
      const canvasX1 = x1 * bounds.drawWidth + bounds.drawX
      const canvasY1 = y1 * bounds.drawHeight + bounds.drawY
      const canvasX2 = x2 * bounds.drawWidth + bounds.drawX
      const canvasY2 = y2 * bounds.drawHeight + bounds.drawY
      
      // Calculate box center and bounds
      const boxCenterX = (canvasX1 + canvasX2) / 2
      const boxCenterY = (canvasY1 + canvasY2) / 2
      const boxLeft = Math.min(canvasX1, canvasX2)
      const boxRight = Math.max(canvasX1, canvasX2)
      const boxTop = Math.min(canvasY1, canvasY2)
      const boxBottom = Math.max(canvasY1, canvasY2)
      
      // Calculate distance from crosshair to box center
      const distanceToCenter = Math.sqrt(
        Math.pow(centerX - boxCenterX, 2) + Math.pow(centerY - boxCenterY, 2)
      )
      
      // Check if crosshair is inside the box
      const isInside = centerX >= boxLeft && centerX <= boxRight && 
                      centerY >= boxTop && centerY <= boxBottom
      
      // Calculate distance from crosshair to nearest box edge if outside
      let distanceToBox = distanceToCenter
      if (!isInside) {
        const distanceToLeft = Math.abs(centerX - boxLeft)
        const distanceToRight = Math.abs(centerX - boxRight)
        const distanceToTop = Math.abs(centerY - boxTop)
        const distanceToBottom = Math.abs(centerY - boxBottom)
        
        if (centerX < boxLeft) {
          if (centerY < boxTop) {
            // Top-left corner
            distanceToBox = Math.sqrt(Math.pow(centerX - boxLeft, 2) + Math.pow(centerY - boxTop, 2))
          } else if (centerY > boxBottom) {
            // Bottom-left corner
            distanceToBox = Math.sqrt(Math.pow(centerX - boxLeft, 2) + Math.pow(centerY - boxBottom, 2))
          } else {
            // Left edge
            distanceToBox = distanceToLeft
          }
        } else if (centerX > boxRight) {
          if (centerY < boxTop) {
            // Top-right corner
            distanceToBox = Math.sqrt(Math.pow(centerX - boxRight, 2) + Math.pow(centerY - boxTop, 2))
          } else if (centerY > boxBottom) {
            // Bottom-right corner
            distanceToBox = Math.sqrt(Math.pow(centerX - boxRight, 2) + Math.pow(centerY - boxBottom, 2))
          } else {
            // Right edge
            distanceToBox = distanceToRight
          }
        } else {
          // Above or below
          distanceToBox = centerY < boxTop ? distanceToTop : distanceToBottom
        }
      } else {
        // Inside the box - use negative distance for priority
        distanceToBox = -Math.min(
          Math.min(centerX - boxLeft, boxRight - centerX),
          Math.min(centerY - boxTop, boxBottom - centerY)
        )
      }
      
      return {
        ...box,
        distanceToCenter,
        distanceToBox,
        isInside
      }
    })
    .sort((a, b) => {
      // Prioritize boxes containing the crosshair, then by distance
      if (a.isInside && !b.isInside) return -1
      if (!a.isInside && b.isInside) return 1
      
      // For boxes both inside or both outside, sort by distance
      return a.distanceToBox - b.distanceToBox
    })
  
  // Take the closest boxes (up to 5) within a reasonable range
  const maxDistance = 150 // Maximum distance to consider a box "relevant"
  magnifyingGlassBoxes.value = boxDistances
    .filter(box => box.isInside || box.distanceToBox <= maxDistance)
    .slice(0, 5) // Limit to 5 boxes for performance
    .map(box => {
      // Set intersection area for compatibility with existing code
      // Higher values for closer boxes or boxes containing the crosshair
      if (box.isInside) {
        box.intersectionArea = 1.0 - (box.distanceToCenter / 1000) // High priority for inside boxes
      } else {
        box.intersectionArea = Math.max(0, 1.0 - (box.distanceToBox / maxDistance))
      }
      return box
    })
}

const drawMagnifyingGlass = (ctx) => {
  if (!magnifyingGlassActive.value || !hiddenImage.value || !canvasImageBounds.value) return
  
  const { x, y } = magnifyingGlassPosition.value
  const radius = adaptiveMagnifyingGlassRadius.value
  const zoom = magnifyingGlassZoom.value
  const bounds = canvasImageBounds.value
  const img = hiddenImage.value
  
  // Save current context state
  ctx.save()
  
  // Create circular clipping path
  ctx.beginPath()
  ctx.arc(x, y, radius, 0, 2 * Math.PI)
  ctx.clip()
  
  // Clear the clipped area
  ctx.clearRect(x - radius, y - radius, radius * 2, radius * 2)
  
  // Calculate source coordinates on the original image
  const sourceX = ((x - bounds.drawX) / bounds.drawWidth) * img.naturalWidth
  const sourceY = ((y - bounds.drawY) / bounds.drawHeight) * img.naturalHeight
  const sourceSize = (radius * 2) / zoom
  
  // Draw zoomed image portion
  ctx.drawImage(
    img,
    sourceX - sourceSize / 2, sourceY - sourceSize / 2, sourceSize, sourceSize,
    x - radius, y - radius, radius * 2, radius * 2
  )
  
  // Restore context to remove clipping
  ctx.restore()
  
  // Draw magnifying glass border with color coding
  drawMagnifyingGlassBorder(ctx, x, y, radius)
  
  // Draw directional guidance
  drawMagnifyingGlassGuidance(ctx, x, y, radius)
  
  // Draw box information overlay
  drawMagnifyingGlassOverlay(ctx, x, y, radius)
}

const drawMagnifyingGlassBorder = (ctx, centerX, centerY, radius) => {
  const borderWidth = 4
  
  ctx.lineWidth = borderWidth
  
  if (magnifyingGlassBoxes.value.length === 0) {
    // Default gray border when no boxes
    ctx.strokeStyle = '#6B7280'
    ctx.beginPath()
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI)
    ctx.stroke()
  } else {
    // Use the color of the most dominant box (largest intersection area)
    const dominantBox = magnifyingGlassBoxes.value[0] // Already sorted by area, largest first
    
    // Draw main border in dominant box color
    ctx.strokeStyle = dominantBox.color
    ctx.beginPath()
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI)
    ctx.stroke()
    
    // Draw corner indicators for other boxes (if any)
    if (magnifyingGlassBoxes.value.length > 1) {
      const indicatorSize = 8
      const cornerOffset = 12
      const corners = [
        { x: centerX + radius - cornerOffset, y: centerY - radius + cornerOffset }, // Top-right
        { x: centerX + radius - cornerOffset, y: centerY + radius - cornerOffset }, // Bottom-right
        { x: centerX - radius + cornerOffset, y: centerY + radius - cornerOffset }, // Bottom-left
        { x: centerX - radius + cornerOffset, y: centerY - radius + cornerOffset }  // Top-left
      ]
      
      // Show up to 4 additional boxes in corners
      magnifyingGlassBoxes.value.slice(1, 5).forEach((box, index) => {
        const corner = corners[index]
        if (corner) {
          // Draw small colored square indicator
          ctx.fillStyle = box.color
          ctx.fillRect(
            corner.x - indicatorSize / 2, 
            corner.y - indicatorSize / 2, 
            indicatorSize, 
            indicatorSize
          )
          
          // Add white border to indicator for better visibility
          ctx.strokeStyle = 'white'
          ctx.lineWidth = 1
          ctx.strokeRect(
            corner.x - indicatorSize / 2, 
            corner.y - indicatorSize / 2, 
            indicatorSize, 
            indicatorSize
          )
        }
      })
    }
  }
  
  // Add outer highlight
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.8)'
  ctx.lineWidth = 1
  ctx.beginPath()
  ctx.arc(centerX, centerY, radius + borderWidth / 2 + 1, 0, 2 * Math.PI)
  ctx.stroke()
}

const drawMagnifyingGlassGuidance = (ctx, centerX, centerY, radius) => {
  const crosshairSize = Math.min(12, radius * 0.2)
  
  // Check if we have a dominant box to guide towards
  const dominantBox = magnifyingGlassBoxes.value.length > 0 ? magnifyingGlassBoxes.value[0] : null
  
  if (dominantBox && dominantBox.bbox_normalized && canvasImageBounds.value) {
    const bounds = canvasImageBounds.value
    const { x1, y1, x2, y2 } = dominantBox.bbox_normalized
    
    // Calculate box center in canvas coordinates
    const boxCenterX = ((x1 + x2) / 2) * bounds.drawWidth + bounds.drawX
    const boxCenterY = ((y1 + y2) / 2) * bounds.drawHeight + bounds.drawY
    
    // Use the distance data we already calculated
    const distanceToBoxCenter = dominantBox.distanceToCenter || 0
    const isInsideBox = dominantBox.isInside || false
    
    // Be more strict about when to show special states
    // Only show "near center" when actually close to center (within 8px)
    const isNearBoxCenter = distanceToBoxCenter < 8
    // Only show "inside box" indicators when BOTH inside the box AND close to center
    const showInsideBoxState = isInsideBox && isNearBoxCenter
    
    // Always show arrow - it provides useful distance information
    const shouldShowArrow = true
    
    if (shouldShowArrow) {
      // Calculate direction to box center
      const deltaX = boxCenterX - centerX
      const deltaY = boxCenterY - centerY
      
      // Draw directional arrow pointing to box center
      const angle = Math.atan2(deltaY, deltaX)
      const arrowDistance = radius * 0.6 // Position arrow inside the magnifying glass
      const arrowX = centerX + Math.cos(angle) * arrowDistance
      const arrowY = centerY + Math.sin(angle) * arrowDistance
      
      // Use different arrow style when inside the box vs outside
      // Use box color with better contrast instead of gold
      let arrowBgColor
      if (isInsideBox) {
        arrowBgColor = dominantBox.color
      } else {
        arrowBgColor = 'rgba(0, 0, 0, 0.8)'
      }
      
      // Draw arrow background (semi-transparent circle) - make it bigger when inside box
      const bgRadius = isInsideBox ? 10 : 8
      ctx.fillStyle = arrowBgColor
      ctx.beginPath()
      ctx.arc(arrowX, arrowY, bgRadius, 0, 2 * Math.PI)
      ctx.fill()
      
      // Draw arrow pointing to box center
      const arrowSize = isInsideBox ? 7 : 6 // Slightly bigger when inside
      ctx.fillStyle = isInsideBox ? 'white' : dominantBox.color // Inverted colors for better contrast
      ctx.strokeStyle = isInsideBox ? 'rgba(0, 0, 0, 0.5)' : 'white' 
      ctx.lineWidth = 2
      
      ctx.beginPath()
      ctx.moveTo(
        arrowX + Math.cos(angle) * arrowSize,
        arrowY + Math.sin(angle) * arrowSize
      )
      ctx.lineTo(
        arrowX + Math.cos(angle + 2.5) * arrowSize * 0.6,
        arrowY + Math.sin(angle + 2.5) * arrowSize * 0.6
      )
      ctx.lineTo(
        arrowX + Math.cos(angle - 2.5) * arrowSize * 0.6,
        arrowY + Math.sin(angle - 2.5) * arrowSize * 0.6
      )
      ctx.closePath()
      ctx.fill()
      ctx.stroke()
      
      // Draw distance indicator text with consistent styling
      const distance = Math.round(distanceToBoxCenter)
      ctx.font = 'bold 10px Inter'
      ctx.fillStyle = 'white'
      ctx.strokeStyle = 'rgba(0, 0, 0, 0.8)'
      ctx.lineWidth = 2
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      
      // Position text near the arrow
      const textX = arrowX + Math.cos(angle + Math.PI/2) * 15
      const textY = arrowY + Math.sin(angle + Math.PI/2) * 15
      
      // Add subtle prefix when inside box to clarify
      const displayText = isInsideBox ? `→ ${distance}px` : `${distance}px`
      
      ctx.strokeText(displayText, textX, textY)
      ctx.fillText(displayText, textX, textY)
    }
    
    // Draw enhanced crosshair based on strict conditions
    if (showInsideBoxState) {
      // Special "inside box and near center" crosshair - this is the target state
      drawBullseyeCrosshair(ctx, centerX, centerY, crosshairSize, dominantBox.color, true)
    } else if (isNearBoxCenter) {
      // Just near center but not inside box - regular bullseye
      drawBullseyeCrosshair(ctx, centerX, centerY, crosshairSize, dominantBox.color, false)
    } else {
      // Standard crosshair with direction hint
      const deltaX = boxCenterX - centerX
      const deltaY = boxCenterY - centerY
      drawStandardCrosshair(ctx, centerX, centerY, crosshairSize, dominantBox.color, deltaX, deltaY)
    }
  } else {
    // No dominant box - draw standard neutral crosshair
    drawStandardCrosshair(ctx, centerX, centerY, crosshairSize, '#6B7280', 0, 0)
  }
}

const drawBullseyeCrosshair = (ctx, centerX, centerY, size, boxColor, isInsideBox = false) => {
  if (isInsideBox) {
    // DRAMATICALLY DIFFERENT: Solid filled circle with crosshair overlay - "TARGET ACQUIRED"
    
    // Large filled circle background
    ctx.fillStyle = `${boxColor}E0` // Semi-transparent
    ctx.beginPath()
    ctx.arc(centerX, centerY, size * 0.8, 0, 2 * Math.PI)
    ctx.fill()
    
    // Solid border
    ctx.strokeStyle = boxColor
    ctx.lineWidth = 3
    ctx.beginPath()
    ctx.arc(centerX, centerY, size * 0.8, 0, 2 * Math.PI)
    ctx.stroke()
    
    // White crosshair overlay (thick and bold)
    const crossSize = size * 0.6
    ctx.strokeStyle = 'white'
    ctx.lineWidth = 4
    ctx.setLineDash([])
    
    // Horizontal line
    ctx.beginPath()
    ctx.moveTo(centerX - crossSize, centerY)
    ctx.lineTo(centerX + crossSize, centerY)
    ctx.stroke()
    
    // Vertical line
    ctx.beginPath()
    ctx.moveTo(centerX, centerY - crossSize)
    ctx.lineTo(centerX, centerY + crossSize)
    ctx.stroke()
    
    // Add black outline to crosshair
    ctx.strokeStyle = 'rgba(0, 0, 0, 0.4)'
    ctx.lineWidth = 6
    
    // Horizontal line outline
    ctx.beginPath()
    ctx.moveTo(centerX - crossSize, centerY)
    ctx.lineTo(centerX + crossSize, centerY)
    ctx.stroke()
    
    // Vertical line outline
    ctx.beginPath()
    ctx.moveTo(centerX, centerY - crossSize)
    ctx.lineTo(centerX, centerY + crossSize)
    ctx.stroke()
    
    // Redraw white crosshair on top
    ctx.strokeStyle = 'white'
    ctx.lineWidth = 4
    
    // Horizontal line
    ctx.beginPath()
    ctx.moveTo(centerX - crossSize, centerY)
    ctx.lineTo(centerX + crossSize, centerY)
    ctx.stroke()
    
    // Vertical line
    ctx.beginPath()
    ctx.moveTo(centerX, centerY - crossSize)
    ctx.lineTo(centerX, centerY + crossSize)
    ctx.stroke()
    
    // Success indicator text
    ctx.font = 'bold 8px Inter'
    ctx.fillStyle = 'white'
    ctx.strokeStyle = 'rgba(0, 0, 0, 0.7)'
    ctx.lineWidth = 2
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.strokeText('TARGET', centerX, centerY + size + 8)
    ctx.fillText('TARGET', centerX, centerY + size + 8)
    
  } else {
    // COMPLETELY DIFFERENT: Traditional concentric rings - "APPROACHING TARGET"
    
    // Multiple thin rings (classic bullseye)
    const rings = [
      { radius: size * 0.8, color: boxColor, width: 2 },
      { radius: size * 0.6, color: 'rgba(255, 255, 255, 0.9)', width: 2 },
      { radius: size * 0.4, color: boxColor, width: 2 },
      { radius: size * 0.2, color: 'rgba(255, 255, 255, 0.9)', width: 2 }
    ]
    
    rings.forEach(ring => {
      ctx.strokeStyle = ring.color
      ctx.lineWidth = ring.width
      ctx.setLineDash([])
      ctx.beginPath()
      ctx.arc(centerX, centerY, ring.radius, 0, 2 * Math.PI)
      ctx.stroke()
    })
    
    // Small center dot
    ctx.fillStyle = boxColor
    ctx.beginPath()
    ctx.arc(centerX, centerY, 2, 0, 2 * Math.PI)
    ctx.fill()
    
    // Approaching indicator text
    ctx.font = 'bold 7px Inter'
    ctx.fillStyle = boxColor
    ctx.strokeStyle = 'white'
    ctx.lineWidth = 2
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.strokeText('CLOSE', centerX, centerY + size + 8)
    ctx.fillText('CLOSE', centerX, centerY + size + 8)
  }
}

const drawStandardCrosshair = (ctx, centerX, centerY, size, color, deltaX, deltaY) => {
  // Standard crosshair with optional directional bias
  const hasDirection = deltaX !== 0 || deltaY !== 0
  
  // Make crosshair slightly biased toward the target direction
  const biasStrength = hasDirection ? Math.min(size * 0.3, 4) : 0
  const angle = hasDirection ? Math.atan2(deltaY, deltaX) : 0
  
  const offsetX = Math.cos(angle) * biasStrength
  const offsetY = Math.sin(angle) * biasStrength
  
  ctx.strokeStyle = 'rgba(0, 0, 0, 0.4)'
  ctx.lineWidth = 2.5
  ctx.setLineDash([])
  
  // Vertical line with bias
  ctx.beginPath()
  ctx.moveTo(centerX + offsetX, centerY - size + offsetY)
  ctx.lineTo(centerX + offsetX, centerY + size + offsetY)
  ctx.stroke()
  
  // Horizontal line with bias
  ctx.beginPath()
  ctx.moveTo(centerX - size + offsetX, centerY + offsetY)
  ctx.lineTo(centerX + size + offsetX, centerY + offsetY)
  ctx.stroke()
  
  // White crosshair on top
  ctx.strokeStyle = hasDirection ? color : 'rgba(255, 255, 255, 0.8)'
  ctx.lineWidth = 1.5
  ctx.setLineDash([3, 2])
  
  // Vertical line
  ctx.beginPath()
  ctx.moveTo(centerX + offsetX, centerY - size + offsetY)
  ctx.lineTo(centerX + offsetX, centerY + size + offsetY)
  ctx.stroke()
  
  // Horizontal line
  ctx.beginPath()
  ctx.moveTo(centerX - size + offsetX, centerY + offsetY)
  ctx.lineTo(centerX + size + offsetX, centerY + offsetY)
  ctx.stroke()
  
  // Reset line dash
  ctx.setLineDash([])
}

const drawMagnifyingGlassOverlay = (ctx, centerX, centerY, radius) => {
  if (magnifyingGlassBoxes.value.length === 0) return
  
  // Position overlay to the side that has more space
  const canvas = imageCanvas.value
  const overlayWidth = 220
  const overlayHeight = Math.min(magnifyingGlassBoxes.value.length * 30 + 30, 200) // Cap height
  
  let overlayX, overlayY
  
  // Determine best position for overlay
  if (centerX + radius + overlayWidth + 10 < canvas.width) {
    // Right side
    overlayX = centerX + radius + 10
    overlayY = centerY - overlayHeight / 2
  } else if (centerX - radius - overlayWidth - 10 > 0) {
    // Left side
    overlayX = centerX - radius - overlayWidth - 10
    overlayY = centerY - overlayHeight / 2
  } else if (centerY - radius - overlayHeight - 10 > 0) {
    // Top
    overlayX = centerX - overlayWidth / 2
    overlayY = centerY - radius - overlayHeight - 10
  } else {
    // Bottom
    overlayX = centerX - overlayWidth / 2
    overlayY = centerY + radius + 10
  }
  
  // Ensure overlay stays within canvas bounds
  overlayX = Math.max(5, Math.min(overlayX, canvas.width - overlayWidth - 5))
  overlayY = Math.max(5, Math.min(overlayY, canvas.height - overlayHeight - 5))
  
  // Draw overlay background
  ctx.fillStyle = 'rgba(0, 0, 0, 0.85)'
  ctx.fillRect(overlayX, overlayY, overlayWidth, overlayHeight)
  
  // Draw overlay border
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)'
  ctx.lineWidth = 1
  ctx.strokeRect(overlayX, overlayY, overlayWidth, overlayHeight)
  
  // Draw header
  ctx.font = 'bold 12px Inter, system-ui, sans-serif'
  ctx.textAlign = 'left'
  ctx.textBaseline = 'middle'
  ctx.fillStyle = 'white'
  ctx.fillText('Objetos detectados:', overlayX + 10, overlayY + 15)
  
  // Draw box information
  ctx.font = '11px Inter, system-ui, sans-serif'
  
  magnifyingGlassBoxes.value.slice(0, 6).forEach((box, index) => { // Show max 6 boxes
    const yPos = overlayY + 35 + index * 25
    const isDominant = index === 0
    
    // Highlight dominant box
    if (isDominant) {
      ctx.fillStyle = 'rgba(255, 255, 255, 0.1)'
      ctx.fillRect(overlayX + 5, yPos - 10, overlayWidth - 10, 20)
    }
    
    // Color indicator (larger for dominant box)
    const indicatorSize = isDominant ? 14 : 10
    ctx.fillStyle = box.color
    ctx.fillRect(overlayX + 10, yPos - indicatorSize/2, indicatorSize, indicatorSize)
    
    // White border for indicator
    ctx.strokeStyle = 'white'
    ctx.lineWidth = 1
    ctx.strokeRect(overlayX + 10, yPos - indicatorSize/2, indicatorSize, indicatorSize)
    
    // Text (bold for dominant box)
    ctx.font = isDominant ? 'bold 11px Inter' : '11px Inter'
    ctx.fillStyle = isDominant ? '#ffffff' : '#e5e7eb'
    const text = `${box.label} ${Math.round(box.confidence * 100)}%`
    const coverage = `(${Math.round(box.intersectionArea * 100)}% visible)`
    
    ctx.fillText(text, overlayX + 30, yPos - 5)
    
    // Coverage percentage in smaller text
    ctx.font = '9px Inter'
    ctx.fillStyle = isDominant ? '#d1d5db' : '#9ca3af'
    ctx.fillText(coverage, overlayX + 30, yPos + 7)
    
    // Crown icon for dominant box
    if (isDominant) {
      ctx.fillStyle = '#fbbf24'
      ctx.font = '12px Arial'
      ctx.fillText('👑', overlayX + overlayWidth - 25, yPos)
    }
  })
  
  // Show count if there are more boxes
  if (magnifyingGlassBoxes.value.length > 6) {
    ctx.font = '10px Inter'
    ctx.fillStyle = '#9ca3af'
    ctx.fillText(`+${magnifyingGlassBoxes.value.length - 6} más...`, overlayX + 10, overlayY + overlayHeight - 10)
  }
}
</script>

<style>
.modal-overlay {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  background-color: rgba(0, 0, 0, 0.6) !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  z-index: 999999 !important;
  padding: 1rem !important;
}

.modal-container {
  background-color: white !important;
  border-radius: 1.5rem !important;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25) !important;
  max-width: 90rem !important;
  width: 95% !important;
  max-height: 95vh !important;
  overflow: hidden !important;
  transform: scale(1) !important;
  transition: all 0.3s ease !important;
  display: flex !important;
  flex-direction: column !important;
}

.modal-container:hover {
  transform: scale(1.01) !important;
}

.gallery-item {
  transition: box-shadow 0.2s ease !important;
  will-change: box-shadow !important;
}

.gallery-item:hover {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04) !important;
  transform: translateY(-2px) !important;
}

.gallery-item img {
  transition: transform 0.2s ease !important;
  will-change: transform !important;
}

.gallery-item:hover img {
  transform: scale(1.05) !important;
}

/* Canvas cursor styles */
canvas {
  transition: cursor 0.2s ease;
}

canvas:hover {
  cursor: pointer;
}

/* Magnifying glass cursor styles */
canvas.cursor-none {
  cursor: none;
}

/* Enhanced magnifying glass overlay styling */
.magnifying-overlay {
  pointer-events: none;
  font-family: 'Inter', system-ui, sans-serif;
}
</style>
