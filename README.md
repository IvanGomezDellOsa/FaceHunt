# FaceHunt

FaceHunt es una herramienta de análisis de video basada en deep learning que identifica todas las apariciones de una persona. Solo necesitas subir una foto de referencia y un video (local o de YouTube) para obtener una lista precisa de los momentos exactos en que aparece la persona.


## Estado del Proyecto

FaceHunt ahora incluye una interfaz web moderna además de la aplicación de escritorio original. Ambas versiones están completamente funcionales.


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


## Probar FaceHunt

### Opción 1: Ejecutar con Docker (Recomendado)
Esta es la forma más rápida de probar la aplicación sin instalar nada más que Docker.

1. **Construye la imagen de Docker:**  
   Desde la raíz de tu proyecto, ejecuta:  
   ```bash
   docker build -t facehunt-web .
   ```

2. **Ejecuta el contenedor:**  
   ```bash
   docker run -it --rm -p 8000:8000 facehunt-web
   ```

3. **Abre la aplicación:**  
   Ve a tu navegador y abre la siguiente dirección:  
   ```
   http://localhost:8000
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
   http://localhost:8000
   ```

---

**Nota para desarrolladores:** La documentación de la API estará disponible automáticamente en `http://localhost:8000/docs`.

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

#### Flujo de trabajo:

1. **Paso 1:** Sube una imagen de referencia (debe contener exactamente una cara)
2. **Paso 2:** Selecciona un video (archivo local o URL de YouTube)
3. **Paso 3:** Elige el modo de procesamiento (Equilibrado o Alta Precisión)
4. **Paso 4:** Revisa los resultados. Si hay coincidencias muestra timestamps de los momentos exactos donde aparece la cara de referencia en el video. 


### Módulos Principales

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


### 🧾 Aclaración de Responsabilidades

Con el fin de dejar claras las responsabilidades de cada parte (y no atribuirme tareas que no realicé), este proyecto fue desarrollado principalmente de forma manual, con el objetivo de garantizar un producto robusto y técnicamente sólido. La inteligencia artificial se utilizó únicamente como herramienta de apoyo en tareas puntuales, sin intervenir en la lógica central ni en la arquitectura del software.

- **Python:** Desarrollo completamente propio. Con un enfoque minucioso en la optimización, simplificación y limpieza del código, eliminando redundancias y asegurando un flujo coherente entre módulos.  
- **Docstrings y README:** Fueron redactados y formateados inicialmente por IA para darles estructura y estética profesional. Posteriormente los modifiqué manualmente en múltiples ocasiones para ajustar detalles técnicos, mejorar la precisión y reflejar fielmente el estado real del proyecto.  
- **HTML, CSS y JavaScript:** No fueron desarrollados por mí, ya que el objetivo de este proyecto fue demostrar habilidades técnicas en **Python** y **lógica de procesamiento**, no en diseño o front-end. La base fue generada por IA (v0) para agilizar la entrega del MVP, y mi participación se limitó a modificar descripciones, nombres de secciones y mensajes al usuario.  
- **FastAPI:** Todo el desarrollo de la API fue realizado manualmente por mí. La IA solo se utilizó para sugerir correcciones de sintaxis, pero **no intervino en la lógica ni en la arquitectura del software**. Al adaptar el proyecto de la versión Tkinter a la web, fue necesario **rediseñar completamente el flujo del programa** para que la API funcione correctamente y no interfiera con otros módulos, asegurando eficiencia, claridad y cumplimiento de responsabilidades dentro del flujo de la aplicación.


## 👤 Autor

**Ivan Gomez Dell'Osa**

- GitHub: https://github.com/IvanGomezDellOsa/FaceHunt
- Email: ivangomezdellosa@gmail.com
- Linkedin: https://www.linkedin.com/in/ivangomezdellosa/
---