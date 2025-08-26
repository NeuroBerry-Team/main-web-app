<template>
  <div class="page-wrapper">

    <div class="logo-wrapper">
      <img src="/NeuroBerry_horizontal.png" alt="NeuroBerry Logo" class="logo-image" />
    </div>

    <section class="hero-section">
      <h1 class="section-title">Etiquetado Demo</h1>
      <p class="justify-text big-paragraph">
        Esta demostración simula el proceso de etiquetado de frambuesas para entrenar la IA. Puedes seleccionar una etiqueta y dibujar un cuadro sobre la imagen para ver cómo se haría en la práctica.
      </p>
    </section>

    <section class="tagging-demo">
      <h2 class="section-title">Generación de la Base de Datos</h2>

      <div class="classes-container">
        <div v-for="label in labels" :key="label.name" class="class-item">
          <div class="color-box" :style="{backgroundColor: label.color}"></div>
          <p class="class-text">
            <strong>{{ label.name }}</strong>: {{ label.description }}
          </p>
        </div>
      </div>

      <div class="demo-container" ref="imageContainer">
        <img 
          ref="demoImage" 
          src="/etiquetado_1.jpg" 
          alt="Frambuesa Ejemplo" 
          class="demo-image"
          @click="createBox($event)"
        />

        <div class="tag-buttons">
          <button 
            v-for="label in labels" 
            :key="label.name" 
            :style="{backgroundColor: label.color}" 
            @click="selectLabel(label.name)"
          >
            {{ label.name }}
          </button>
        </div>

        <p v-if="selectedLabel" class="selected-message">
          <br>Etiqueta seleccionada: <strong>{{ selectedLabel }}</strong><br></br>
        </p>

        <div 
          v-for="(box, index) in boxes" 
          :key="index" 
          class="tag-box" 
          :style="{top: box.top + 'px', left: box.left + 'px', borderColor: box.color}"
        >
          {{ box.label }}
        </div>
      </div>
    </section>

    <section class="examples-section">
      <h2 class="section-title">Ejemplos Explicativos</h2>

      <div class="examples-container">
        <div v-for="(example, index) in examples" :key="index" class="example-item">
          <img :src="example.image" alt="Ejemplo Imagen" class="example-image" />
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
  { name: 'Button', color: '#008000', description: 'Marcador especial para referencia o prueba.' }
]

const selectedLabel = ref('')
const boxes = ref([])

function selectLabel(label) {
  selectedLabel.value = label
}

function createBox(event) {
  if (!selectedLabel.value) return

  const containerRect = imageContainer.value.getBoundingClientRect()

  const top = event.clientY - containerRect.top
  const left = event.clientX - containerRect.left

  const color = labels.find(l => l.name === selectedLabel.value)?.color || '#000'

  boxes.value.push({
    top: top - 15,   
    left: left - 30,
    label: selectedLabel.value,
    color
  })
}

const examples = [
  { image: 'fram/fram2.png', title: 'Frambuesa muy roja', description: 'Frambuesa muy roja, en su punto máximo de maduración.' },
  { image: 'fram/fram1.png', title: 'Frambuesa Roja', description: 'Frambuesa roja, lista para consumo.' },
  { image: 'fram/fram3.png', title: 'Frambuesa con punto rojo', description: 'Frambuesa con puntos naranjas o rojos, en transición de maduración.' },
  { image: 'fram/fram4.png', title: 'Frambuesa verde', description: 'Frambuesa verde, aún inmadura.' },
  { image: 'fram/fram5.png', title: 'Botón', description: 'Botón de referencia.' }
]
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
  gap: 4rem;
  text-align: center;
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

section {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.section-title {
  font-size: 2rem;
  font-weight: 800;
  color: #b22222;
}

.justify-text {
  text-align: justify;
}

.big-paragraph {
  font-size: 1.1rem;
  line-height: 1.8;
}

.classes-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin: 1rem 0;
  align-items: flex-start;
}

.class-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.color-box {
  width: 30px;
  height: 30px;
  border-radius: 6px;
  border: 2px solid #333;
}

.class-text {
  font-size: 1rem;
  text-align: left;
}

.tagging-demo {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  align-items: center;
}

.demo-container {
  position: relative;
  display: inline-block;
  width: 600px;
  height: 400px;
}

.demo-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 10px;
  cursor: crosshair;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.tag-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
}

.tag-buttons button {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  color: white;
  border: none;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tag-buttons button:hover {
  transform: scale(1.05);
}

.selected-message {
  font-size: 1rem;
  color: #b22222;
  font-weight: 700;
}

.tag-box {
  position: absolute;
  width: 60px;
  height: 30px;
  border: 2px solid;
  border-radius: 5px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 0.8rem;
  font-weight: 700;
  background-color: rgba(255,255,255,0.3);
}

.examples-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  align-items: flex-start;
}

.example-item {
  display: flex;
  gap: 1rem;
  align-items: center;
  text-align: left;
}

.example-image {
  width: 150px;
  height: 100px;
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.example-text h3 {
  margin: 0 0 0.3rem 0;
  font-size: 1.1rem;
  color: #b22222;
}

.example-text p {
  margin: 0;
  font-size: 0.95rem;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .demo-container {
    width: 90%;
    height: 300px; 
  }

  .example-item {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .example-image {
    width: 90%;
    height: auto;
  }
}
</style>