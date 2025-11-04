<template>
  <div class="page-wrapper">

    <div class="logo-wrapper">
      <img src="/NeuroBerry_horizontal.png" alt="NeuroBerry Logo" class="logo-image" />
    </div>

    <section class="hero-section animated-section">
      <h1 class="section-title">Nuestra Base de Datos</h1>
      <p class="justify-text">
        Hemos recolectado un total de <strong>3000 imágenes de frambuesas</strong>, capturadas en condiciones reales de cultivo: 
        distintos ángulos, iluminación, ambientes de invernadero y campo abierto.  
        <br><br>
        Estas imágenes están organizadas en <strong>5 clases principales</strong> que corresponden al estado de madurez del fruto.  
        Este dataset constituye la base para entrenar nuestro modelo de IA y lograr una clasificación robusta y precisa.
      </p>
    </section>

    <section class="research-section animated-section" style="animation-delay: 0.2s;">
      <h2 class="section-title">Ejemplo de galería</h2>
      <div class="gallery">
        <div 
          class="gallery-item" 
          v-for="i in 16" 
          :key="i" 
          @click="openPreview(`/data/database${i}.jpeg`)"
        >
          <img :src="`/data/database${i}.jpeg`" :alt="`Ejemplo ${i}`" class="gallery-image" />
        </div>

        <div class="gallery-item" @click="openPreview('/data/database1.jpeg')">
          <img src="/data/database1.jpeg" alt="Ejemplo repetido 1" class="gallery-image" />
        </div>
        <div class="gallery-item" @click="openPreview('/data/database2.jpeg')">
          <img src="/data/database2.jpeg" alt="Ejemplo repetido 2" class="gallery-image" />
        </div>
      </div>
    </section>

    <section class="reference-section animated-section" style="animation-delay: 0.4s;">
      <h2 class="section-title">Ejemplo de Etiquetado</h2>
      <img src="/data/database1.jpeg" alt="Ejemplo etiquetado" class="reference-image" />

      <div class="labels">
        <div class="label-item">
          <div class="color-box darkred"></div>
          <span><b>Rojo Fuerte</b> - Frambuesa muy madura</span>
        </div>
        <div class="label-item">
          <div class="color-box cherryred"></div>
          <span><b>Rojo Cherry</b> - Frambuesa madura perfecta para consumo</span>
        </div>
        <div class="label-item">
          <div class="color-box orange"></div>
          <span><b>Naranja</b> - Frambuesa con punto rojo, en maduración</span>
        </div>
        <div class="label-item">
          <div class="color-box greenyellow"></div>
          <span><b>Verde amarilloso</b> - Frambuesa verde, aún inmadura</span>
        </div>
        <div class="label-item">
          <div class="color-box green"></div>
          <span><b>Verde fuerte</b> - Botón</span>
        </div>
      </div>
    </section>

    <div v-if="previewImage" class="modal" @click="closePreview">
      <img :src="previewImage" alt="Vista previa" class="modal-content" />
    </div>

  </div>
</template>

<script setup>
import { ref } from "vue";

const previewImage = ref(null);

const openPreview = (imgPath) => {
  previewImage.value = imgPath;
};

const closePreview = () => {
  previewImage.value = null;
};
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
}

/* --- Estilos para la animación --- */
.animated-section {
  opacity: 0; /* Empieza invisible */
  animation: fadeInUp 0.8s ease-out forwards; /* 'forwards' mantiene el estado final */
}

.section-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: #b22222;
  word-wrap: break-word;
  overflow-wrap: break-word;
}
@media (min-width: 640px) {
  .section-title {
    font-size: 1.8rem;
  }
}
@media (min-width: 768px) {
  .section-title {
    font-size: 2rem;
  }
}

.justify-text {
  max-width: 900px;
  margin: 0 auto;
  text-align: justify;
  font-size: 1rem;
  line-height: 1.8;
  color: #555;
  word-wrap: break-word;
  overflow-wrap: break-word;
}
@media (min-width: 768px) {
  .justify-text {
    font-size: 1.2rem;
  }
}

.gallery {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  margin-top: 2rem;
}
@media (min-width: 640px) {
  .gallery {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.25rem;
  }
}
@media (min-width: 768px) {
  .gallery {
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
  }
}

.gallery-item {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  background-color: #fff;
  height: 200px;
  font-size: 1rem;
  color: #888;
  cursor: pointer;
  
  /* Animación para cada item */
  opacity: 0;
  animation: fadeInUp 0.5s ease-out forwards;
}

/* --- Retraso en cascada para los items de la galería --- */
.gallery-item:nth-child(1) { animation-delay: 0.1s; }
.gallery-item:nth-child(2) { animation-delay: 0.2s; }
.gallery-item:nth-child(3) { animation-delay: 0.3s; }
.gallery-item:nth-child(4) { animation-delay: 0.4s; }
.gallery-item:nth-child(5) { animation-delay: 0.5s; }
.gallery-item:nth-child(6) { animation-delay: 0.6s; }
/* ... puedes continuar para el resto si lo deseas */


.gallery-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.15);
}

.gallery-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 12px;
}

.reference-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
}

.reference-image {
  width: 80%;
  max-width: 800px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.labels {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  text-align: left;
}

.label-item {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  font-size: 0.95rem;
  word-wrap: break-word;
  overflow-wrap: break-word;
}
@media (min-width: 768px) {
  .label-item {
    font-size: 1.1rem;
  }
}

.color-box {
  width: 22px;
  height: 22px;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}

.darkred { background-color: #8B0000; }
.cherryred { background-color: #FF0000; }
.orange { background-color: #FFA500; }
.greenyellow { background-color: #9ACD32; }
.green { background-color: #006400; }

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 1000;
}

.modal-content {
  max-width: 90%;
  max-height: 90%;
  border-radius: 12px;
}

/* Keyframes para la animación de entrada */
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

@media (max-width: 768px) {
  .gallery {
    grid-template-columns: repeat(2, 1fr);
  }
  .justify-text {
    font-size: 1rem;
  }
  .reference-image {
    width: 100%;
  }
}
</style>