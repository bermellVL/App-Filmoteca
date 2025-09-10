import requests
import pandas as pd

# API Key de TMDB
API_KEY = "0e1b521bb784d936b178e6dc486eeabf"

def get_movie_details(movie_id):
    """
    Obtiene los detalles de una película por su ID.
    Maneja errores de conexión y de API.
    """
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lanza un error para códigos de estado 4xx/5xx
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error en la petición a la API: {e}")
        return None

def get_movies_by_genres(genre_ids, num_pages=3):
    """
    Busca películas por género en múltiples páginas.
    """
    all_movies = []
    # Convertimos la lista de IDs a una cadena separada por comas
    genres_str = ','.join(map(str, genre_ids))
    
    for page in range(1, num_pages + 1):
        url = f"https://api.themoviedb.org/3/discover/movie?with_genres={genres_str}&sort_by=vote_average.desc&vote_count.gte=50&page={page}&api_key={API_KEY}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            all_movies.extend(data.get('results', []))
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener la página {page}: {e}")
            break
            
    return pd.DataFrame(all_movies)

# --- INICIO DEL PROGRAMA PRINCIPAL ---

print("Dame el nombre de una pelicula:")
nombre_pelicula = input()

try:
    url_busqueda = f"https://api.themoviedb.org/3/search/movie?query={nombre_pelicula}&api_key={API_KEY}"
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