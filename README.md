# Lucario - Moonani Discord Pokemon Coordinates Bot

Bot de Discord en Python que consulta el endpoint de Moonani PokeList para obtener apariciones de Pokemon, extraer sus coordenadas y publicarlas en Discord mediante comandos slash.

## Que hace este proyecto

- Consulta el endpoint `https://moonani.com/PokeList/ajax.php?page=pokemon&action=load`
- Limpia el HTML que devuelve Moonani en campos como nombre, IV, coordenadas y pais
- Extrae coordenadas listas para copiar y abrir en Google Maps
- Permite buscar por nombre parcial
- Devuelve los resultados disponibles del endpoint 100 IV de Moonani
- Responde en Discord con mensajes compactos o embeds

## Estructura del proyecto

- `discord_bot.py`: punto de entrada del bot y definicion de comandos slash
- `moonani_client.py`: cliente HTTP y logica de parseo y filtrado de resultados
- `test_pokelist_limpio.py`: script base limpio usado para validar la idea original
- `.env.example`: ejemplo de variables de entorno
- `requirements.txt`: dependencias del proyecto

## Comandos disponibles

- `/ping`: verifica si el bot esta en linea
- `/pokemon`: muestra resultados con formato enriquecido
- `/coords`: devuelve coordenadas en formato compacto para copiar rapido

## Requisitos

- Python 3.13 recomendado
- Un bot creado en el [Discord Developer Portal](https://discord.com/developers/applications)

## Obtener el proyecto

Tienes dos formas de conseguir los archivos del bot.

### Opcion 1: clonar el repositorio

```powershell
git clone https://github.com/KernelX-debug/Discord-Bot_Lucario_Moonamiphp.git
cd Discord-Bot_Lucario_Moonamiphp
```

### Opcion 2: descargar y copiar los archivos manualmente

Si no vas a usar Git, crea una carpeta para el proyecto y copia dentro estos archivos:

- `discord_bot.py`
- `moonani_client.py`
- `requirements.txt`
- `.env.example`

Si descargaste el proyecto como ZIP desde GitHub, extraelo y entra a la carpeta extraida antes de seguir.

## Archivos minimos necesarios

Antes de instalar, asegúrate de que tu carpeta contiene al menos:

- `discord_bot.py`
- `moonani_client.py`
- `requirements.txt`
- `.env.example`

## Instalacion paso a paso

1. Entra a la carpeta del proyecto.

```powershell
cd ruta\de\tu\proyecto
```

2. Instala las dependencias.

```powershell
py -3.13 -m pip install -r requirements.txt
```

3. Crea el archivo `.env`.

```powershell
New-Item -Path .env -ItemType File -Force
```

4. Abre `.env` y pega esta configuracion base.

```env
DISCORD_BOT_TOKEN=pega_aqui_el_token_de_tu_bot
DISCORD_GUILD_ID=pega_aqui_el_id_del_servidor(opcional)
MOONANI_TIMEOUT=20
MOONANI_PAGE_SIZE=100
MOONANI_MAX_SCAN_RECORDS=10000
MOONANI_RESOLVE_COUNTRIES=false
MOONANI_GEOCODER_ENDPOINT=
MOONANI_GEOCODER_USER_AGENT=Lucario Discord Bot/1.0
```

## Significado de las variables

- `DISCORD_BOT_TOKEN`: token privado de tu bot
- `DISCORD_GUILD_ID`: opcional, acelera la aparicion de comandos slash en un servidor concreto
- `MOONANI_TIMEOUT`: tiempo maximo de espera para peticiones HTTP
- `MOONANI_PAGE_SIZE`: cuantos registros pedir por bloque al endpoint
- `MOONANI_MAX_SCAN_RECORDS`: limite maximo de registros a revisar en una busqueda
- `MOONANI_RESOLVE_COUNTRIES`: intenta resolver el pais desde coordenadas cuando Moonani no lo devuelve
- `MOONANI_GEOCODER_ENDPOINT`: endpoint de reverse geocoding
- `MOONANI_GEOCODER_USER_AGENT`: identificador HTTP para el geocoder

## Ejecucion

```powershell
py -3.13 discord_bot.py
```

## Prueba tecnica de funcionamiento

Antes de levantar el bot en Discord, se puede validar de forma aislada la extraccion de datos desde Moonani usando unicamente el archivo `test_pokelist_limpio.py`.

Si necesitas recrear este script manualmente, crea un archivo llamado `test_pokelist_limpio.py` y pega el siguiente contenido:

```python
import html
import re

import requests


def extraer_coords(texto):
    match = re.search(r'data-clipboard-text="([^"]+)"', texto)
    return match.group(1) if match else ""


def limpiar_nombre(texto):
    # Primero decodifica entidades HTML (&#9792; -> ♀, &#9794; -> ♂)
    texto = html.unescape(texto)
    # Luego elimina las etiquetas HTML
    texto = re.sub(r"<[^>]+>", "", texto)
    # Limpia espacios extra
    return texto.strip()


def extraer_pais(texto):
    texto = html.unescape(texto)
    texto = re.sub(r"<[^>]+>", "", texto).strip()
    return texto if texto else "??"


url = "https://moonani.com/PokeList/ajax.php?page=pokemon&action=load"
payload = {
    "iv": 100,
    "pvp": 0,
    "pokemons": "",
    "start": 0,
    "length": 230,
    "draw": 1,
}
headers = {
    "Referer": "https://moonani.com/PokeList/index.php",
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0",
}

r = requests.post(url, data=payload, headers=headers, timeout=20)
r.raise_for_status()
data = r.json().get("data", [])

print(f"Total pokémones recibidos: {len(data)}\n")

for p in data:
    nombre = limpiar_nombre(p["Name"])
    coords = extraer_coords(p["Coords"])
    shiny = "✨ SHINY" if p["Shiny"] == "Yes" else ""
    pais = extraer_pais(p["Country"])

    print(f"{'=' * 50}")
    print(f"🎯 {nombre} #{p['Number']} {shiny}")
    print(f"📍 {coords}")
    print(f"⚡ CP: {p['CP']} | Nivel: {p['Level']}")
    print(f"💪 ATK:{p['Attack']} DEF:{p['Defense']} HP:{p['HP']}")
    print(f"⏱️  Inicio: {p['Start Time']}")
    print(f"⏱️  Fin:    {p['End Time']}")
    print(f"🌍 País: {pais}")
    print(f"🗺️  https://maps.google.com/?q={coords}")
```

Ejecuta la prueba con:

```powershell
py -3.13 test_pokelist_limpio.py
```

Resultado esperado:

- El script realiza una peticion HTTP directa al endpoint de Moonani
- Procesa la respuesta JSON sin depender de Discord
- Limpia el HTML embebido en campos como `Name`, `Coords` y `Country`
- Imprime en consola una lista tecnica de Pokemon detectados con nombre, coordenadas, CP, nivel, stats, ventana de aparicion y enlace de Google Maps

Esta prueba sirve para validar que el endpoint responde correctamente y que el parseo base del proyecto funciona de forma independiente antes de usar `discord_bot.py`.

## Ejemplos de uso

```text
/pokemon nombre:wiglett cantidad:3
/coords nombre:pikachu cantidad:5
```

## Como invitar el bot a tu servidor

1. Abre tu aplicacion en el [Discord Developer Portal](https://discord.com/developers/applications).
2. Ve a `OAuth2` > `URL Generator`.
3. Marca los scopes `bot` y `applications.commands`.
4. Concede permisos como `View Channels`, `Send Messages`, `Embed Links` y `Read Message History`.
5. Abre el enlace generado y selecciona tu servidor.

## Que subir a GitHub

Sube estos archivos:

- `discord_bot.py`
- `moonani_client.py`
- `test_pokelist_limpio.py`
- `requirements.txt`
- `.env.example`
- `.gitignore`
- `README.md`

No subas estos archivos:

- `.env` porque contiene tu token
- `__pycache__/` y archivos `*.pyc`
- `test_pokelist.py` si quieres mantener el repositorio limpio y sin borradores

## Mejoras futuras

- Agregar busqueda por numero de Pokedex y por rango de CP
- Permitir publicar alertas automaticas en un canal especifico
- Anadir tests unitarios para el parseo del endpoint
- Manejar mejor paises faltantes o banderas invalidas devueltas por Moonani
- Crear paginacion para listas largas dentro de Discord
- Agregar Docker para despliegue sencillo
- Permitir configuracion por servidor usando una base de datos ligera
- Anadir logs estructurados y manejo de reintentos ante errores del endpoint

## Notas

- El parametro `pokemons` del endpoint no filtra de forma fiable por nombre parcial, por eso el filtrado principal se hace del lado del bot.
- El endpoint devuelve fragmentos HTML en varios campos, asi que el cliente limpia esos datos antes de mostrarlos.
- Los comandos slash se simplificaron para usar solo `nombre` y `cantidad`, porque en este endpoint el filtro practico siempre gira alrededor de spawns 100 IV.
- Si Moonani no devuelve pais, el bot muestra `Unknown`. Puedes activar `MOONANI_RESOLVE_COUNTRIES=true` para intentar resolver el pais desde las coordenadas usando reverse geocoding.
- El endpoint publico de Nominatim puede devolver `429 Too Many Requests` si recibe demasiadas consultas. Para un bot publico, lo ideal es usar un geocoder propio, uno autoalojado o un proveedor con cuota adecuada.

## Licencia

Antes de publicarlo como codigo abierto, te conviene agregar una licencia. Si quieres algo simple y permisivo, `MIT` suele ser una buena opcion.
