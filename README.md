# Carbon Zero API

- PostgreSQL
- FastAPI (with SwaggerUI)
- Python 3.9.17
- Docker and Docker-Compose

## Development

Copy example environment file to using as main environment

```bash
cp .env.example .env
```

Run project using Docker-Compose

```bash
docker-compose up -d
```

### Info

> FastAPI with Swagger UI default port `8000` can be access through `localhost:8000/docs`
> PostgreSQL default port `5432` access through `postgresql://user:passwd@localhost:5432/esco_db` with TablePlus or other Database Management
