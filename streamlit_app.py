## ⚙️ Setup

import os
import openai
import warnings
import pandas as pd
import os
import streamlit as st
warnings.filterwarnings("ignore")
from langchain.agents import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.prompts.prompt import PromptTemplate

# Título de la página
st.set_page_config(page_title='🤖 Structural Database Search')
st.title('🤖 DataBase-SearchGPT: Asistente de Búsqueda en la Base de datos')

def read_csv_from_github(archivo):
  """
  Lee un archivo CSV que se encuentra en la carpeta main del repositorio de GitHub.

  Parámetros:
    archivo: Nombre del archivo CSV.

  Devuelve:
    DataFrame con los datos del archivo CSV.
  """


  # Obtener el URL del archivo CSV.
  url = f'https://raw.githubusercontent.com/[{archivo}]/main/{archivo}'

  # Comprobar si el archivo CSV existe.
  if not requests.head(url).ok:
    raise FileNotFoundError(f'El archivo CSV {archivo} no existe.')

  # Leer el archivo CSV.
  df_db = pd.read_csv(url)

  return df_db


#Primero se deben subir el csv que se van a utilizar como fuente de información 

df_db = read_csv_from_github('df_base.csv')

# Añadir una opción para seleccionar el modelo de openai a utilizar
model_option = st.sidebar.selectbox(
    'Selecciona un modelo:',
    ('gpt-3.5-turbo-1106','gpt-4','gpt-4-1106-preview')
)

def generate_response(df_db, user_query):
 # Crear un objeto `ChatOpenAI` con la configuración deseada.
 llm = ChatOpenAI(temperature=0, model=model_option, openai_api_key=openai_api_key, streaming=True)
 # Crear un objeto `PromptTemplate` con el formato de la respuesta deseada.
 _DEFAULT_TEMPLATE = """
 Dada una consulta del usuario {dialect}
 Sólo utiliza la información de df_db que integra df_estructuras y df_memorias 
 1. Consulta los datos similares en df_estructuras
 2. Devuelve una respuesta en español que incluya:
   - Referencias a proyectos con las condiciones exactas a la consulta de usuario en df_estructuras con id_archivo y su url de ubicación de df_memorias
   - Referencias a proyectos con las condiciones similares a la consulta de usuario en df_estructuras con id_archivo y su url de ubicación de df_memorias

 Respuesta {output}
 Pregunta {input}
 """
 PROMPT = PromptTemplate(input_variables=["input","dialect","output",],template=_DEFAULT_TEMPLATE)
 # Crear un agente `pandas_df_agent` que usa el modelo de lenguaje y el DataFrame base.
 pandas_df_agent = create_pandas_dataframe_agent(
    llm,
    df_db,
    verbose=True,
    agent_type=AgentType.OPENAI_FUNCTIONS,
    prompt_template=PROMPT,
    max_iterations=5,
    handle_parsing_errors=True,
    )

   
 response = pandas_df_agent({"input": user_query}, {"dialect": _DEFAULT_TEMPLATE}, include_run_info=True)
 result = response["output"]
 return st.success(result)


## Obtén las características de la estructura del usuario
caracteristicas_estructura = st.text_input('Ingresa las características para la búsqueda:', placeholder = 'Escribe tu consulta aquí ...')

# Agrega más información a la solicitud para una respuesta robusta
texto_ad1 = "Limítate a siempre actuar como buscador en la base de datos, además referencia proyectos usando id_archivo con las condiciones exactas de df_db en df_estructuras a la siguiente consulta de usuario :\n"
texto_ad2 = "\n O referencia proyectos usando id_archivo con alguna condición similar a la consulta de usuario de df_db en df_estructuras, referencia por id_archivo, por url y describe las características de cada proyecto referenciado"
user_query = texto_ad1 + caracteristicas_estructura + texto_ad2

# Agrega el botón de buscar
button_buscar = st.button('Buscar')

# Obtén la openai api key desde https://platform.openai.com/account/api-keys 🔑
openai_api_key = st.sidebar.text_input('Inserte su OpenAI API Key', type='password', disabled=not (caracteristicas_estructura))
if not openai_api_key.startswith('sk-'):
 st.warning('Por favor ingrese su llave OpenAI API!', icon='⚠')
if openai_api_key.startswith('sk-') and caracteristicas_estructura != '' and button_buscar.is_pressed():
 st.header('Sugerencia')
 generate_response(df_db, user_query)
 
