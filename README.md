## Uso con Docker Compose
1. Clona este repositorio
2. Ajusta las variables en `docker-compose.yml` según sea necesario
3. Ejecuta `docker-compose up -d`

## Uso con Docker
1. Clona este repositorio
2. Crea un archivo `.env` con las variables necesarias
3. Construye la imagen: `docker build -t jfa-bot .`
4. Ejecuta el contenedor: `docker run --env-file .env -d jfa-bot`


## Use with Docker Compose
1. Clone this repository
2. Adjust variables in `docker-compose.yml` as needed
3. Run `docker-compose up -d`

## Use with Docker
1. Clone this repository
2. Create a `.env` file with the necessary variables
3. Build the image: `docker build -t jfa-bot .`
4. Run the container: `docker run --env-file .env -d jfa-bot`