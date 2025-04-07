#Importaciones

import feedparser
import os
import openai
import random
import requests
import re
import locale
import datetime
import asyncio
from bs4 import BeautifulSoup
from dominate import document
from dominate.tags import *
from PIL import Image, ImageOps
from io import BytesIO
from pyppeteer import launch




### Definiciones

# Clave de OpenAI. Se debe generar en el portal del usuario de OpenAI, y ponerla en una variable de entrono "openai.api_key"
openai.api_key_path = "../clave_API.txt"
# Define las locales en español para que la fecha se genere correctamente
locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
# Versión de GPT a utilizar. Si tenemos acceso a gpt-4 se puede usar, aunque habría que afinar los prompts para sacarle partido
#gpt_version = "gpt-3.5-turbo"
gpt_version = "gpt-4"
# Temática que se debe incluir cualquier noticia. Por defecto, no se especifica ninguna.
tematica_obligatiorias = ""



# Función de generación de noticias
# - Abreviatura_servicio: Identificador del servicio a generar (mundomundial, sinconciencia, lamonclia, vidaextrana)
# - Número de noticias falsas a generar
# - Número de noticias reales de los feed RSS que le vamos a mandar a GPT
# - Máximo de caracteres que vamos a coger por noticia
# Según la versión de GPT hay un máximo de tokens a pasarle, así que debemos limitar estos parámetros.
# Además, el coste de la petición será más alto cuantos más tokens utilicemos.

def generar_noticia(abreviatura_servicio, num_noticias, num_noticias_rss, max_caracteres_noticia_rss):
  with open("../clave_API.txt", "r") as f:
    api_key = f.read().strip()
  client = openai.OpenAI(api_key=api_key)
    
  # Definir la URL y el tipo del feed RSS
  # - urls : listado de URLs a consultar (se leen completas, y luego se barajan y se eligen las num_noticias_rss primeras)
  # - tipo_servicio : descripción a alto nivel de qué generador de fake news queremos (un periódico, una web oficial, un blog de videojuegos...)
  # - cuenta_twitter : identificador de la cuenta de Twitter, para que aparezca como marca de agua.
  # - informacion_adicional : un párrafo que se añade a la petición de la notifica falsa, donde se dan más detalles de lo que queremos.
  
  if abreviatura_servicio == 'mundomundial':
    # ElMundoMundial
    urls = {
      'https://e00-elmundo.uecdn.es/elmundo/rss/internacional.xml',
      'https://e00-elmundo.uecdn.es/elmundo/rss/economia.xml',
      'https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada'
      'https://e00-elmundo.uecdn.es/elmundo/rss/portada.xml',
      'https://www.europapress.es/rss/rss.aspx',
      'https://api2.rtve.es/rss/temas_noticias.xml'
      }
    tipo_servicio = "un periódico generalista de España (actualidad, nacional, internacional, deportes, economía, sociedad...)"
    nombre_servicio = 'El Mundo Mundial'
    cuenta_twitter = 'MundoMundial_IA'
    informacion_adicional = ""
    
  elif abreviatura_servicio == 'sinconciencia':
    # SinConCiencia
    urls = {'https://feedpress.me/naukas',
      'https://www.museosdetenerife.org/coffeebreak/?feed=rss2',
      'https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/ciencia/portada',
      'https://e00-elmundo.uecdn.es/elmundo/rss/portada.xml'}
    tipo_servicio = "una web que difunde falsas noticias de ciencia (negacionismo científico, antivacunas, conspiranoia, illuminati, pseudociencia, terapias alternativas, física, química, actualidad científica, educación...)}"
    nombre_servicio = 'SinConCiencia'
    cuenta_twitter = 'SinConCienciaIA'
    informacion_adicional = "Puedes hacer noticias negacionistas, o noticias falsas de ciencia que resulten ridículas"
    
  elif abreviatura_servicio == 'lamonclia':
    # La MonclIA
    urls = {
      'https://www.lamoncloa.gob.es/paginas/rss.aspx?tipo=2',
      'https://www.lamoncloa.gob.es/paginas/rss.aspx?tipo=1',
      'https://portal.mineco.gob.es/es-es/comunicacion/_layouts/15/listfeed.aspx?List=%7BDE1040A8%2D90D1%2D4F24%2D9455%2D423894813206%7D&Source=/es-es/comunicacion/Paginas/Forms/AllItems.aspx',
      'https://www.sanidad.gob.es/gabinete/notap_rss.do',
      'https://www.defensa.gob.es/comun/rssChannel/rssNotasPrensa.xml'
      }
    tipo_servicio = 'la web oficial de noticias del gobierno de España (ministerios, gobierno, política, presidente, ministros, diputados...)'
    nombre_servicio = 'LaMonclIA'
    cuenta_twitter = 'laMoncl_IA'
    informacion_adicional = "El titular de la noticia debe hacer mención específica a algún organismo oficial o político español. La noticia debe parecer promocional del gobierno presentándose como un logro o evento relevante, pero a la vez divertida y absurda."
    
  elif abreviatura_servicio == 'vidaextrana':
    # VidaExtraña
    urls = {'https://vandal.elespanol.com/xml.cgi',
      'https://www.vidaextra.com/feedburner.xml',
      'https://www.eurogamer.es/feed',
      'https://www.3djuegos.com/feedburner.xml',
      'https://e00-elmundo.uecdn.es/rss/tecnologia/videojuegos.xml'
      }
    tipo_servicio = 'una web de noticias de videojuegos (hardware gaming, consolas, móviles, Nintendo, Xbox, Playstation, VR, juegos de mesa, cultura popular...)'
    nombre_servicio = 'VidaExtraña'
    cuenta_twitter = 'VidaExtrana_IA'
    informacion_adicional = "además de noticias de videojuegos como tales, puedes generar noticias sobre hardware para videojuegos (tarjetas gráficas, teclados, ratones, etc.) o sobre el mundo del gaming en general"
    

  # Añade la fecha actual al tipo de servicio para intentar que nos dé más información de actualidad

  tipo_servicio = f"{tipo_servicio} con información del {datetime.date.today().strftime('%d de %B de %Y')}"

  # Crear la ruta si no existe, para que cada la información de cada servicio se genere en una subcarpeta
  ruta = abreviatura_servicio
  if not os.path.exists(ruta):
    os.makedirs(ruta)

  # Comienza a crear la conversación
  mensaje=[]
  prompt_inicial=f"Eres el listado de titulares de {tipo_servicio}"
  mensaje.append({"role": "system", "content": prompt_inicial})
  #print(f"PROMPT INICIAL --> {prompt_inicial}")


  # Analizar el feed RSS utilizando la biblioteca feedparser, creando una lista de noticias en formato "TITULAR: xxxxx, TEXTO: xxxxxxxxx"
  # Trunca el texto de las noticias a max_caracteres_noticia_rss caracteres
  noticias=[]
  for url in urls:
    feed = feedparser.parse(url)
    for entry in feed.entries:
        noticia_titular=entry.title
        noticia_texto=BeautifulSoup(entry.description, "html.parser").get_text()
        noticias.append(f"TITULAR: {noticia_titular}, TEXTO: {noticia_texto[:max_caracteres_noticia_rss]}")
    #print(f"- Leídas noticias del RSS ({url}).")

  # Baraja las noticias y le pasa las primeras num_noticias_rss a GPT
  random.shuffle(noticias)
  for noticia in noticias[:num_noticias_rss]:
    mensaje.append({"role": "assistant", "content": noticia })
    #print (f"   -{noticia}")

  # Genera tantas noticias como le hayamos pedido
  for noticia_generada in range(num_noticias):

    #Generar el titular
    prompt_gpt = f"Inventa una nueva noticia irónica y divertida que sirva como continuación del listado anterior. Escribe con un toque de humor ácido y parodia. Escribe solo un titular de una línea. {informacion_adicional}"
    if tematica_obligatiorias:
      prompt_gpt += "La noticia debe además tener esta temática concreta: " + tematica_obligatiorias
    #print(f"PROMPT2 --> {prompt_gpt}")
    mensaje.append( {"role": "user", "content": prompt_gpt} )
    completion = client.chat.completions.create(
        model=gpt_version,
        messages=mensaje
    )
    titular_noticia=completion.choices[0].message.content

    #Si el titular contiene TEXTO, TITULAR, comillas, o puntos finales, lo elimina.
    print("----NOTICIA GENERADA----")
    titular_noticia=re.sub("TITULAR DE LA NOTICIA: ", "", titular_noticia)
    titular_noticia=re.sub("TITULAR: ", "", titular_noticia)
    titular_noticia=re.sub("ENTRADILLA: ", "", titular_noticia)
    titular_noticia=re.sub("TEXTO.*", "", titular_noticia)
    titular_noticia=re.sub(r"\.$", "", titular_noticia)
    titular_noticia=re.sub('^\"|\"$', "", titular_noticia)
    print(f"TITULAR --> {titular_noticia}")

    #Generar la entradilla (le pedimos que la entradilla tenga unos 200 caracteres)
    mensaje.append( {"role": "user", "content": f"TITULAR DE LA NOTICIA: '{titular_noticia}\n\nTEXTO (unos 200 caracteres): "} )
    completion = client.chat.completions.create(
        model=gpt_version,
        messages=mensaje
    )
    entradilla_noticia=completion.choices[0].message.content
    print(f"ENTRADILLA --> {entradilla_noticia}")

    #Generar el prompt para Dall-E 2
    mensaje.append( {"role": "user", "content": f"TITULAR DE LA NOTICIA: '{titular_noticia}\n\nPROMPT PARA ENVIARLE A DALL-E 2 (texto completamente en inglés, compuesto por tokens de una o dos palabras separados por comas, añadir como token que el estilo sea fotográfico detallado y realista, evitar palabras conflictivas o malsonantes). No hace falta generar la imagen, solo el prompt): "} )
    completion = client.chat.completions.create(
        model=gpt_version,
        messages=mensaje
    )
    prompt_noticia=completion.choices[0].message.content
    print(f"PROMPT -> {prompt_noticia}")

    #Generar un nombre de fichero con un sufijo aleatorio
    nombre_fichero=f"{abreviatura_servicio}_{random.randint(10000000, 99999999)}"

    #Generar la imagen
    try:
        response = client.images.generate(
          model="dall-e-3",
          prompt=prompt_noticia,
          n=1,
          size="1024x1024"
        )
        imagen_url = response.data[0].url
        response = requests.get(imagen_url)
        imagen = Image.open(BytesIO(response.content))
        imagen.save(f"{ruta}/{nombre_fichero}.png")
        print(f"IMAGEN -> {nombre_fichero}.png")
    except Exception as e:
        # Si no la ha podido generar (habitualmente, porque tiene personajes públicos o texto que considere ofensivo, nos avisa para que la creemos a mano)
        print("****** ERROR AL GENERAR LA IMAGEN:", e)

    # Creamos el documento HTML.
    doc = document(title=titular_noticia)
    with doc.head:
        link(rel='stylesheet', href='../noticias.css')
        link(rel='stylesheet', href=f'../{abreviatura_servicio}.css')
    with doc:
        h1(nombre_servicio)
        with div(cls='cabecera'):
            img(src=f'{nombre_fichero}.png',alt=f'{prompt_noticia}')
            h3(f'@{cuenta_twitter}')
            h2(titular_noticia)
        p(entradilla_noticia)
        with div(cls='pie'):
            p("Noticia generada utilizando inteligencias artificiales sin intervención humana.")
            p("Cualquier tipo de contenido ofensivo o inadecuado que pueda aparecer no ha sido en ningún momento intencionado.")

    #Guardarlo en disco
    with open(f'{ruta}/{nombre_fichero}.html', 'w') as f:
        f.write(doc.render())
    print(f"HTML -> {nombre_fichero}.html")

#     Genera automáticamente una captura de pantalla de la web, utilizando un navegador interno
#     Comentado porque es aún una opción experimental
#
    #Capturar la pantalla
##    asyncio.get_event_loop().run_until_complete(capturar(abreviatura_servicio,f"{nombre_fichero}.html"))
    
##    #Recortar la captura
##    captura_de_pantalla = Image.open(f"{abreviatura_servicio}/captura_tmp.png")
##    captura_de_pantalla_gris = captura_de_pantalla.convert('L')
##    captura_de_pantalla_invertida = ImageOps.invert(captura_de_pantalla_gris)
##    contornos = captura_de_pantalla_invertida.getbbox()
##    captura_de_pantalla_recortada = captura_de_pantalla.crop(contornos)
##    captura_de_pantalla_recortada.save(f"{abreviatura_servicio}/{nombre_fichero}_captura.png")

    #Borrar el temporal
##    os.remove(f"{abreviatura_servicio}/captura_tmp.png")
    
    print(f"CAPTURA_RECORTADA -> {nombre_fichero}_captura.png")

    print("----TERMINADO----")


# Función auxiliar para la captura de pantalla

##async def capturar(abreviatura_servicio,archivo):
##    # Crear una instancia del navegador
##    browser = await launch()
##    # Crear una nueva página
##    page = await browser.newPage()
##    await page.setViewport({'width': 640, 'height': 1280})
##    # Navegar a la página que deseas capturar
##    nombre_archivo =  f'{abreviatura_servicio}/{archivo}'
##    url_completa = f"file://{os.path.abspath(nombre_archivo)}"
##    await page.goto(url_completa)
##    # Tomar una captura de pantalla y guardarla en un archivo
##    await page.screenshot({'path': f'{abreviatura_servicio}/captura_tmp.png'})
##    # Cerrar el navegador
##    await browser.close()


# BUCLE PRINCIPAL

# Genera las noticias (abreviatura, número de noticias a generar, número de noticias a seleccionar de las fuentes RSS, número de caracteres a coger de cada noticia)

# Si especificamos esta variable, todas las noticias tendrán la temática indicada
#tematica_obligatiorias = "Star Wars"

generar_noticia("mundomundial", 1, 20, 200)
generar_noticia("vidaextrana", 1, 20, 200)
generar_noticia("lamonclia", 1, 20, 200)
generar_noticia("sinconciencia", 1, 20, 200)
