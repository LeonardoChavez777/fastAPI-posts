FROM python:3.14.5

WORKDIR /usr/src/app
#esto es para crear un directorio de trabajo dentro del contenedor

COPY requirements.txt . 
#esto es para copiar el archivo de requerimientos al contenedor

RUN pip install --no-cache-dir -r requirements.txt
#esto es para instalar las dependencias del archivo de requerimientos

COPY . . 
#esto es para copiar todo el contenido del directorio actual al contenedor


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

