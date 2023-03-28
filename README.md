# RSS2fake
Generación de noticias falsas con GPT utilizando feed RSS de medios reales

Para utilizarlo, crear un fichero `../clave_API.txt` con la clave de acceso a la API de OpenAI, o bien editar el código para colocarla en la variable openai.api_key_path de cualquier otra manera (escribiéndola en los fuentes, tomándola de una variable de entorno, etc.)

Las últimas líneas del código generan las noticias falsas. Por ejemplo:

```
generar_noticia("mundomundial", 1, 20, 200)
```

Genera una noticia para el portal "El Mundo Mundial", pasándole a GPT veinte titulares elegidos al azar desde las fuentes RSS, con 200 caracteres de máximo por cada uno de ellos.

# Instrucciones

Este es un programa en Python que requiere ciertas dependencias para su correcto funcionamiento. A continuación, se detallan las instrucciones necesarias para instalar las dependencias requeridas utilizando pip.

## Dependencias

Este programa requiere las siguientes dependencias:

* feedparser
* openai
* requests
* datetime
* asyncio
* beautifulsoup4
* dominate
* Pillow
* pyppeteer

## Instalación

Asegúrese de tener pip instalado en su sistema. Puede verificar si pip está instalado ejecutando el siguiente comando en la terminal:

```
pip --version
```

Si no tiene pip instalado, siga las instrucciones en la [documentación oficial de pip](https://pip.pypa.io/en/stable/installation/) para instalarlo.

Abra una terminal y vaya al directorio raíz del proyecto.

Instale las dependencias necesarias utilizando el siguiente comando:


```
pip install feedparser openai requests datetime asyncio beautifulsoup4 dominate Pillow pyppeteer
```

Una vez que se completen todas las instalaciones, puede ejecutar el programa.

## Uso

Para utilizar este programa, simplemente ejecute el archivo `.py` que contiene el código. Por ejemplo:

```
python mi_programa.py
```

Se espera que este programa funcione correctamente después de instalar las dependencias requeridas y seguir las instrucciones proporcionadas anteriormente. Si encuentra algún problema, asegúrese de verificar que todas las dependencias estén instaladas correctamente y que esté utilizando la versión correcta de Python.
