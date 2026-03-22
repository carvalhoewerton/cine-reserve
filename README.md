# CineReserve API 🎬

API RESTful para gerenciamento do **Cinépolis Natal**, desenvolvida com Django REST Framework. O sistema permite gerenciar filmes, salas, sessões, reservas de assentos e geração de ingressos com foco em integridade de dados e controle de concorrência.

---

## 🛠️ Tecnologias

- Python 3.12
- Django 6.0
- Django REST Framework
- PostgreSQL
- Redis (distributed lock + cache)
- Celery + Celery Beat (tarefas assíncronas)
- JWT (SimpleJWT)
- Docker + Docker Compose
- Poetry

---

## 🚀 Instalação

### Pré-requisitos

- Docker
- Docker Compose
- Poetry

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd cinereverse
```

### 2. Crie um arquivo `.env` com as credenciais necessárias

Crie um arquivo `.env` na raiz do projeto e defina suas próprias credenciais:
```env
POSTGRES_DB=your_db_name
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
DB_HOST=db
DB_PORT=5432
SECRET_KEY=your_secret_key
DEBUG=True
EMAIL_HOST_USER=your_gmail@gmail.com
EMAIL_HOST_PASSWORD=your_gmail_app_password
```

> Para o envio de emails via Gmail, gere uma **senha de app** em `myaccount.google.com → Segurança → Senhas de app`.

### 3. Suba os containers

```bash
docker compose up --build
```

Isso irá subir automaticamente:
- PostgreSQL
- Redis
- Django (web)
- Celery Worker
- Celery Beat

### 4. Crie um superusuário (staff)

```bash
docker exec -it cinereverse-web-1 python manage.py createsuperuser
```

---

## 📖 Documentação Swagger

A documentação interativa da API está disponível via **Swagger UI**. Com ela você pode visualizar todos os endpoints, seus parâmetros, schemas de request/response e testá-los diretamente no navegador.

```
http://localhost:8000/api/docs/
```

Para acessar endpoints protegidos no Swagger:
1. Faça login em `POST /auth/token/` e copie o `access` token
2. Clique em **Authorize** no topo da página
3. Digite `Bearer <seu_token>` e confirme

---

## 📋 Visão Geral do Sistema

O fluxo correto de uso da API segue esta ordem:

```
1. [STAFF] Criar filmes
2. [STAFF] Criar salas
3. [STAFF] Criar sessões (seats são gerados automaticamente)
4. [USER]  Se cadastrar        → CASE 1
5. [USER]  Fazer login         → CASE 1
6. [USER]  Listar filmes       → CASE 2
7. [USER]  Listar sessões      → CASE 3
8. [USER]  Ver mapa de assentos → CASE 4
9. [USER]  Reservar assento(s) → CASE 5
10. [USER] Fazer checkout      → CASE 6
11. [USER] Ver meus ingressos  → CASE 7
```

> **Nota:** Ao criar uma sessão, os assentos são gerados automaticamente baseados no layout da sala. Tipo `basic` = 5x10 = 50 assentos, tipo `vip` = 3x10 = 30 assentos.

---

## 🔐 Autenticação — CASE 1

O sistema utiliza **JWT (JSON Web Tokens)** para autenticação. Após o login, inclua o token em todas as requisições protegidas.

### Cadastro
```
POST /users/
```
```json
{
    "username": "ewerton",
    "email": "ewerton@email.com",
    "password": "123456"
}
```

### Login
```
POST /auth/token/
```
```json
{
    "username": "ewerton",
    "password": "123456"
}
```

Retorna:
```json
{
    "access": "eyJ...",
    "refresh": "eyJ..."
}
```

Inclua o `access` token nas requisições protegidas:
```
Authorization: Bearer eyJ...
```

### Refresh do token
```
POST /auth/token/refresh/
```
```json
{
    "refresh": "eyJ..."
}
```

---

## 📡 Endpoints

### 👤 Usuários

| Método | Endpoint | Auth | Descrição |
|--------|----------|------|-----------|
| POST | `/users/` | ❌ | Cadastrar usuário |
| GET | `/users/` | ✅ | Listar usuários |
| GET | `/users/{id}/` | ✅ | Detalhe do usuário |
| DELETE | `/users/{id}/` | ✅ | Deletar usuário |

---

### 🎬 Filmes — CASE 2

> **CASE 2:** Qualquer usuário, autenticado ou não, pode ver a lista de filmes disponíveis com sessões ativas.

| Método | Endpoint | Auth | Descrição |
|--------|----------|------|-----------|
| GET | `/movies/` | ❌ | **[CASE 2]** Listar filmes com sessões ativas |
| POST | `/movies/` | ✅ Staff | Criar filme |
| GET | `/movies/{id}/` | ❌ | Detalhe do filme |
| DELETE | `/movies/{id}/` | ✅ Staff | Deletar filme |

**Criar filme (Staff):**
```
POST /movies/
```
```json
{
    "name": "Stalker",
    "duration": 160,
    "genre": "Drama",
    "director": "Andrei Tarkovsky",
    "description": "A long walk to the philosophy"
}
```

---

### 🏠 Salas

> Salas precisam ser criadas antes das sessões. O layout de assentos é definido pelo tipo da sala.

| Método | Endpoint | Auth | Descrição |
|--------|----------|------|-----------|
| GET | `/rooms/` | ❌ | Listar salas |
| POST | `/rooms/` | ✅ Staff | Criar sala |

**Tipos de sala:**
- `basic` → 5 fileiras x 10 assentos = 50 assentos
- `vip` → 3 fileiras x 10 assentos = 30 assentos

**Criar sala (Staff):**
```
POST /rooms/
```
```json
{
    "name": "Sala 1",
    "type": "basic"
}
```

---

### 🎭 Sessões — CASE 3

> **CASE 3:** Qualquer usuário, autenticado ou não, pode ver as sessões disponíveis para um filme específico.

| Método | Endpoint | Auth | Descrição |
|--------|----------|------|-----------|
| GET | `/sessions/movie/{movie_id}/` | ❌ | **[CASE 3]** Sessões por filme |
| POST | `/sessions/` | ✅ Staff | Criar sessão |
| GET | `/sessions/{id}/seats/` | ✅ | **[CASE 4]** Mapa de assentos |
| POST | `/sessions/{id}/seats/{seat_id}/reserve/` | ✅ | **[CASE 5]** Reservar assento |

**Criar sessão (Staff):**
```
POST /sessions/
```
```json
{
    "movie_id": 1,
    "room_id": 1,
    "starts_at": "19/03/2026 18:00"
}
```

> O campo `ends_at` é calculado automaticamente baseado na duração do filme. A API valida automaticamente conflitos de horário na mesma sala.

---

### 🪑 Mapa de Assentos — CASE 4

> **CASE 4:** O sistema distingue entre assentos Disponíveis, Reservados (lock temporário) e Comprados.

```
GET /sessions/{id}/seats/
```

Retorna todos os assentos com status:
- `available` → disponível para reserva
- `hold` → temporariamente reservado (lock de 10 minutos via Redis)
- `purchased` → comprado permanentemente

---

### 🔒 Reserva de Assentos — CASE 5

> **CASE 5:** Ao selecionar um assento, o sistema cria um lock temporário de 10 minutos via Redis, impedindo outros usuários de selecioná-lo durante o checkout.

```
POST /sessions/{session_id}/seats/{seat_id}/reserve/
```

- Requer autenticação JWT
- Cria um lock temporário de 10 minutos via Redis
- O assento fica com status `hold`
- Se o checkout não for realizado em 10 minutos, o Celery libera o assento automaticamente

---

### 🎟️ Checkout e Ingressos — CASE 6 e 7

> **CASE 6:** O sistema processa a reserva temporária e a transforma em um registro permanente no banco de dados. Um ingresso digital único é gerado e vinculado à conta do usuário.
>
> **CASE 7:** Usuários autenticados podem listar todos os seus ingressos comprados.

| Método | Endpoint | Auth | Descrição |
|--------|----------|------|-----------|
| POST | `/tickets/checkout/` | ✅ | **[CASE 6]** Gerar ingressos |
| GET | `/tickets/my-tickets/` | ✅ | **[CASE 7]** Meus ingressos |

**Checkout:**
```
POST /tickets/checkout/
```

- Processa todas as reservas ativas do usuário
- Gera um ingresso para cada assento reservado
- Envia email de confirmação automaticamente via Celery
- Remove os locks do Redis

**Response:**
```json
{
    "message": "1 ticket(s) successfully generated",
    "data": [
        {
            "id": 1,
            "user_name": "ewerton",
            "movie_name": "Stalker",
            "movie_duration": 160,
            "session_starts_at": "19/03/2026 18:00",
            "room_name": "Sala 1",
            "seat_label": "A5"
        }
    ]
}
```

---

## ⚙️ Tarefas Automáticas (Celery)

| Task | Intervalo | Descrição |
|------|-----------|-----------|
| `release_expired_seats` | 60s | Libera assentos com reservas expiradas automaticamente |
| `send_ticket_email` | On demand | Envia email de confirmação após checkout |

---

## 🔒 Segurança

- **Rate Limiting** → limita 100 requests/dia para usuários não autenticados e 1000/dia para autenticados
- **JWT Authentication** → tokens de curta duração com refresh token
- **SQL Injection** → prevenido automaticamente pelo Django ORM
- **CSRF Protection** → middleware ativo por padrão
- **Input Validation** → validação via serializers do DRF

---

## 🧪 Testes

```bash
# Rodar todos os testes
docker exec -it cinereverse-web-1 python manage.py test

# Rodar testes de um app específico
docker exec -it cinereverse-web-1 python manage.py test apps.user

# Rodar com detalhes
docker exec -it cinereverse-web-1 python manage.py test --verbosity=2
```
