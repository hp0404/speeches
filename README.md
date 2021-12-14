# speeches

This repository contains FastAPI & SQLModel API hosted on DigitalOcean's droplet.

## Usage (local development)

Before running docker-compose, make sure you have 
`.env` file with database credentials stored in 
the root directory. 

```console
docker-compose -f docker-compose.prod.yml up -d --build
```