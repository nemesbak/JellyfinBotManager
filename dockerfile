# Usa una imagen base con Python
FROM python:3.11-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia los archivos de tu aplicación al contenedor
COPY . .

# Instala las dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Define el comando por defecto para ejecutar tu aplicación
CMD ["python", "jfa.py"]
