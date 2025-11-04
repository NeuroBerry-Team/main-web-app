<template>
  <div class="page-wrapper">

    <div class="logo-wrapper">
      <img src="/NeuroBerry_horizontal.png" alt="NeuroBerry Logo" class="logo-image" />
    </div>

    <section class="hero-section animated-section">
      <h1 class="section-title">Etiquetado Demo</h1>
      <p class="hero-text">
        Esta demostración simula el proceso de etiquetado de frambuesas para entrenar la IA. Puedes seleccionar una etiqueta y dibujar un cuadro sobre la imagen para ver cómo se haría en la práctica.
      </p>
    </section>

    <section class="tagging-demo animated-section" style="animation-delay: 0.2s;">
      <h2 class="section-title">Generación de la Base de Datos</h2>

      <div class="classes-description-container">
        <div v-for="(label, index) in labels" :key="label.name" class="class-item animated-item" :style="{ 'animation-delay': (0.3 + index * 0.1) + 's' }">
          <div class="color-box" :style="{backgroundColor: label.color}"></div>
          <p class="class-text">
            <strong>{{ label.name }}</strong>: {{ label.description }}
          </p>
        </div>
      </div>

      <div class="demo-image-wrapper">
        <div class="demo-container" ref="imageContainer">
          <img 
            ref="demoImage" 
            src="/etiquetado_1.jpg" 
            alt="Frambuesa Ejemplo" 
            class="demo-image"
            @click="createBox($event)"
          />

          <div 
            v-for="(box, index) in boxes" 
            :key="index" 
            class="tag-box animated-tag-box" 
            :style="{top: box.top + 'px', left: box.left + 'px', borderColor: box.color, animationDelay: (0.1 * index) + 's'}"
          >
            {{ box.label }}
          </div>
        </div>

        <div class="tag-controls">
          <div class="tag-buttons animated-item" style="animation-delay: 0.8s;">
            <button 
              v-for="label in labels" 
              :key="label.name" 
              :style="{backgroundColor: label.color, outline: selectedLabel === label.name ? '3px solid #333' : 'none'}" 
              @click="selectLabel(label.name)"
            >
              {{ label.name }}
            </button>
          </div>

          <p v-if="selectedLabel" class="selected-message animated-item" style="animation-delay: 0.9s;">
            Etiqueta seleccionada: <strong>{{ selectedLabel }}</strong>
          </p>
        </div>
      </div>
    </section>

    <section class="examples-section animated-section" style="animation-delay: 0.6s;">
      <h2 class="section-title">Ejemplos Explicativos</h2>

      <div class="examples-grid">
        <div v-for="(example, index) in examples" :key="index" class="example-item animated-item" :style="{ 'animation-delay': (0.7 + index * 0.1) + 's' }">
          <img :src="example.image" :alt="example.title" class="example-image" />
          <div class="example-text">
            <h3>{{ example.title }}</h3>
            <p>{{ example.description }}</p>
          </div>
        </div>
      </div>
    </section>

  </div>
</template>

<script setup>
import { ref } from 'vue'

const demoImage = ref(null)
const imageContainer = ref(null)

const labels = [
  { name: 'DarkRed', color: '#8B0000', description: 'Frambuesa muy roja, en su punto máximo de maduración.' },
  { name: 'Cherry Red', color: '#FF4D4D', description: 'Frambuesa de color rojo cereza, lista para consumo.' },
  { name: 'Orange Dot', color: '#FFA500', description: 'Frambuesa con puntos naranjas o rojos, en transición de maduración.' },
  { name: 'Green', color: '#ADFF2F', description: 'Frambuesa verde amarillosa, aún inmadura.' },
  { name: 'Button', color: '#008000', description: 'Botón de referencia o para el inicio de la fruta.' }
]

const selectedLabel = ref('')
const boxes = ref([])

function selectLabel(label) {
  selectedLabel.value = label
}

function createBox(event) {
  if (!selectedLabel.value) return

  const imageRect = demoImage.value.getBoundingClientRect();
  const scaleX = demoImage.value.naturalWidth / imageRect.width;
  const scaleY = demoImage.value.naturalHeight / imageRect.height;

  const top = event.clientY - imageRect.top;
  const left = event.clientX - imageRect.left;

  const color = labels.find(l => l.name === selectedLabel.value)?.color || '#000'

  boxes.value.push({
    top: top - 15,   
    left: left - 30,
    label: selectedLabel.value,
    color
  })
}

const examples = [
  { image: '/fram/fram2.png', title: 'Frambuesa Muy Roja', description: 'Frambuesa con tonalidad roja oscura, indicando plena madurez.' },
  { image: '/fram/fram1.png', title: 'Frambuesa Cherry Red', description: 'Tono rojo brillante, ideal para la cosecha y el consumo inmediato.' },
  { image: '/fram/fram3.png', title: 'Frambuesa Orange Dot', description: 'Presenta manchas naranjas o un color general anaranjado, en proceso de maduración.' },
  { image: '/fram/fram4.png', title: 'Frambuesa Verde', description: 'Color verde pálido a amarillento, aún no apta para la cosecha.' },
  { image: '/fram/fram5.png', title: 'Botón de Frambuesa', description: 'Fase inicial del fruto, pequeño y de color verde intenso.' }
]
</script>

<style scoped>
.page-wrapper {
  width: 100%;
  min-height: 100vh;
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
  font-family: 'Poppins', sans-serif;
  color: #333;
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
  text-align: center;
  background-color: #fff;
  overflow-x: hidden;
}
@media (min-width: 640px) {
  .page-wrapper {
    padding: 2rem;
    gap: 4rem;
  }
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

section {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  text-align: center;
}

/* --- Animaciones generales --- */
.animated-section, .animated-item {
  opacity: 0;
  animation: fadeInUp 0.8s ease-out forwards;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: #b22222;
  margin-bottom: 1rem;
  word-wrap: break-word;
  overflow-wrap: break-word;
  hyphens: auto;
}
@media (min-width: 640px) {
  .section-title {
    font-size: 2rem;
  }
}
@media (min-width: 768px) {
  .section-title {
    font-size: 2.5rem;
  }
}

.hero-text {
  max-width: 900px;
  margin: 0 auto;
  text-align: center;
  font-size: 1rem;
  line-height: 1.8;
  color: #555;
  word-wrap: break-word;
  overflow-wrap: break-word;
}
@media (min-width: 768px) {
  .hero-text {
    font-size: 1.2rem;
  }
}

/* --- Contenedor de descripciones de clases --- */
.classes-description-container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  margin: 1rem auto 2rem auto;
  max-width: 900px;
}
@media (min-width: 640px) {
  .classes-description-container {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.25rem;
    margin: 1rem auto 2.5rem auto;
  }
}
@media (min-width: 768px) {
  .classes-description-container {
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 280px), 1fr));
    gap: 1.5rem;
    margin: 1rem auto 3rem auto;
  }
}

.class-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-align: left;
  background-color: #f9f9f9;
  padding: 0.85rem;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  border: 1px solid #eee;
  overflow-x: hidden;
  word-wrap: break-word;
}
@media (min-width: 640px) {
  .class-item {
    gap: 1rem;
    padding: 1rem;
  }
}

.color-box {
  min-width: 25px;
  height: 25px;
  border-radius: 6px;
  border: 2px solid rgba(0,0,0,0.1);
  flex-shrink: 0;
}
@media (min-width: 640px) {
  .color-box {
    min-width: 30px;
    height: 30px;
  }
}

.class-text {
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0;
  word-wrap: break-word;
  overflow-wrap: break-word;
}
@media (min-width: 640px) {
  .class-text {
    font-size: 1rem;
  }
}

/* --- Contenedor de la demo de etiquetado --- */
.tagging-demo {
  display: flex;
  flex-direction: column;
  gap: 2.5rem; /* Más espacio entre elementos */
  align-items: center;
}

.demo-image-wrapper {
  background-color: #fff;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1); /* Sombra más grande */
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  max-width: 700px; /* Controlar el ancho máximo del wrapper */
  width: 95%;
}

.demo-container {
  position: relative;
  width: 100%; /* Ocupa el 100% del wrapper */
  padding-bottom: 66.66%; /* Proporción 3:2 (altura / ancho) */
  height: 0;
  overflow: hidden;
  border-radius: 10px;
}

.demo-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 10px;
  cursor: crosshair;
}

.tag-controls {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  width: 100%;
}

.tag-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem; /* Más espacio entre botones */
  justify-content: center;
}

.tag-buttons button {
  padding: 0.7rem 1.4rem; /* Más padding */
  border-radius: 25px; /* Forma de píldora */
  color: white;
  border: none;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 3px 8px rgba(0,0,0,0.1); /* Sombra para los botones */
}

.tag-buttons button:hover {
  transform: translateY(-3px) scale(1.02); /* Animación más notoria */
  box-shadow: 0 6px 15px rgba(0,0,0,0.15);
}

.selected-message {
  font-size: 1.1rem; /* Tamaño de fuente ajustado */
  color: #b22222;
  font-weight: 700;
  margin-top: 0.5rem; /* Espacio superior */
}

.tag-box {
  position: absolute;
  min-width: 60px; /* Ancho mínimo */
  height: 30px;
  border: 2px solid;
  border-radius: 5px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 0.85rem; /* Tamaño de fuente ligeramente mayor */
  font-weight: 700;
  color: white; /* Color de texto blanco para contraste */
  text-shadow: 0 0 3px rgba(0,0,0,0.5); /* Sombra para el texto */
  background-color: rgba(0,0,0,0.4); /* Fondo más oscuro */
  padding: 0 5px; /* Padding interno */
  animation: fadeIn 0.3s ease-out; /* Animación de entrada para las cajas */
}

.animated-tag-box {
  opacity: 0;
  animation: fadeInScale 0.3s ease-out forwards;
}

/* --- Sección de Ejemplos Explicativos --- */
.examples-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  margin-top: 1rem;
}
@media (min-width: 640px) {
  .examples-grid {
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 280px), 1fr));
    gap: 2rem;
  }
}

.example-item {
  display: flex;
  flex-direction: column; /* Apilar elementos verticalmente */
  gap: 1rem;
  align-items: center;
  text-align: center;
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.example-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.12);
}

.example-image {
  width: 100%; /* Ocupa el 100% del item */
  max-width: 300px; /* Máximo ancho de imagen */
  height: 200px; /* Altura fija */
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.example-text h3 {
  margin: 0 0 0.5rem 0; /* Más espacio debajo del título */
  font-size: 1.3rem;
  color: #b22222;
}

.example-text p {
  margin: 0;
  font-size: 1rem;
  line-height: 1.6;
  color: #666;
}

/* --- Animaciones Keyframes --- */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInScale {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* --- Media Queries para Responsividad --- */
@media (max-width: 768px) {
  .hero-text {
    font-size: 1rem;
  }
  .classes-description-container {
    grid-template-columns: 1fr; /* Una columna en móvil */
  }
  .demo-image-wrapper {
    padding: 1rem;
  }
  .tag-buttons {
    gap: 0.5rem;
  }
  .tag-buttons button {
    padding: 0.6rem 1rem;
    font-size: 0.9rem;
  }
  .examples-grid {
    grid-template-columns: 1fr; /* Una columna en móvil */
  }
  .example-image {
    width: 90%;
    height: auto;
  }
  .example-item {
    padding: 1rem;
  }
}
</style>