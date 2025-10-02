<template>
  <div class="page-wrapper">
    <section class="hero-section">
      <h1 class="hero-title animated-item" style="animation-delay: 0.1s;">Módulo II: Sistemas Inteligentes</h1>
      <p class="hero-text animated-item" style="animation-delay: 0.2s;">
        El núcleo de NeuroBerry: una Inteligencia Artificial entrenada para ver y entender la madurez de las frambuesas como un experto.
      </p>
    </section>

    <div class="content-grid">
      <div 
        v-for="card in cards" 
        :key="card.title"
        class="content-section animated-item" 
        :style="{ animationDelay: card.animationDelay }"
        @click="openModal(card)"
      >
        <div class="icon-wrapper">
          <div class="section-icon">{{ card.icon }}</div>
        </div>
        <h2 class="section-title">{{ card.title }}</h2>
        <div class="section-text" v-html="card.text"></div>
      </div>
    </div>

    <div v-if="selectedCard" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <button class="modal-close-button" @click="closeModal">&times;</button>
        <div class="icon-wrapper">
          <div class="section-icon">{{ selectedCard.icon }}</div>
        </div>
        <h2 class="section-title">{{ selectedCard.title }}</h2>
        <div class="section-text" v-html="selectedCard.text"></div>
      </div>
    </div>

    <section class="map-section animated-item" style="animation-delay: 0.6s;">
      <h2 class="map-title">📍 Origen de los Datos: Jalisco</h2>
      <p class="map-text">
        Nuestro modelo fue entrenado con datos recolectados directamente de los campos de esta región, asegurando que la IA aprenda de las condiciones del mundo real para ofrecer resultados precisos y confiables.
      </p>
      <div class="map-container">
        <iframe 
          src="https://www.google.com/maps/embed?pb=!1m13!1m8!1m3!1d48010.058458001025!2d-103.4436237!3d20.2593632!3m2!1i1024!2i768!4f13.1!3m2!1m1!2zMjDCsDE2JzA5LjUiTiAxMDPCsDI2JzU1LjgiVw!5e1!3m2!1ses-419!2smx!4v1759366268179!5m2!1ses-419!2smx" 
          width="600" 
          height="450" 
          style="border:0;" 
          allowfullscreen="" 
          loading="lazy" 
          referrerpolicy="no-referrer-when-downgrade">
        </iframe>
      </div>
    </section>

  </div>
</template>

<script setup>
// SCRIPT (No changes)
import { ref } from 'vue';

const selectedCard = ref(null);
const cards = ref([
  {
    icon: '🧠',
    title: '¿Por qué YOLOv8?',
    text: `
      Se eligió <strong>YOLOv8</strong> (You Only Look Once) por ser un modelo de vanguardia que ofrece un balance perfecto para una aplicación real en el campo:
      <ul>
        <li><strong>Detección en Tiempo Real:</strong> Es extremadamente rápido, permitiendo analizar imágenes casi instantáneamente.</li>
        <li><strong>Alta Precisión:</strong> Posee una gran capacidad para identificar objetos pequeños y superpuestos, como las frambuesas en una planta.</li>
        <li><strong>Eficiencia:</strong> Requiere menos recursos computacionales que otros modelos, lo que lo hace más accesible y escalable.</li>
      </ul>
    `,
    animationDelay: '0.3s'
  },
  {
    icon: '📸',
    title: 'Un Dataset Creado en Campo',
    text: `
      La precisión de la IA depende de la calidad de los datos con los que aprende. Por eso, creamos un dataset único:
      <ul>
        <li>Se capturaron <strong>más de 3,000 imágenes</strong> directamente en campos de cultivo de Jocotepec, Jalisco.</li>
        <li>Se utilizó la herramienta <strong>Label Studio</strong> para etiquetar manualmente las frambuesas en 5 clases de madurez (de C1 a C5).</li>
        <li>El resultado es un modelo entrenado para las condiciones reales de iluminación, sombras y variabilidad que se encuentran en un cultivo.</li>
      </ul>
    `,
    animationDelay: '0.4s'
  },
  {
    icon: '🎯',
    title: 'Enseñando a la IA a Ver',
    text: `
      El proceso se basa en <strong>aprendizaje supervisado</strong>. Cada una de las miles de imágenes etiquetadas actúa como un ejemplo para el modelo, enseñándole a asociar patrones visuales (color, textura, forma) con una clase de madurez. El entrenamiento se realizó usando aceleración por GPU (CUDA) y se probaron múltiples versiones hasta encontrar la más precisa y robusta.
    `,
    animationDelay: '0.5s'
  }
]);

const openModal = (card) => { selectedCard.value = card; };
const closeModal = () => { selectedCard.value = null; };
</script>

<style scoped>
/* STYLES (Existing styles + new styles for map section) */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');

.page-wrapper {
  width: 100%;
  min-height: 100vh;
  padding: 2rem;
  padding-top: 7rem;
  font-family: 'Poppins', sans-serif;
  color: #333;
  background-color: #ffffff;
}
.hero-section {
  max-width: 1200px;
  margin: 0 auto 4rem auto;
  padding: 4rem 2rem;
  border-radius: 20px;
  text-align: center;
  background: linear-gradient(135deg, #e52d27, #b31217);
  color: white;
  box-shadow: 0 10px 40px rgba(185, 28, 28, 0.25);
}
.hero-title { font-size: 2.8rem; font-weight: 800; text-shadow: 0 3px 6px rgba(0,0,0,0.2); }
.hero-text { color: rgba(255, 255, 255, 0.9); font-size: 1.2rem; margin-top: 1.5rem; max-width: 800px; margin-left: auto; margin-right: auto; line-height: 1.6; }
.content-grid {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 2.5rem;
}
.content-section {
  background-color: #ffffff;
  border-radius: 18px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.07);
  padding: 2.5rem;
  text-align: center;
  border: 1px solid #e5e7eb;
  border-bottom: 4px solid transparent;
  transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
  display: flex;
  flex-direction: column;
  cursor: pointer;
}
.content-section:hover {
  transform: translateY(-12px);
  box-shadow: 0 20px 40px -5px rgba(0,0,0,0.12);
  border-bottom-color: #c31432;
}
.icon-wrapper {
  margin: 0 auto 1.5rem auto;
  background: linear-gradient(135deg, #e52d27, #b31217);
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 5px 15px rgba(195, 20, 50, 0.4);
  animation: pulse 2.5s infinite cubic-bezier(0.4, 0, 0.6, 1);
  flex-shrink: 0;
}
.section-icon { font-size: 2.5rem; color: white; }
.section-title { font-size: 1.5rem; font-weight: 700; color: #b91c1c; margin-bottom: 1rem; }
.section-text { font-size: 1rem; line-height: 1.7; color: #555; flex-grow: 1; text-align: left;}
.section-text:deep(strong) { color: #c31432; font-weight: 600; }
.section-text:deep(ul) { list-style-position: inside; padding-left: 1rem; margin-top: 1rem; }
.section-text:deep(li) { margin-bottom: 0.5rem; }
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(5px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}
.modal-content {
  background: #ffffff;
  padding: 3rem;
  border-radius: 20px;
  max-width: 650px;
  width: 90%;
  text-align: center;
  position: relative;
  box-shadow: 0 10px 50px rgba(0,0,0,0.3);
  animation: scaleIn 0.3s ease;
}
.modal-close-button {
  position: absolute;
  top: 15px;
  right: 20px;
  background: none;
  border: none;
  font-size: 2.5rem;
  color: #aaa;
  cursor: pointer;
  line-height: 1;
  transition: color 0.2s ease;
}
.modal-close-button:hover { color: #333; }
.modal-content .section-title { font-size: 1.8rem; }
.modal-content .section-text { font-size: 1.1rem; line-height: 1.8; }
.animated-item { opacity: 0; animation: fadeInUp 0.7s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards; }

/* --- NEW MAP STYLES --- */
.map-section {
  max-width: 1200px;
  margin: 4rem auto 2rem auto; /* Add margin top and bottom */
  padding: 2.5rem;
  background-color: #ffffff;
  border-radius: 20px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.07);
  border: 1px solid #e5e7eb;
  text-align: center;
}
.map-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: #b91c1c;
  margin-bottom: 1rem;
}
.map-text {
  font-size: 1.1rem;
  color: #555;
  max-width: 800px;
  margin: 0 auto 2rem auto;
  line-height: 1.7;
}
.map-container {
  position: relative;
  width: 100%;
  padding-top: 56.25%; /* 16:9 Aspect Ratio */
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}
.map-container iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: 0;
}


/* --- KEYFRAMES --- */
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
@keyframes pulse { 0% { transform: scale(1); box-shadow: 0 5px 15px rgba(195, 20, 50, 0.4); } 50% { transform: scale(1.05); box-shadow: 0 8px 25px rgba(195, 20, 50, 0.6); } 100% { transform: scale(1); box-shadow: 0 5px 15px rgba(195, 20, 50, 0.4); } }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes scaleIn { from { opacity: 0; transform: scale(0.9); } to { opacity: 1; transform: scale(1); } }

/* --- MEDIA QUERIES --- */
@media (max-width: 768px) {
  .hero-title { font-size: 2.2rem; }
  .hero-text { font-size: 1.1rem; }
  .modal-content { padding: 2rem; }
  .modal-content .section-title { font-size: 1.5rem; }
  .modal-content .section-text { font-size: 1rem; }
  .map-title { font-size: 1.5rem; }
  .map-text { font-size: 1rem; }
}
</style>