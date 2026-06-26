[English](README.en.md) | [Español](README.md)

# FaceHunt

FaceHunt is a deep learning-based video analysis tool that identifies every appearance of a person. You only need to upload a reference photo and a video (local or from YouTube) to get a precise list of the exact moments when the person appears.

> 🚀 **New version available:** [**FaceHunt 2**](https://github.com/IvanGomezDellOsa/FaceHunt-2) — a complete rewrite: ~10x faster, with GPU acceleration, a local desktop app and more complete results.


## Project Status

FaceHunt now includes a modern web interface in addition to the original desktop application. Both versions are fully functional.

The web version is ideal for trying FaceHunt as a demo, since it requires no installation or local setup. However, since it runs on public servers, processing times are longer compared to the local version.

<p align="center">
  <a href="https://huggingface.co/spaces/IvanGomezDellOsa/FaceHunt" target="_blank">
    <img 
      alt="Click para probar FaceHunt Web" 
      src="https://img.shields.io/badge/%F0%9F%91%89_CLICK_PARA_PROBAR_FACEHUNT_WEB-0066ff?style=for-the-badge" 
      height="100"
      width="350"
    >
  </a>
</p>

<br><br><br><br>

## ✨ Features

- 🌐 **Modern Web Interface**
    - A clean, responsive, step-by-step UI that works in any modern browser.

- 🎯 **Accurate Facial Recognition**
    - Uses the `DeepFace` library with the `FaceNet` model for high accuracy in face identification.

- 📹 **Flexible Video Sources**
    - Native support for both YouTube URLs and uploading local video files (MP4, AVI, MOV, MKV, WebM).

- ⚡ **Two Processing Modes**
    - Lets the user choose the perfect balance between speed and accuracy for each analysis.
        - **High Accuracy:** Uses the `RetinaFace` detector for maximum quality.
        - **Balanced:** Uses the `mtcnn` detector for a faster analysis (still extremely accurate).

- 🔍 **Multiple Detection Backends**
    - Support for `RetinaFace`, `mtcnn` and `OpenCV`.

- 🛰️ **Robust RESTful API**
    - A backend powered by `FastAPI` that exposes all the business logic securely and efficiently.    

- 🖥️ **Desktop GUI (Legacy)**
    - Built with `Tkinter`.


#### Usage:

1. **Step 1:** Upload a reference image (it must contain exactly one face)
<p align="center">
  <img alt="Paso 1 - Subir Imagen de Referencia" src="https://cdn.jsdelivr.net/gh/IvanGomezDellOsa/FaceHunt@a7a5a2ff8fa0e41c1923414a6b9c13ec63bebd9d/assets/wf_0.webp" width="750" />
</p>
<p align="center">
  <img alt="Paso 1 - Subir Imagen de Referencia" src="https://cdn.jsdelivr.net/gh/IvanGomezDellOsa/FaceHunt@a7a5a2ff8fa0e41c1923414a6b9c13ec63bebd9d/assets/wf_1.webp" width="750" />
</p>

---

2. **Step 2:** Select a video (local file or YouTube URL)
<p align="center">
  <img alt="Paso 2 - Seleccionar Fuente de Video" src="https://cdn.jsdelivr.net/gh/IvanGomezDellOsa/FaceHunt@a7a5a2ff8fa0e41c1923414a6b9c13ec63bebd9d/assets/wf_2.webp" width="750" />
</p>

---

3. **Step 3:** Choose the processing mode (Balanced or High Accuracy)
<p align="center">
  <img alt="Paso 3 - Elegir Modo de Procesamiento" src="https://cdn.jsdelivr.net/gh/IvanGomezDellOsa/FaceHunt@a7a5a2ff8fa0e41c1923414a6b9c13ec63bebd9d/assets/wf_3.webp" width="750" />
</p>

---

4. **Step 4:** Review the results. If there are matches, it shows timestamps of the exact moments where the reference face appears in the video. 
<p align="center">
  <img alt="Paso 4 - Procesando" src="https://cdn.jsdelivr.net/gh/IvanGomezDellOsa/FaceHunt@a7a5a2ff8fa0e41c1923414a6b9c13ec63bebd9d/assets/wf_4.webp" width="750" />
</p>
<p align="center">
  <img alt="Paso 4 - Procesando" src="https://cdn.jsdelivr.net/gh/IvanGomezDellOsa/FaceHunt@a7a5a2ff8fa0e41c1923414a6b9c13ec63bebd9d/assets/wf_5.webp" width="750" />
</p>


## Try FaceHunt

<p align="center">
  <a href="https://huggingface.co/spaces/IvanGomezDellOsa/FaceHunt" target="_blank">
    <img 
      alt="Click para probar FaceHunt Web" 
      src="https://img.shields.io/badge/%F0%9F%91%89_CLICK_PARA_PROBAR_FACEHUNT_WEB-0066ff?style=for-the-badge" 
      height="100"
      width="300"
    >
  </a>
</p>

### Option 1: Run with Docker (Recommended)
This is the fastest way to try the application without installing anything other than Docker. Docker will automatically download it from Docker Hub.

1. **Run the container:**
   Open a terminal and run the following command:  
   ```bash
   docker run -it --rm -p 7860:7860 ivangomezdellosa/facehunt
   ```

2. **Open the application:**  
   Go to your browser and open the following address:  
   ```
   http://localhost:7860
   ```

### Option 2: Run Locally
This option is ideal for developers who want to explore the source code and understand how the application works.

1. **Clone the repository:**  
   ```bash
   git clone https://github.com/IvanGomezDellOsa/FaceHunt.git
   cd FaceHunt
   ```

2. **Create and activate a virtual environment:**  
   ```bash
   # Crea el entorno
   python -m venv .venv

   # Activa en Windows (PowerShell)
   .venv\Scripts\Activate.ps1

   # Activa en macOS/Linux
   source .venv/bin/activate
   ```

3. **Install the dependencies:**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the server:**  
   This single command will start both the backend (API) and the frontend (web interface).  
   ```bash
   python api_server.py
   ```

5. **Open the application:**  
   Go to your browser and open the following address:  
   ```
   http://localhost:7860
   ```

---

**Note for developers:** The API documentation will be available automatically at `http://localhost:7860/docs`.


<details>
<summary>🗄️ Instructions for the Desktop GUI (Tkinter)</summary>

I decided to keep the code of the original desktop version so as not to remove that option and so it serves as a record of the project's evolution. This version was built with Tkinter.

### Run the GUI Locally (Without Docker)

To run the old graphical interface, first follow the steps in [Option 2: Run Locally](#option-2-run-locally) of the main guide to clone the project and install the dependencies in a virtual environment.

Once you have everything installed, simply run the following command:

```bash
python main.py
```

**Important Note:** This version is no longer under active development. The old instructions for running this GUI inside a Docker container with an X server (such as VcXsrv) are no longer compatible with the current Dockerfile, which is designed exclusively for the web application.

</details>


<details>
<summary>🏛️ Architecture and Main Modules</summary>

#### `fh_core.py`
- **Purpose:** Coordinates the full processing flow
- **Key functions:**
  - `validate_image_file()`: Validates the image and extracts the facial embedding
  - `validate_video_source()`: Verifies the video's accessibility
  - `execute_workflow()`: Orchestrates the validation, extraction and recognition, returning the facial match results.

#### `fh_downloader.py`
- **Purpose:** Downloads YouTube videos
- **Technology:** yt-dlp
- **Format:** MP4 at 480p maximum
- **Validations:** Disk space, duplicates
- **Destination:** Temporary folder managed automatically by the system.

#### `fh_frame_extractor.py`
- **Purpose:** Extracts frames from the video
- **Modes:**
  - High Accuracy: 1 frame every 0.25s (RetinaFace)
  - Balanced: 1 frame every 0.5s (mtcnn)
- **Optimization:** Batch frame generator to reduce memory usage on long videos.

#### `fh_face_recognizer.py`
- **Purpose:** Detects and compares faces
- **Model:** FaceNet (128-d embeddings)
- **Metric:** Cosine distance (match if ≤ 0.32)
- **Available detectors:**
  - RetinaFace (high accuracy, slow)
  - mtcnn (balanced)
  - OpenCV (fast, low accuracy)

</details>

### 🧾 Disclosure of Responsibilities

The goal of this project was to demonstrate skills in **Python**, covering software architecture, video processing, integration of Machine Learning models and resource optimization.  
For transparency, I clarify which parts AI was involved in and which it was not. It was used with a defined purpose as a support tool, and not as the protagonist or orchestrator of the development.

- **Logic (Python):** Entirely my own development. With a meticulous focus on optimization, simplification and cleanliness of the code, removing redundancies, fixing failing validations, improving execution times and ensuring a coherent flow between modules.  
- **Frontend (HTML/CSS/JS)** Although I have experience in these technologies, this component was not the focus of the challenge. I decided to delegate the web design to an AI (v0), recognizing that it could generate a cleaner and more aesthetic interface in less time. This allowed me to not deviate from the project's goal and focus 100% on the backend.  
- **API Architecture (FastAPI):** Since I am in the process of learning FastAPI, I used AI to generate the basic syntax. My work focused on the design of the logical architecture. This involved actively rejecting the inefficient architectures proposed by the AI (which duplicated code, split responsibilities and sacrificed optimization) and, instead, designing and implementing a clean and fully optimized data flow. This redesign was fundamental to ensure the API communicates efficiently with the Python core.
- **Documentation (README and Docstrings):** The writing was done almost entirely by AI. Afterwards, the content was edited and refined manually by me to ensure technical accuracy and faithfully reflect the architecture decisions made.  

## 👤 Author

**Iván Gómez Dell'Osa**

- GitHub: https://github.com/IvanGomezDellOsa
- Email: ivangomezdellosa@gmail.com
- Linkedin: https://www.linkedin.com/in/ivangomezdellosa/
---
