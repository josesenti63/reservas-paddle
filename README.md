# 🎾 Sistema de Reservas de Canchas de Paddle

Aplicación web **mobile-first** desarrollada con Django para gestionar reservas
de canchas de paddle en clubes y complejos deportivos.

## Características principales

- Reserva de canchas desde el celular en pocos pasos
- Panel de administración para gestores del club
- Calendario visual de disponibilidad en tiempo real
- Autenticación de usuarios (socios)
- Integración con MercadoPago para pago online

## Tecnologías

| Capa | Tecnología |
|---|---|
| Backend | Django 5.x + Python 3.12 |
| Base de datos | PostgreSQL (producción) / SQLite (desarrollo) |
| Frontend | Django Templates + Bootstrap 5 |
| Pagos | MercadoPago SDK |
| Deploy | Railway |

---

## Instalación local

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/reservas-paddle.git
cd reservas-paddle
```

### 2. Crear y activar el entorno virtual

```bash
# Crear el entorno virtual
python -m venv venv

# Activar en Linux/Mac
source venv/bin/activate

# Activar en Windows
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus valores locales
```

### 5. Crear la base de datos y superusuario

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Ejecutar el servidor de desarrollo

```bash
python manage.py runserver
```

Abrir en el navegador: http://127.0.0.1:8000

Panel de administración: http://127.0.0.1:8000/admin

---

## Estructura del proyecto

```
reservas_paddle/          ← carpeta raíz del proyecto
│
├── config/               ← configuración principal de Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── canchas/              ← app: gestión de canchas
│   ├── models.py         ← modelos: Cancha, HorarioDisponible
│   ├── admin.py
│   └── ...
│
├── reservas/             ← app: lógica de reservas
│   ├── models.py         ← modelos: Reserva
│   ├── admin.py
│   └── ...
│
├── usuarios/             ← app: autenticación y perfiles
│   ├── models.py         ← modelo: PerfilUsuario
│   ├── admin.py
│   └── ...
│
├── templates/            ← plantillas HTML globales
├── static/               ← archivos estáticos (CSS, JS)
├── requirements.txt
├── .env.example
└── manage.py
```

---

## Modelo de datos

### Cancha
Representa una cancha física del club.

| Campo | Tipo | Descripción |
|---|---|---|
| nombre | CharField | Ej: "Cancha 1", "Cancha Central" |
| descripcion | TextField | Descripción opcional |
| activa | BooleanField | Si está disponible para reservar |
| creada_en | DateTimeField | Fecha de alta |

### HorarioDisponible
Define los bloques horarios posibles para reservar.

| Campo | Tipo | Descripción |
|---|---|---|
| hora_inicio | TimeField | Ej: 08:00 |
| hora_fin | TimeField | Ej: 09:00 |
| dias_semana | CharField | Ej: "lunes,martes,miércoles" |

### Reserva
Registro de cada reserva hecha por un usuario.

| Campo | Tipo | Descripción |
|---|---|---|
| usuario | ForeignKey → User | Quién reservó |
| cancha | ForeignKey → Cancha | Qué cancha |
| horario | ForeignKey → HorarioDisponible | Qué turno |
| fecha | DateField | Día de la reserva |
| estado | CharField | pendiente / confirmada / cancelada |
| pagado | BooleanField | Si se abonó |
| creada_en | DateTimeField | Cuándo se hizo la reserva |

### PerfilUsuario
Extiende el usuario de Django con datos del socio.

| Campo | Tipo | Descripción |
|---|---|---|
| usuario | OneToOneField → User | Vinculado al User de Django |
| telefono | CharField | Número de contacto |
| numero_socio | CharField | Número de socio del club (opcional) |

---

## Roadmap

- [x] Parte 1 — Estructura del proyecto y modelos
- [x] Parte 2 — Lógica de reservas (vistas y URLs)
- [x] Parte 3 — Interfaz mobile-first
- [x] Parte 4 — Autenticación de usuarios
- [x] Parte 5 — Pagos con MercadoPago
- [x] Parte 6 — Deploy en Railway

---

*Desarrollado como proyecto de portafolio · Django 5 · Python 3.12*

---

## Deploy en Railway

### Variables de entorno requeridas

Configurar en el panel de Railway → Variables:

| Variable | Valor |
|---|---|
| `SECRET_KEY` | Clave secreta larga y aleatoria |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `.railway.app` (Railway lo completa automáticamente) |
| `DATABASE_URL` | Railway la inyecta automáticamente al agregar PostgreSQL |

### Pasos para el deploy

1. Crear repositorio en GitHub y subir el código
2. Crear proyecto en Railway → "Deploy from GitHub repo"
3. Agregar servicio PostgreSQL desde Railway
4. Configurar las variables de entorno
5. Railway hace el deploy automáticamente
6. Crear superusuario desde la terminal de Railway:
   ```bash
   python manage.py createsuperuser
   ```

### Archivos de deploy

| Archivo | Propósito |
|---|---|
| `Procfile` | Le dice a Railway cómo arrancar el servidor |
| `runtime.txt` | Versión de Python a usar |
| `railway.toml` | Configuración de build y deploy |
| `requirements.txt` | Dependencias Python |
