# speeches

[![codecov](https://codecov.io/gh/hp0404/speeches/branch/master/graph/badge.svg?token=I2DM8IGJBU)](https://codecov.io/gh/hp0404/speeches)

This repository contains FastAPI & SQLModel app hosted on DigitalOcean's droplet.

## Usage (local development)

Before running docker-compose, make sure you have 
`.env` file with database credentials stored in 
the root directory. 

```console
docker-compose -f docker-compose.prod.yml up -d --build
```