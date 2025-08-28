<template>
  <div class="w-full min-h-screen max-w-5xl mx-auto px-4 py-10 flex flex-col gap-16 font-poppins text-gray-800">

    <!-- Logo -->
    <div class="flex justify-center mb-4">
      <img src="/NeuroBerry_horizontal.png" alt="NeuroBerry Logo" class="w-11/12 max-w-md h-auto rounded-lg shadow" />
    </div>

    <!-- Hero Section -->
    <section class="flex flex-col gap-8 text-center">
      <h1 class="text-4xl font-extrabold text-[#b22222]">🍓 NeuroBerry - Madurez en frambuesas por IA</h1>
      <p class="text-lg leading-relaxed text-justify max-w-2xl mx-auto">
        Automatizamos la identificación del estado de madurez de frambuesas en una granja real mediante Visión por Computadora.
        Partimos de miles de imágenes etiquetadas con Label Studio en 5 clases (DarkRed, Cherry Red, Orange Dot, Green y Button) para entrenar un modelo que detecta y clasifica los frutos.
        <br><br><strong>El objetivo:</strong> optimizar cosecha, calidad y trazabilidad, reduciendo costos de mano de obra y variabilidad humana.
      </p>
    </section>

    <!-- Research Section -->
    <section class="flex flex-col gap-8">
      <h2 class="text-3xl font-extrabold text-[#b22222] text-center">Investigación y Desarrollo</h2>
      <div class="flex flex-col md:flex-row items-center justify-between gap-8">
        <div class="flex-1 min-w-[250px] text-justify text-lg leading-relaxed">
          <strong>Dataset propio en campo:</strong> capturamos imágenes en diferentes horas del día, invernaderos y ángulos.
          <br><br><strong>Etiquetado con Label Studio:</strong> anotamos miles de instancias en 5 clases estandarizadas.
          <br><br><strong>Modelo de IA:</strong> red de detección (p. ej., tipo YOLO) para localizar y clasificar cada fruto.
          <br><br><strong>Bucle de mejora continua:</strong> activo-aprendizaje (active learning), re-etiquetado selectivo y reentrenamiento periódico.
        </div>
        <div class="flex-1 min-w-[250px] flex justify-center">
          <img src="/frambuesas_1.jpg" alt="Investigación" class="w-full max-w-xs rounded-lg shadow-md" />
        </div>
      </div>
    </section>

    <!-- Process Section -->
    <section class="flex flex-col gap-8">
      <h2 class="text-3xl font-extrabold text-[#b22222] text-center">Nuestro Proceso</h2>
      <div class="flex flex-col md:flex-row-reverse items-center justify-between gap-8">
        <div class="flex-1 min-w-[250px] flex justify-center">
          <img src="/frambuesas_2.png" alt="Proceso" class="w-full max-w-xs rounded-lg shadow-md" />
        </div>
        <div class="flex-1 min-w-[250px] text-justify text-lg leading-relaxed">
          <strong>Dataset propio en campo:</strong> capturamos imágenes en diferentes horas del día, invernaderos y ángulos.
          <br><br><strong>Etiquetado con Label Studio:</strong> anotamos miles de instancias en 5 clases estandarizadas.
          <br><br><strong>Modelo de IA:</strong> red de detección (YOLO) para localizar y clasificar cada fruto.
          <br><br><strong>Bucle de mejora continua:</strong> activo-aprendizaje, re-etiquetado selectivo y reentrenamiento periódico.
        </div>
      </div>
    </section>

    <!-- Results Section -->
    <section class="flex flex-col gap-8">
      <h2 class="text-3xl font-extrabold text-[#b22222] text-center">Resultados y Beneficios</h2>
      <div class="flex flex-wrap justify-center gap-6">
        <div class="bg-white rounded-xl p-6 w-60 shadow-md hover:shadow-lg hover:-translate-y-1 transition-all">
          <h3 class="text-[#b22222] mb-2 text-xl font-semibold">Optimización</h3>
          <p>Optimizar la identificación del estado de madurez de frambuesas en una granja real</p>
        </div>
        <div class="bg-white rounded-xl p-6 w-60 shadow-md hover:shadow-lg hover:-translate-y-1 transition-all">
          <h3 class="text-[#b22222] mb-2 text-xl font-semibold">Sostenibilidad</h3>
          <p>Reducción de costos de mano de obra y variabilidad humana.</p>
        </div>
        <div class="bg-white rounded-xl p-6 w-60 shadow-md hover:shadow-lg hover:-translate-y-1 transition-all">
          <h3 class="text-[#b22222] mb-2 text-xl font-semibold">Progresivo</h3>
          <p>Mejora continua del modelo a través de activo-aprendizaje y reentrenamiento.</p>
        </div>
      </div>
    </section>

    <!-- Diagram Section -->
    <section class="flex flex-col gap-6">
      <h2 class="text-3xl font-extrabold text-[#b22222] text-center">Diagrama de Bloques</h2>
      <div class="flex justify-center items-center bg-white rounded-xl shadow-md p-4 md:p-8">
        <img src="/diagrama_bloques.png" alt="Diagrama de bloques" class="w-full max-w-2xl rounded-lg object-contain" />
      </div>
    </section>

  </div>
</template>

<script setup></script>
