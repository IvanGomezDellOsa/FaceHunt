# FaceHunt

FaceHunt es una herramienta de análisis de video basada en deep learning que identifica todas las apariciones de una persona. Solo necesitas subir una foto de referencia y un video (local o de YouTube) para obtener una lista precisa de los momentos exactos en que aparece la persona.


## Estado del Proyecto

FaceHunt ahora incluye una interfaz web moderna además de la aplicación de escritorio original. Ambas versiones están completamente funcionales.

La versión web es ideal para probar FaceHunt como demo, ya que no requiere instalación ni configuración local. Sin embargo, al ejecutarse en servidores públicos, los tiempos de procesamiento son mayores en comparación con la versión local.

<p align="center">
  <a href="https://huggingface.co/spaces/IvanGomezDellOsa/FaceHunt" target="_blank">
    <img src="https://raw.githubusercontent.com/IvanGomezDellOsa/assets/main/facehunt_web_button.svg" 
         alt="👉 Click para probar FaceHunt Web" width="280">
  </a>
</p>


## ✨ Características

- 🌐 **Interfaz Web Moderna**
    - Una UI limpia, responsiva y guiada por pasos que funciona en cualquier navegador moderno.

- 🎯 **Reconocimiento Facial Preciso**
    - Utiliza la librería `DeepFace` con el modelo `FaceNet` para una alta precisión en la identificación de rostros.

- 📹 **Fuentes de Video Flexibles**
    - Soporte nativo tanto para URLs de YouTube como para la subida de archivos de video locales (MP4, AVI, MOV, MKV, WebM).

- ⚡ **Dos Modos de Procesamiento**
    - Permite al usuario elegir el balance perfecto entre velocidad y exactitud para cada análisis.
        - **Alta Precisión:** Usa el detector `RetinaFace` para máxima calidad.
        - **Equilibrado:** Usa el detector `MTCNN` para un análisis más rápido (igualmente extremadamente preciso).

- 🔍 **Múltiples Backends de Detección**
    - Soporte para `RetinaFace`, `MTCNN` y `OpenCV`.

- 🛰️ **API RESTful Robusta**
    - Un backend impulsado por `FastAPI` que expone toda la lógica de negocio de forma segura y eficiente.    

- 🖥️ **GUI de Escritorio (Legado)**
    - Construida con `Tkinter`.


#### Uso:

1. **Paso 1:** Sube una imagen de referencia (debe contener exactamente una cara)
2. **Paso 2:** Selecciona un video (archivo local o URL de YouTube)
3. **Paso 3:** Elige el modo de procesamiento (Equilibrado o Alta Precisión)
4. **Paso 4:** Revisa los resultados. Si hay coincidencias muestra timestamps de los momentos exactos donde aparece la cara de referencia en el video. 


## Probar FaceHunt

### Opción 1: Ejecutar con Docker (Recomendado)
Esta es la forma más rápida de probar la aplicación sin instalar nada más que Docker. Docker la descargará automáticamente desde Docker Hub.

1. **Ejecuta el contenedor:**
   Abre una terminal y ejecuta el siguiente comando:  
   ```bash
   docker run -it --rm -p 7860:7860 ivangomezdellosa/facehunt
   ```

2. **Abre la aplicación:**  
   Ve a tu navegador y abre la siguiente dirección:  
   ```
   http://localhost:7860
   ```

### Opción 2: Ejecutar Localmente
Esta opción es ideal para desarrolladores que quieran explorar el código fuente y entender cómo funciona la aplicación.

1. **Clona el repositorio:**  
   ```bash
   git clone https://github.com/IvanGomezDellOsa/FaceHunt.git
   cd FaceHunt
   ```

2. **Crea y activa un entorno virtual:**  
   ```bash
   # Crea el entorno
   python -m venv .venv

   # Activa en Windows (PowerShell)
   .venv\Scripts\Activate.ps1

   # Activa en macOS/Linux
   source .venv/bin/activate
   ```

3. **Instala las dependencias:**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Inicia el servidor:**  
   Este único comando iniciará tanto el backend (API) como el frontend (interfaz web).  
   ```bash
   python api_server.py
   ```

5. **Abre la aplicación:**  
   Ve a tu navegador y abre la siguiente dirección:  
   ```
   http://localhost:7860
   ```

---

**Nota para desarrolladores:** La documentación de la API estará disponible automáticamente en `http://localhost:7860/docs`.


<details>
<summary>🗄️ Instrucciones para la GUI de Escritorio (Tkinter)</summary>

Decidí conservar el código de la versión de escritorio original para no eliminar esa opción y para que sirva como registro de la evolución del proyecto. Esta versión fue construida con Tkinter.

### Ejecutar la GUI Localmente (Sin Docker)

Para ejecutar la antigua interfaz gráfica, primero sigue los pasos de la [Opción 2: Ejecutar Localmente](#opcion-2-ejecutar-localmente) de la guía principal para clonar el proyecto e instalar las dependencias en un entorno virtual.

Una vez que tengas todo instalado, simplemente ejecuta el siguiente comando:

```bash
python main.py
```

**Nota Importante:** Esta versión ya no está en desarrollo activo. Las antiguas instrucciones para ejecutar esta GUI dentro de un contenedor Docker con un servidor X (como VcXsrv) ya no son compatibles con el Dockerfile actual, que está diseñado exclusivamente para la aplicación web.

</details>


<details>
<summary>🏛️ Arquitectura y Módulos Principales</summary>

#### `fh_core.py`
- **Propósito:** Coordina el flujo completo de procesamiento
- **Funciones clave:**
  - `validate_image_file()`: Valida imagen y extrae embedding facial
  - `validate_video_source()`: Verifica accesibilidad del video
  - `execute_workflow()`: Orquesta la validación, extracción y reconocimiento, devolviendo los resultados de coincidencia facial.

#### `fh_downloader.py`
- **Propósito:** Descarga videos de YouTube
- **Tecnología:** yt-dlp
- **Formato:** MP4 a 480p máximo
- **Validaciones:** Espacio en disco, duplicados
- **Destino:** Carpeta temporal gestionada automáticamente por el sistema.

#### `fh_frame_extractor.py`
- **Propósito:** Extrae frames del video
- **Modos:**
  - Alta Precisión: 1 frame cada 0.25s (RetinaFace)
  - Equilibrado: 1 frame cada 0.5s (MTCNN)
- **Optimización:** Generador de frames por lotes para reducir uso de memoria en videos largos.

#### `fh_face_recognizer.py`
- **Propósito:** Detecta y compara rostros
- **Modelo:** FaceNet (128-d embeddings)
- **Métrica:** Distancia coseno (match si ≤ 0.32)
- **Detectores disponibles:**
  - RetinaFace (alta precisión, lento)
  - MTCNN (equilibrado)
  - OpenCV (rápido, baja precisión)

</details>

### 🧾 Aclaración de Responsabilidades

El objetivo de este proyecto fue demostrar habilidades en **Python**, abarcando arquitectura de software, procesamiento de video, integración de modelos con Machine Learning y optimización de recursos.  
Por transparencia, aclaro en qué partes intervino la inteligencia artificial y en cuáles no. Fue utilizada con un propósito definido como herramienta de apoyo, y no como protagonista ni orquestadora del desarrollo.

- **Lógica (Python):** Desarrollo completamente propio. Con un enfoque minucioso en la optimización, simplificación y limpieza del código, eliminando redundancias, corrigiendo validaciones fallidas, mejorando los tiempos de ejecución y asegurando un flujo coherente entre módulos.  
- **Frontend (HTML/CSS/JS)** Aunque tengo experiencia en estas tecnologías, este componente no era el foco del desafío. Decidí delegar el diseño web a una IA (v0), reconociendo que podía generar una interfaz limpia y más estética en menos tiempo. Esto me permitió no desviar el objetivo del proyecto y centrarme 100% en el backend.  
- **Arquitectura de la API (FastAPI):** Como estoy en proceso de aprendizaje de FastAPI, utilicé la IA para generar la sintaxis básica. Mi trabajo se centró en el diseño de la arquitectura lógica. Esto implicó rechazar activamente las arquitecturas ineficientes propuestas por la IA (que duplicaban código, dividían responsabilidades y sacrificaban la optimización) y, en su lugar, diseñar e implementar un flujo de datos limpio y completamente optimizado. Este rediseño fue fundamental para asegurar que la API se comunique eficientemente con el núcleo de Python.
- **Documentación (README y Docstrings):** La redacción fue realizada casi en su totalidad por IA. Posteriormente, el contenido fue editado y refinado manualmente por mí para garantizar la precisión técnica y reflejar fielmente las decisiones de arquitectura tomadas.  

## 👤 Autor

**Ivan Gomez Dell'Osa**

- GitHub: https://github.com/IvanGomezDellOsa/FaceHunt
- Email: ivangomezdellosa@gmail.com
- Linkedin: https://www.linkedin.com/in/ivangomezdellosa/
---
