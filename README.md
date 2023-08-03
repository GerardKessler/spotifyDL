# spotifyDL

Complemento que permite descargar canciones de la plataforma Spotify. Basado en el programa spotify-downloader <https://github.com/spotDL/spotify-downloader>

## Instrucciones:

Asignar un atajo de teclado en la configuración de gestos de entrada, categoría spotifyDL.

La primera vez que se ejecuta el comando antes configurado se solicita la descarga del ejecutable del programa desde su repositorio oficial de github. Seguidamente se descarga el ejecutable de ffmpeg, y se guarda en la carpeta de configuración del programa:

    c:\Users\NombreDeUsuario\.spotdl

Al volver a pulsar el gesto se activa la interfaz del complemento, la cual tiene tan solo un cuadro editable donde se debe pegar el link válido de spotify de lo que se quiere descargar. Al pulsar intro comienza la descarga.

En el caso de las listas o álbumes, la descarga puede demorarse bastante. Con las canciones individuales se activa una ventana modal de notificación al finalizar.

La ruta por defecto donde se van a descargar los archivos en mp3 es:

    c:\Users\NombreDeUsuario\spotifyDL

