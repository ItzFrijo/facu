import spotipy
from spotipy.oauth2 import SpotifyOAuth
import datetime

from sklearn.cluster import KMeans ###Clustering de Canciones
import numpy as np ### para Clustering de Canciones

# Credenciales de autenticación
def autenticar_usuario():
    # Configura la autenticación con las credenciales de tu aplicación
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
       client_id="96e2f02f81f2427e9a7bd6a3d4c4e1aa",
      client_secret="e3686e970c754cdd8c6c1d42033858a7",
       redirect_uri="http://localhost:8888/callback",
      scope="playlist-modify-public user-top-read playlist-read-private"
      ))
    return sp



# Función para obtener las canciones más escuchadas diariamente
def obtener_top_canciones(periodo='short_term', limite=20):
    resultados = sp.current_user_top_tracks(time_range=periodo, limit=limite)
    return [track['id'] for track in resultados['items']]

# Función para obtener el ID de una playlist por su nombre, si existe
def obtener_playlist_id(nombre_playlist):
    playlists = sp.current_user_playlists()
    for playlist in playlists['items']:
        if playlist['name'] == nombre_playlist:
            return playlist['id']
    return None

# Función para crear o actualizar una playlist
def crear_actualizar_playlist(nombre_playlist, descripcion, canciones):
    playlist_id = obtener_playlist_id(nombre_playlist)
    if playlist_id:
        # Actualizar la playlist existente
        sp.user_playlist_replace_tracks(user=sp.current_user()['id'], playlist_id=playlist_id, tracks=canciones)
    else:
        # Crear una nueva playlist
        sp.user_playlist_create(user=sp.current_user()['id'], name=nombre_playlist, public=True, description=descripcion)
        playlist_id = obtener_playlist_id(nombre_playlist)
        sp.user_playlist_add_tracks(user=sp.current_user()['id'], playlist_id=playlist_id, tracks=canciones)

# Crear y actualizar la playlist diaria
def crear_playlist_diaria():
    top_canciones_diarias = obtener_top_canciones(periodo='short_term', limite=20)
    crear_actualizar_playlist("Playlist Diaria by Spotylist", "Las canciones más escuchadas diariamente", top_canciones_diarias)

# Crear y actualizar la playlist semanal
def crear_playlist_semanal():
    top_canciones_semanales = obtener_top_canciones(periodo='medium_term', limite=30)
    crear_actualizar_playlist("Playlist Semanal by Spotylist", "Las canciones más escuchadas semanalmente", top_canciones_semanales)

# Función para obtener recomendaciones basadas en canciones pasadas
def obtener_recomendaciones(canciones_fuente, limite=30):
    recomendaciones = sp.recommendations(seed_tracks=canciones_fuente[:5], limit=limite)
    return [track['id'] for track in recomendaciones['tracks']]

# Crear y actualizar la playlist de recomendaciones
def crear_playlist_recomendaciones():
    top_canciones_diarias = obtener_top_canciones(periodo='short_term', limite=5)
    top_canciones_semanales = obtener_top_canciones(periodo='medium_term', limite=5)

    # Obtener todas las canciones de las playlists del usuario
    playlists = sp.current_user_playlists()
    canciones_todas_playlists = []
    for playlist in playlists['items']:
        tracks = sp.playlist_tracks(playlist['id'])
        canciones_todas_playlists.extend([track['track']['id'] for track in tracks['items']])

    # Usar canciones de playlists y top de canciones para recomendaciones
    canciones_fuente = top_canciones_diarias + top_canciones_semanales + canciones_todas_playlists[:10]
    canciones_recomendadas = obtener_recomendaciones(canciones_fuente, limite=30)
    crear_actualizar_playlist("Recomendaciones de Spotylist", "Canciones recomendadas basadas en tu actividad reciente", canciones_recomendadas)


#Función principal para familia e indi
if __name__ == "__main__":
    usuarios = ["usuario1", "usuario2", "usuario3"]  # Lista de nombres o identificadores de usuarios
    for usuario in usuarios:
        print(f"Autenticando a {usuario}...")
        sp = autenticar_usuario()  # Cada usuario debe autenticarse
        top_canciones = obtener_top_canciones(sp)
        print(f"Top Canciones de {usuario}:", top_canciones)
        
# Ejecutar las funciones para crear/actualizar playlists
if __name__ == "__main__":
    crear_playlist_diaria()
    crear_playlist_semanal()
    crear_playlist_recomendaciones()
    
    

#para cluster de canciones (agrupar canciones similares basándote 
# en características como el tempo, la energía, la valencia, etc.,
# podrías usar algoritmos de clustering como K-means o DBSCAN. Para esto,
# necesitarías extraer las características de las canciones 
# usando la API de Spotify y luego aplicar el algoritmo de clustering a esos datos.)

# Obtener características de las canciones
def obtener_caracteristicas_canciones(ids_canciones):
    features = sp.audio_features(ids_canciones)
    return np.array([[f['danceability'], f['energy'], f['valence']] for f in features if f is not None])

# Clustering de Canciones
def clusterizar_canciones():
    # Obtener las canciones más escuchadas
    top_canciones = obtener_top_canciones()
    caracteristicas = obtener_caracteristicas_canciones(top_canciones)
    
    # Aplicar K-Means
    kmeans = KMeans(n_clusters=5)  # Puedes ajustar el número de clusters
    kmeans.fit(caracteristicas)
    
    # Obtener etiquetas de clusters
    etiquetas = kmeans.labels_
    
    for i in range(5):  # Imprimir canciones en cada cluster
        print(f"Cluster {i}:")
        for idx, label in enumerate(etiquetas):
            if label == i:
                print(f" - Canción ID: {top_canciones[idx]}")

# Ejecutar la función
if __name__ == "__main__":
    clusterizar_canciones()
    
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA


# Supongamos que 'X' es tu matriz de características de audio
kmeans = KMeans(n_clusters=5, random_state=0).fit(2)
labels = kmeans.labels_

# Reducir la dimensionalidad
pca = PCA(n_components=2)
X_reduced = pca.fit_transform(5)

# Graficar los clústeres
plt.scatter(X_reduced[:, 0], X_reduced[:, 1], c=labels, cmap='viridis')
plt.title('Visualización de Clústeres de Canciones')
plt.xlabel('Componente Principal 1')
plt.ylabel('Componente Principal 2')
plt.colorbar(label='Etiqueta del Clúster')
plt.show()