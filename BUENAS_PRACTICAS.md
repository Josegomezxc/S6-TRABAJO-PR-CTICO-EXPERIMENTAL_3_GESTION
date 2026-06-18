# Buenas prácticas para trabajar con control de versiones y contenedores

## 1. Convenciones de nomenclatura (Naming Conventions)

### Python / Django
- **Archivos Python**: snake_case (auth_service.py, profile_service.py)
- **Clases**: PascalCase (AuthService, ProfileService)
- **Funciones/variables**: snake_case (get_user_by_email(), login_fails)
- **Constantes**: MAYÚSCULAS con guiones bajos (LOGIN_MAX_FAILS, SESSION_IDLE_TIMEOUT_SECONDS)

### CSS
- **Archivos**: snake_case (login.css, admin_dashboard.css)
- **Selectores**: kebab-case (.user-card, .btn-primary)
- **Variables CSS**: kebab-case con -- (--ai-purple, --danger)

### JavaScript
- **Archivos**: snake_case (inbox.js, base_2.js)
- **Funciones**: camelCase (fetchNewEmails(), showToast())
- **Variables**: camelCase (newEmailCount, isLoading)

### Plantillas Django
- **Archivos**: snake_case (login.html, admin_user_detail.html)
- **Nombres de bloque**: descriptivos ({% block content %}, no {% block body %})

### Git
- **Ramas**: usar / para separar tipo/propósito:
  - feature/nueva-funcionalidad
  - fix/correccion-error
  - docs/actualizar-readme
  - refactor/mejora-rendimiento

---

## 2. Mensajes de commit (Conventional Commits)

Usar el formato estándar **Conventional Commits**:

```
<tipo>(<alcance opcional>): <descripción breve>

<cuerpo opcional>
```

### Tipos permitidos

| Tipo | Cuándo usarlo |
|------|---------------|
| feat | Nueva funcionalidad |
| fix | Corrección de bug |
| docs | Cambios en documentación |
| style | Formato, estilos (no cambia lógica) |
| refactor | Refactorización de código |
| perf | Mejora de rendimiento |
| test | Añadir o modificar tests |
| chore | Tareas de mantenimiento (config, build) |
| ci | Cambios en CI/CD |

### Ejemplos

```
feat(sandbox): add dynamic execution with strace

fix(auth): correct rate limit reset on successful login

docs: add API endpoint documentation

chore: configure Docker multi-stage build
```

### Reglas
- **Máximo 72 caracteres** en la primera línea
- **Verboso en el cuerpo**: explicar el QUÉ y el POR QUÉ, no el CÓMO
- Usar **imperativo** ("add", "fix", no "added", "fixed")
- No terminar con punto en la primera línea

---

## 3. Estrategia de ramas (Git Flow simplificado)

### Estructura

```
main (producción)
  +-- develop (integración)
        +-- feature/docker
        +-- feature/ci-cd
        +-- fix/login-error
        +-- docs/readme
```

### Flujo de trabajo

1. **main**: código listo para producción. Solo se mergea desde develop
2. **develop**: rama de integración. Aquí se fusionan todas las features
3. **feature/***: ramas para desarrollo de funcionalidades específicas
4. **fix/***: ramas para corrección de errores

### Ciclo de vida de una feature

```
git checkout develop
git checkout -b feature/mi-funcionalidad
# ... trabajar y hacer commits ...
git checkout develop
git merge feature/mi-funcionalidad
git branch -d feature/mi-funcionalidad
```

### Reglas
- **Nunca** commitear directamente en main o develop
- Siempre crear una rama específica para cada tarea
- Mantener las ramas cortas (1-2 días máximo)
- Eliminar la rama después de mergear

---

## 4. Resolución de conflictos

### Prevención
- Mantener las ramas actualizadas con develop frecuentemente:
  ```
  git checkout feature/mi-feature
  git merge develop
  ```
- Commits pequeños y enfocados
- Comunicarse con el equipo sobre qué archivos se están modificando

### Resolución

1. Identificar el conflicto:
   ```
   git status  # muestra archivos en conflicto
   ```

2. Abrir el archivo y buscar los marcadores:
   ```
   <<<<<<< HEAD
   código actual (de develop)
   =======
   código entrante (de tu rama)
   >>>>>>> feature/mi-feature
   ```

3. Editar: decidir qué versión conservar (o una combinación de ambas)

4. Eliminar los marcadores <<<<<<<, =======, >>>>>>>

5. Marcar como resuelto:
   ```
   git add <archivo>
   git commit
   ```

---

## 5. Buenas prácticas con contenedores (Docker)

### Dockerfile
- Usar imágenes base oficiales y ligeras: python:3.12-slim
- Especificar versiones exactas (FROM python:3.12-slim no FROM python:latest)
- Usar .dockerignore para excluir archivos innecesarios
- Minimizar el número de capas (RUN agrupados con &&)
- Limpiar caché de apt después de instalar (rm -rf /var/lib/apt/lists/*)
- Usar --no-cache-dir en pip
- **No ejecutar como root**: usar USER para crear un usuario no privilegiado
- Exponer solo los puertos necesarios (EXPOSE 8000)

### docker-compose.yml
- Usar la sintaxis más reciente de Docker Compose v2 (sin version:)
- Nombrar los contenedores descriptivamente (container_name: dockershield-web)
- Usar volúmenes para persistencia de datos
- Pasar configuración mediante variables de entorno (archivo .env)
- Especificar siempre command de forma explícita

### Seguridad
- No incluir secretos en el Dockerfile ni en la imagen
- Usar archivos .env locales (nunca subirlos al repositorio)
- En producción, usar un proxy reverso (nginx) y Gunicorn/uWSGI
- Escanear imágenes con herramientas como Trivy o Docker Scout

---

## 6. Integración Continua (CI/CD)

### GitHub Actions
- Ejecutar el pipeline en cada push y pull request
- Verificar que el contenedor se construye correctamente
- Usar caching de Docker Layers para builds más rápidos
- No hacer push a registries (Docker Hub) sin verificar que pase los tests

### Buenas prácticas
- Pipeline rápido (< 10 minutos)
- Un solo job por responsabilidad
- Usar matrices (matrix) para probar múltiples versiones si es necesario
- Notificar al equipo si el pipeline falla

---

## 7. Trabajo en equipo - Revisiones de código (Code Review)

### Para el autor del PR
- Hacer PR pequeños y enfocados (máximo 200-300 líneas)
- Incluir descripción clara: qué hace y por qué
- Asignar revisores específicos
- Responder a los comentarios con cambios o explicaciones

### Para el revisor
- Revisar dentro de las 24 horas hábiles
- Enfocarse en la lógica, no en el estilo (para eso están los linters)
- Ser constructivo: "¿Qué tal si movemos esto a una función separada?"
- Aprobar solo cuando esté seguro de que el código es correcto

---

## 8. Checklist antes de hacer merge a main

- [ ] ¿El código compila/ejecuta sin errores?
- [ ] ¿Pasaron todas las pruebas?
- [ ] ¿Se construye correctamente la imagen Docker?
- [ ] ¿Los mensajes de commit siguen el formato Conventional Commits?
- [ ] ¿Se eliminaron los secretos o credenciales?
- [ ] ¿La rama está actualizada con develop?
- [ ] ¿Alguien más revisó el código?
- [ ] ¿Se actualizó la documentación si es necesario?

---

*Documento generado como parte del proyecto DockerShield - UNEMI 2026*
