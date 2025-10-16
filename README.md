# FaceHunt

FaceHunt utiliza deep learning para encontrar todas las apariciones de una persona específica en videos. Simplemente sube una foto de referencia con un rostro claro, proporciona un enlace de YouTube o un video local, y deja que FaceHunt haga el resto.

## 🚧 Estado del Proyecto y Uso con Docker

Este proyecto es actualmente una aplicación de escritorio y se encuentra **en desarrollo**. El proximo objetivo (antes de noviembre de 2025) es ofrecer una versión web.

Mientras tanto, la forma más sencilla de probar la versión actual es a través de Docker.

## ✨ Características

- 🎯 Reconocimiento facial preciso usando DeepFace
- 📹 Soporte para YouTube - Procesa videos directamente desde URLs
- 💾 Archivos de video locales - Soporta MP4, AVI, MOV, MKV, WebM
- 🎨 GUI amigable para el usuario construida con Tkinter
- ⚡ Dos modos de procesamiento: Alta Precisión & Equilibrado
- 🔍 Múltiples backends de detección: RetinaFace, MTCNN, OpenCV

## Inicio Rápido

### Prerrequisitos

**Usuarios de Windows:**

- Instala Docker Desktop
- Instala VcXsrv (X Server para GUI)

**Usuarios de Linux:**

- Instala Docker
- X11 debería estar disponible

### Paso 1: Prepara Tus Archivos

Crea una carpeta compartida en tu Escritorio:

```bash
# Windows (PowerShell)
mkdir "$env:USERPROFILE\Desktop\facehunt_inputs"

# Linux
mkdir ~/Desktop/facehunt_inputs
```

Coloca tu imagen de referencia (Que contenga un sola cara, no importa la definicion o el tamaño) en esta carpeta. Opcionalmente, agrega videos locales para procesar.

### Paso 2: Inicia VcXsrv (Solo Windows)

- Abre XLaunch desde el menú Inicio
- Configuración:
  - Display settings: Multiple windows → Next
  - Client startup: Start no client → Next
  - Extra settings: ✅ Disable access control → Next → Finish
- Deberías ver un ícono "X" en la bandeja del sistema.

### Paso 3: Ejecuta FaceHunt

**Windows (PowerShell):**

```powershell
# Detección automática de IP y lanzamiento
$ip = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias 'Wi-Fi', 'Ethernet' | Where-Object { $_.AddressState -eq 'Preferred' } | Select-Object -First 1).IPAddress;
if ($ip) {
    Write-Host "✅ IP detectada: $ip";
    
    # Verifica si VcXsrv está ejecutándose
    $vcxsrv = Get-NetTCPConnection -LocalPort 6000 -ErrorAction SilentlyContinue;
    if (-not $vcxsrv) {
        Write-Host "⚠️  Advertencia: VcXsrv no parece estar ejecutándose" -ForegroundColor Yellow;
        Write-Host "    Inicia XLaunch antes de continuar.";
        $continue = Read-Host "Continuar de todos modos? (y/n)";
        if ($continue -ne 'y') { exit; }
    }
    
    Write-Host "🚀 Iniciando contenedor...";
    docker run -it --rm `
      -e DISPLAY="${ip}:0.0" `
      -v "$env:USERPROFILE\Desktop\facehunt_inputs:/app/shared" `
      ivangomezdellosa/facehunt;
} else {
    Write-Host "❌ Error: No se pudo detectar la IP local. Verifica tu conexión de red.";
}
```

**Linux:**

```bash
xhost +local:docker
docker run -it --rm \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v ~/Desktop/facehunt_inputs:/app/shared \
  ivangomezdellosa/facehunt
```

### Paso 4: Usando la Aplicación

Cuando se abra la GUI, haz clic en "Examinar Imagen"  
Navega a `/app/shared` para ver tus archivos  
Selecciona tu imagen de referencia  
Haz clic en "Validar Imagen"  
Ingresa una URL de YouTube o examina un video local (también en `/app/shared`)  
Haz clic en "Validar Fuente de Video"  
Elige el modo de procesamiento (Alta Precisión o Equilibrado)  
Haz clic en "Iniciar Reconocimiento"

## 🛠️ Ejecutar localmente sin Docker


```bash
# Clona el repositorio
git clone https://github.com/IvanGomezDellOsa/FaceHunt.git
cd FaceHunt

# Crea un entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate     # Windows

# Instala dependencias
pip install -r requirements.txt

# Ejecuta la aplicación
python main.py
```

## 🔧 Construyendo la Imagen de Docker

```bash
# Construye localmente
docker build -t facehunt .

# Ejecuta tu construcción local
docker run -it --rm -e DISPLAY=YOUR_IP:0.0 -v path/to/inputs:/app/shared facehunt
```

## ⚠️ Solución de Problemas

**"Could not connect to display"**

**Windows:**
- Asegúrate de que VcXsrv esté ejecutándose (verifica el ícono "X" en la bandeja del sistema)
- Verifica que "Disable access control" esté marcado en la configuración de XLaunch
- Intenta reiniciar VcXsrv

**Linux:**
- Ejecuta `xhost +local:docker` antes de iniciar el contenedor
- Verifica que la variable de entorno `$DISPLAY` esté configurada

---
