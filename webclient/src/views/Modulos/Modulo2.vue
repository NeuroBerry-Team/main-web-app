<template>
  <div class="page-wrapper">
    <section class="hero-section animated-item">
      <h1 class="hero-title">Módulo II: Sistemas Inteligentes</h1>
      <p class="hero-text">
        El núcleo de NeuroBerry: una Inteligencia Artificial entrenada para ver y entender la madurez de las frambuesas como un experto.
      </p>
    </section>

    <div class="content-grid">
      <div class="content-section animated-item" style="animation-delay: 0.1s;">
        <div class="section-icon">🧠</div>
        <h2 class="section-title">¿Por qué YOLOv8?</h2>
        <p class="section-text">
          Se eligió **YOLOv8** (You Only Look Once) por ser un modelo de vanguardia que ofrece un balance perfecto para una aplicación real en el campo:
          <ul>
            <li><strong>Detección en Tiempo Real:</strong> Es extremadamente rápido, permitiendo analizar imágenes casi instantáneamente.</li>
            <li><strong>Alta Precisión:</strong> Posee una gran capacidad para identificar objetos pequeños y superpuestos, como las frambuesas en una planta.</li>
            <li><strong>Eficiencia:</strong> Requiere menos recursos computacionales que otros modelos, lo que lo hace más accesible y escalable.</li>
          </ul>
        </p>
        
      </div>

      <div class="content-section animated-item" style="animation-delay: 0.2s;">
        <div class="section-icon">📸</div>
        <h2 class="section-title">Un Dataset Creado en Campo</h2>
        <p class="section-text">
          La precisión de la IA depende de la calidad de los datos con los que aprende. Por eso, creamos un dataset único:
          <ul>
            <li>Se capturaron **más de 3,000 imágenes** directamente en campos de cultivo de Jocotepec, Jalisco.</li>
            <li>Se utilizó la herramienta **Label Studio** para etiquetar manualmente las frambuesas en 5 clases de madurez (de C1 a C5).</li>
            <li>El resultado es un modelo entrenado para las condiciones reales de iluminación, sombras y variabilidad que se encuentran en un cultivo.</li>
          </ul>
        </p>
        
      </div>
      
      <div class="content-section animated-item" style="animation-delay: 0.3s;">
        <div class="section-icon">🎯</div>
        <h2 class="section-title">Enseñando a la IA a Ver</h2>
        <p class="section-text">
          El proceso se basa en **aprendizaje supervisado**. Cada una de las miles de imágenes etiquetadas actúa como un ejemplo para el modelo, enseñándole a asociar patrones visuales (color, textura, forma) con una clase de madurez. El entrenamiento se realizó usando aceleración por GPU (CUDA) y se probaron múltiples versiones hasta encontrar la más precisa y robusta.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
/* Estilos idénticos al Módulo 1 para consistencia */
.page-wrapper {
  width: 100%;
  min-height: 100vh;
  padding: 2rem;
  padding-top: 7rem;
  font-family: 'Poppins', sans-serif;
  color: #333;
  background-color: #fff;
}
.hero-section {
  max-width: 1200px;
  margin: 0 auto 3rem auto;
  background: linear-gradient(45deg, #b91c1c, #7f1d1d);
  color: white;
  padding: 3rem;
  border-radius: 16px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(185, 28, 28, 0.25);
}
.hero-title {
  font-size: 2.5rem;
  font-weight: 800;
  text-shadow: 0 2px 4px rgba(0,0,0,0.2);
}
.hero-text {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.2rem;
  margin-top: 1rem;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}
.content-grid {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 2rem;
}
.content-section {
  background-color: #fff;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.07);
  padding: 2.5rem;
  text-align: center;
  border: 1px solid #e5e7eb;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  display: flex;
  flex-direction: column;
}
.content-section:hover {
  transform: translateY(-8px);
  box-shadow: 0 15px 30px -5px rgba(0,0,0,0.1);
}
.section-icon {
  font-size: 3rem;
  margin-bottom: 1.5rem;
}
.section-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #b22222;
  margin-bottom: 1rem;
}
.section-text {
  font-size: 1rem;
  line-height: 1.7;
  color: #555;
  flex-grow: 1;
}
.section-text ul {
  text-align: left;
  list-style-position: inside;
  margin-top: 1rem;
}
.animated-item {
  opacity: 0;
  animation: fadeInUp 0.7s ease-out forwards;
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>