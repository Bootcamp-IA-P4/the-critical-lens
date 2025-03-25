# The Critical Lens

![Django](https://img.shields.io/badge/Django-5.1.7-green.svg)
![Tailwind](https://img.shields.io/badge/Tailwind-3.4-blue.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-latest-blue.svg)
![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)

![Vista de la página principal](static/img/Macbook-Pro-16-2110x1286_critical_lens.png)

## ⚠️ Aviso Legal

**Este proyecto es exclusivamente para fines educativos y de investigación.** La extracción de datos (scraping) implementada en este proyecto tiene como único objetivo el estudio académico y la práctica del desarrollo de software, sin fines comerciales. 

No se pretende violar los términos de servicio de ningún sitio web. Los datos extraídos no se redistribuyen ni se utilizan con fines comerciales. El desarrollador no se hace responsable del mal uso que se pueda hacer de estas herramientas.

Cualquier entidad que considere que sus derechos están siendo vulnerados puede contactar con el desarrollador para solicitar la eliminación del contenido correspondiente.

## 📝 Descripción

**The Critical Lens** es una aplicación web desarrollada con Django y Tailwind CSS que ayuda a los usuarios a combatir la desinformación mediante herramientas basadas en el pensamiento crítico. En la era digital, donde la información fluye sin control, discernir la verdad se ha vuelto más difícil que nunca. Este proyecto ofrece:

- **Analizador de Credibilidad**: Evalúa automáticamente la credibilidad de noticias y contenidos usando parámetros de verificación de hechos y principios del pensamiento crítico.
- **Estadísticas de Desinformación**: Análisis de datos sobre casos verificados de desinformación para comprender mejor el panorama actual y desarrollar herramientas de evaluación crítica efectivas.
- **Base de Datos de Verificación**: Sistema de scraping que extrae y almacena verificaciones de hechos del portal Newtral para su análisis.

Esta aplicación se basa en los conceptos y herramientas del pensamiento crítico desarrollados por la Fundación para el Pensamiento Crítico (Dr. Richard Paul y Dra. Linda Elder), cuya guía se encuentra en el directorio `/docs` del proyecto. Los criterios de análisis implementados en el servicio `ContentAnalysisService` se han desarrollado siguiendo los estándares intelectuales universales y elementos del pensamiento descritos en esta guía.

## 🚀 Tecnologías

- **Backend**: Django 5.1.7
- **Frontend**: Tailwind CSS 3.4
- **Base de datos**: PostgreSQL
- **Web Scraping**: Selenium, BeautifulSoup4
- **Testing**: Pytest
- **Infraestructura**: Docker & Docker Compose

## 🔧 Instalación

El proyecto puede instalarse mediante Docker (recomendado) o de forma manual.

### Opción 1: Instalación con Docker (recomendada)

Esta opción proporciona un entorno completo y aislado con todas las dependencias necesarias, incluyendo PostgreSQL, Tailwind CSS y ChromeDriver para los tests.

#### Requisitos previos
- Docker y Docker Compose instalados en tu sistema

#### Pasos para instalación con Docker

1. Clonar el repositorio
   ```bash
   git clone https://github.com/tuusuario/the-critical-lens.git
   cd the-critical-lens
   ```

2. Crear archivo de configuración
   ```bash
   cp .env.example .env
   ```
   
   El archivo `.env` debe contener las siguientes variables para funcionar con Docker:
   ```
   # Django settings
   SECRET_KEY=django-insecure-your-secure-key-here
   DEBUG=True
   ALLOWED_HOSTS=127.0.0.1,localhost
   
   # Database settings
   DB_NAME=critical_lens
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_HOST=db    # Importante: usar 'db' para conectar con la base de datos en Docker
   DB_PORT=5432
   ```

3. Iniciar los contenedores
   ```bash
   # Iniciar la base de datos
   docker-compose up -d db
   
   # Iniciar el entorno de desarrollo de Django y Tailwind
   docker-compose up -d dev
   ```

4. Acceder a la aplicación
   La aplicación estará disponible en http://localhost:8000/

#### Comandos útiles para Docker

```bash
# Ver logs de la aplicación
docker-compose logs -f dev

# Extraer artículos de Newtral (limit=5)
docker-compose exec dev python manage.py scrape_newtral --limit 5

# Crear superusuario para el panel de administración
docker-compose exec dev python manage.py createsuperuser
```

#### Alternancia entre bases de datos

El proyecto permite alternar fácilmente entre usar la base de datos en Docker o una base de datos local/externa:

1. Para usar la base de datos en Docker:
   ```
   # Abre el archivo .env y asegúrate de que contenga esta línea:
   DB_HOST=db
   ```

2. Para usar una base de datos local/externa:
   ```
   # Abre el archivo .env y cambia la configuración a:
   DB_HOST=localhost    # O la dirección IP/hostname de tu base de datos externa
   ```

3. Después de cambiar el archivo .env, reinicia los contenedores:
   ```bash
   docker-compose restart dev
   ```

Esta configuración te permite desarrollar con flexibilidad, usando la base de datos en Docker cuando quieres un entorno completamente autocontenido, o conectándote a una base de datos externa cuando sea necesario.

### Opción 2: Instalación manual

Si prefieres una instalación sin Docker, sigue estos pasos:

1. Asegúrate de tener los requisitos previos:
   - Python 3.8+
   - PostgreSQL
   - Node.js y NPM (para Tailwind CSS)
   - Chrome WebDriver (para el scraping con Selenium)

2. Clonar el repositorio
   ```bash
   git clone https://github.com/tuusuario/the-critical-lens.git
   cd the-critical-lens
   ```

3. Crear y activar entorno virtual
   ```bash
   python -m venv venv
   # En Windows
   venv\Scripts\activate
   # En macOS/Linux
   source venv/bin/activate
   ```

4. Instalar dependencias
   ```bash
   pip install -r requirements.txt
   ```

5. Configurar variables de entorno
   ```bash
   cp .env.example .env
   ```
   
   El archivo `.env` debe contener:
   ```
   # Django settings
   SECRET_KEY=django-insecure-your-secure-key-here
   DEBUG=True
   ALLOWED_HOSTS=127.0.0.1,localhost
   
   # Database settings
   DB_NAME=critical_lens
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_HOST=localhost    # Importante: usar 'localhost' para instalación manual
   DB_PORT=5432
   ```

6. Configurar base de datos PostgreSQL
   ```bash
   # Crear base de datos en PostgreSQL
   createdb critical_lens
   ```

7. Aplicar migraciones
   ```bash
   python manage.py migrate
   ```

8. Configurar Tailwind CSS
   ```bash
   cd theme/static_src
   npm install
   cd ../..
   python manage.py tailwind start
   ```

9. Ejecutar servidor de desarrollo
   ```bash
   python manage.py runserver
   ```

10. Crear superusuario (opcional)
    ```bash
    python manage.py createsuperuser
    ```

La aplicación estará disponible en http://127.0.0.1:8000/

## 🔍 Uso

### Analizador de Credibilidad

El analizador evalúa diferentes aspectos de un contenido siguiendo los principios del pensamiento crítico:

1. **Título**: Verifica la longitud y estructura del título, evaluando su claridad y precisión.
2. **Autor**: Verifica la credibilidad de la fuente, aplicando criterios de autoridad y confiabilidad.
3. **Contenido**: Analiza el lenguaje empleado, buscando palabras sensacionalistas o emocionalmente cargadas que puedan indicar sesgo o manipulación.
4. **Fuente**: Compara con una base de datos de fuentes de mayor y menor credibilidad, basada en el historial de verificación de hechos.

Cada uno de estos aspectos recibe una puntuación y retroalimentación detallada, generando una evaluación global de la credibilidad del contenido.

URL: `/analyzer/`

### Estadísticas de Desinformación

Visualiza datos sobre la desinformación verificada a partir de los artículos fact-check del portal Newtral, incluyendo:
* Distribución por categorías de verificación
* Fuentes más frecuentes de contenido verificado
* Temáticas más comunes de desinformación

URL: `/statistics/`

## 🤖 Scraping y Tests

### Ejecutar el scraper

```bash
# Con Docker:
docker-compose exec dev python manage.py scrape_newtral --limit 10

# Sin Docker:
python manage.py scrape_newtral --limit 10 
```

### Ejecutar los tests

```bash
# Con Docker - todos los tests:
docker-compose run --rm test

# Con Docker - tests específicos:
docker-compose run --rm test pytest -v apps/scraper/tests/test_base_scraper.py
docker-compose run --rm test pytest -v apps/scraper/tests/test_user_agent_rotation.py
docker-compose run --rm test pytest -v apps/scraper/tests/test_newtral_scraper.py

# Sin Docker - todos los tests:
pytest -v apps/scraper/tests/

# Sin Docker - tests específicos:
pytest -v apps/scraper/tests/test_base_scraper.py
pytest -v apps/scraper/tests/test_user_agent_rotation.py
pytest -v apps/scraper/tests/test_newtral_scraper.py
```

## 📚 Estructura del proyecto

El proyecto sigue una arquitectura modular orientada a buenas prácticas de desarrollo Django:

```
the-critical-lens/
├── apps/                        # Aplicaciones Django (estructura modular)
│   ├── analyzer/                # App de análisis de credibilidad
│   │   ├── services.py          # Servicio de análisis de contenido
│   │   ├── templates/           # Plantillas HTML
│   │   ├── views.py             # Vistas
│   │   └── ...
│   ├── dashboard/               # App de inicio y dashboard
│   │   ├── templates/           # Plantillas HTML
│   │   ├── views.py             # Vistas
│   │   └── ...
│   └── scraper/                 # App de scraping de fact-checks
│       ├── management/          # Comandos personalizados
│       ├── migrations/          # Migraciones de base de datos
│       ├── models.py            # Modelos de datos
│       ├── scrapers/            # Implementaciones de scrapers
│       │   ├── base.py          # Scraper base
│       │   └── newtral.py       # Scraper para Newtral
│       ├── services.py          # Servicio de scraping
│       ├── utils/               # Utilidades (logging, user agents, etc.)
│       ├── views.py             # Vistas (estadísticas)
│       └── ...
├── core/                        # Configuración principal de Django
│   ├── settings.py              # Configuración del proyecto
│   ├── urls.py                  # URLs del proyecto
│   └── ...
├── docs/                        # Documentación del proyecto
│   └── miniguia_pensamiento_critico.pdf  # Guía que fundamenta los criterios de análisis
├── templates/                   # Plantillas globales
│   └── base.html                # Plantilla base
├── theme/                       # Configuración de Tailwind CSS
│   └── static_src/              # Archivos fuente para Tailwind
├── static/                      # Archivos estáticos para producción
│   └── img/                     # Imágenes del proyecto
├── docker-compose.yml           # Configuración de Docker Compose
├── Dockerfile                   # Configuración de la imagen Docker
├── .env_example                 # Ejemplo de variables de entorno
├── .gitignore                   # Archivos ignorados por Git
├── manage.py                    # Script de administración de Django
├── pytest.ini                   # Configuración de Pytest
└── requirements.txt             # Dependencias del proyecto
```

Esta estructura sigue buenas prácticas de desarrollo Django, con clara separación de responsabilidades y organización modular.

## 📄 Modelos de datos

### Diagrama de la base de datos

La siguiente imagen muestra la estructura relacional de la base de datos:

[Ver diagrama de la base de datos](https://dbdiagram.io/d/67e1377a75d75cc8443a3b7d)

Esta estructura permite gestionar eficientemente tanto las categorías de verificación como los artículos extraídos mediante el scraper.

### VerificationCategory

Almacena las categorías de verificación utilizadas para clasificar los fact-checks.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| name | CharField | Nombre de la categoría (ej. "Falso", "Engañoso") |
| description | TextField | Descripción de la categoría |
| color | CharField | Código de color para representación visual |

### FactCheckArticle

Almacena artículos de verificación de hechos extraídos del portal Newtral.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| title | CharField | Título del artículo |
| url | URLField | URL única del artículo |
| publish_date | DateField | Fecha de publicación |
| verification_category | ForeignKey | Categoría de verificación |
| claim | TextField | Afirmación verificada |
| claim_source | CharField | Fuente de la afirmación |
| content | TextField | Contenido del artículo |
| tags | CharField | Etiquetas temáticas |
| author | CharField | Autor del artículo |
| scraped_at | DateTimeField | Fecha de extracción |
| is_processed | BooleanField | Estado de procesamiento |

## ⏭️ Próximos Pasos

### Machine Learning para un Análisis Avanzado
- Implementación de modelos de NLP (Procesamiento de Lenguaje Natural) para un análisis más preciso del contenido
- Uso de APIs como OpenAI, HuggingFace o Google Cloud NLP para enriquecer el análisis
- Integración con datasets de fact-checking para entrenar modelos propios de detección de fake news
- Desarrollo de un sistema de puntuación más granular basado en técnicas de machine learning

### Mejoras de Infraestructura
- Implementación de CI/CD para pruebas automáticas y despliegue
- Despliegue en plataformas como Render o Railway para acceso público
- Ampliación de los servicios Docker para incluir entornos de producción y staging

## 👥 Contribuir

Si deseas contribuir a este proyecto, por favor:

1. Haz un fork del repositorio
2. Crea una rama para tu funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. Haz commit de tus cambios (`git commit -am 'Añade nueva funcionalidad'`)
4. Sube la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📜 Licencia

Este proyecto está licenciado bajo la Licencia MIT