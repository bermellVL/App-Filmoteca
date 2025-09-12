
# 🎬 App-Filmoteca: Tu Buscador y Recomendador de Películas

## 📖 Descripción del Proyecto
**App-Filmoteca** es una herramienta de consola en **Python** que combina la API de **TMDB**, la librería **Pandas** y la **API de Gemini** para buscar y recomendar películas.  
El proyecto muestra cómo integrar varias fuentes de datos y modelos de IA para crear un recomendador de películas práctico y educativo.

---

## ✨ Características Principales
- 🔍 **Búsqueda Detallada**: Encuentra películas por título y obtiene información como géneros, puntuación y popularidad.  
- 🤖 **Recomendaciones Inteligentes**: Usa una **puntuación ponderada** para priorizar películas de calidad con gran número de votos.  
- 🛡 **Manejo de Errores Robusto**: Soporta errores de conexión, IDs incorrectos y resultados vacíos.  
- 💡 **Búsqueda por Descripción (Gemini + TMDB)**: A partir de una frase o sinopsis, Gemini sugiere títulos y Cinevisor muestra detalles de las películas encontradas.  

---

## 🛠 Instalación y Uso

### 📦 Requisitos
Instala las librerías necesarias con `pip`:

```bash
pip install pandas requests google-generativeai
