import requests
import pandas as pd
import json
import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# API Keys de TMDB y Gemini
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Verificación de las API keys
if not TMDB_API_KEY or not GEMINI_API_KEY:
    print("Error: No se encontraron las claves de API.")
    print("Asegúrate de tener un archivo '.env' en el mismo directorio que 'Peliculas.py'")
    print("y que contenga las siguientes líneas:")
    print("TMDB_API_KEY=tu_clave_aqui")
    print("GEMINI_API_KEY=tu_clave_aqui")
    sys.exit()
    
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def get_movie_details(movie_id):
    """Obtiene los detalles de una película por su ID y maneja errores."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error en la petición a la API de TMDB: {e}")
        return None

def get_ai_movie_titles(query):
    """
    Usa la API de Gemini con Google Search Grounding para encontrar y
    estructurar los títulos de películas.
    """
    # Se le pide a la IA que devuelva una lista numerada en lugar de JSON.
    prompt = f"""Basado en esta descripción, dame una lista numerada de 5 títulos de películas que puedan coincidir. Responde únicamente con la lista de títulos, sin texto adicional, por ejemplo: 
1. Título 1
2. Título 2
...

Descripción: "{query}". Si no hay resultados, devuelve una lista vacía. Si un título no está disponible, no lo incluyas."""
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': GEMINI_API_KEY
    }
    
    try:
        response = requests.post(
            GEMINI_API_URL,
            headers=headers,
            data=json.dumps(payload)
        )
        response.raise_for_status()
        result = response.json()
        
        # Extraer el texto y procesarlo para obtener los títulos
        candidate = result.get('candidates', [])[0]
        text = candidate.get('content', {}).get('parts', [{}])[0].get('text', '')
        
        # Parsear la lista numerada
        titles = []
        for line in text.split('\n'):
            if line and line.strip() and line[0].isdigit():
                # Elimina el número y el punto
                parts = line.split('.', 1)
                if len(parts) > 1:
                    title = parts[1].strip()
                    if title:
                        titles.append(title)
        
        if titles:
            return titles
        else:
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error en la petición a la API de Gemini o al procesar la respuesta: {e}")
        return None


def get_movies_by_genres(genre_ids, num_pages=3):
    """
    Busca películas por género en múltiples páginas.
    """
    all_movies = []
    # Convertimos la lista de IDs a una cadena separada por comas
    genres_str = ','.join(map(str, genre_ids))
    
    for page in range(1, num_pages + 1):
        url = f"https://api.themoviedb.org/3/discover/movie?with_genres={genres_str}&sort_by=vote_average.desc&vote_count.gte=50&page={page}&api_key={TMDB_API_KEY}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            all_movies.extend(data.get('results', []))
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener la página {page}: {e}")
            break
            
    return pd.DataFrame(all_movies)

def search_by_description():
    """Lógica para buscar películas por descripción usando Gemini."""
    print("¡Bienvenido a App-Filmoteca!")
    print("Describe una película con tus propias palabras.")
    print("Ejemplo: 'Una película de acción de los 90 sobre dinosaurios'")
    
    print("\nDame una descripción de la pelicula:")
    descripcion_pelicula = input()

    print("\nBuscando títulos de películas que coincidan...")
    
    ai_titles = None
    for attempt in range(3):
        ai_titles = get_ai_movie_titles(descripcion_pelicula)
        if ai_titles:
            break
        print(f"Intento {attempt + 1} fallido. Reintentando...")
    
    if not ai_titles:
        print("La IA no ha sugerido títulos de películas. Por favor, intenta una descripción diferente.")
        return
        
    print("\nLa IA ha sugerido los siguientes títulos:")
    for i, title in enumerate(ai_titles):
        print(f"{i+1}. {title}")
        
    try:
        selection = int(input("\nSelecciona el número de la película que quieres analizar: "))
        if 1 <= selection <= len(ai_titles):
            movie_title_from_ai = ai_titles[selection - 1]
            print(f"\nBuscando detalles de '{movie_title_from_ai}' en TMDB...")

            # Hacemos la búsqueda en TMDB con el título seleccionado
            url_busqueda = f"https://api.themoviedb.org/3/search/movie?query={movie_title_from_ai}&api_key={TMDB_API_KEY}"
            respuesta_busqueda = requests.get(url_busqueda)
            respuesta_busqueda.raise_for_status()
            datos_busqueda = respuesta_busqueda.json()
            
            if not datos_busqueda.get('results'):
                print("No se encontraron resultados en TMDB para ese título.")
            else:
                df_peliculas = pd.DataFrame(datos_busqueda['results'])
                df_busqueda_filtrado = df_peliculas[['id', 'title', 'release_date', 'vote_average', 'vote_count', 'popularity']]
                print("-------------Resultados de la busqueda------------------")
                print(df_busqueda_filtrado.head())
        else:
            print("Selección inválida. Por favor, reinicia el programa.")
    except (ValueError, IndexError):
        print("Entrada inválida. Por favor, ingresa un número válido.")

def recommend_movies():
    """Lógica para recomendar películas similares."""
    print("\nDame el nombre de la pelicula:")
    nombre_pelicula = input()

    try:
        url_busqueda = f"https://api.themoviedb.org/3/search/movie?query={nombre_pelicula}&api_key={TMDB_API_KEY}"
        respuesta_busqueda = requests.get(url_busqueda)
        respuesta_busqueda.raise_for_status()
        datos_busqueda = respuesta_busqueda.json()
        
        if not datos_busqueda.get('results'):
            print("No se encontraron resultados para esa película.")
        else:
            df_peliculas = pd.DataFrame(datos_busqueda['results'])
            df_busqueda_filtrado = df_peliculas[['id', 'title', 'release_date', 'vote_average', 'vote_count', 'popularity', 'genre_ids']]
            print("-------------Resultados de la busqueda------------------")
            print(df_busqueda_filtrado.head())
            
            print("\nDame el ID de la pelicula que quieres analizar:")
            id_elegido = input()
            
            datos_detalle = get_movie_details(id_elegido)
            
            if datos_detalle and 'genres' in datos_detalle:
                generos_seleccionados = [g['name'] for g in datos_detalle['genres']]
                generos_ids_seleccionados = [g['id'] for g in datos_detalle['genres']]
                print("\n-------------Generos de la pelicula seleccionada-------------------")
                print(generos_seleccionados)
                
                # Obtiene un DataFrame grande de recomendaciones basado en los géneros
                df_recomendaciones = get_movies_by_genres(generos_ids_seleccionados, num_pages=5)
                
                if not df_recomendaciones.empty:
                    # Calculamos el promedio global de votos para el cálculo ponderado
                    C = df_recomendaciones['vote_average'].mean()
                    # Definimos el mínimo de votos para calificar, un valor común es 50
                    m = 50
                    
                    # Calculamos el Weighted Rating para cada película
                    df_recomendaciones['weighted_rating'] = (
                        (df_recomendaciones['vote_count'] / (df_recomendaciones['vote_count'] + m)) * df_recomendaciones['vote_average']
                        + (m / (df_recomendaciones['vote_count'] + m)) * C
                    )
                    
                    # Ordenamos las recomendaciones por la puntuación ponderada
                    df_recomendaciones = df_recomendaciones.sort_values(by='weighted_rating', ascending=False)
                    
                    print("\n-------------Peliculas recomendadas (puntuacion ponderada)-----------------")
                    # Imprimimos las 5 mejores recomendaciones
                    print(df_recomendaciones[['title', 'vote_average', 'vote_count', 'weighted_rating']].head(5))
                else:
                    print("No se encontraron recomendaciones con los géneros de la película.")
            else:
                print("El ID de la película no es válido. Por favor, reinicia e intenta de nuevo.")

    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}. Por favor, revisa tu conexión a Internet o tu clave de API.")


# --- INICIO DEL PROGRAMA PRINCIPAL --- 
def main():
    while True:
        print("\n--- MENÚ PRINCIPAL ---")
        print("1. Buscar películas por descripción (con IA)")
        print("2. Recomendar películas similares")
        print("3. Salir")
        
        choice = input("Selecciona una opción (1, 2 o 3): ")
        
        if choice == '1':
            search_by_description()
        elif choice == '2':
            recommend_movies()
        elif choice == '3':
            print("Saliendo del programa. ¡Hasta pronto!")
            break
        else:
            print("Opción no válida. Por favor, selecciona 1, 2 o 3.")

if __name__ == "__main__":
    main()
