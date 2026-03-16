# Plan: Testing, análisis estático, anotaciones de tipo y cobertura

## 1. Testing

- **Mantener** los tests actuales en `bn/tests.py` (unittest + Django `TestCase`); ya hay 19 tests que pasan.
- **Añadir** un runner/config unificado vía **pyproject.toml** para poder ejecutar tests con `pytest` o `python -m pytest` (opcional, si se añade pytest-django) o dejar solo `python manage.py test bn`.
- **Dependencias**: añadir en `requirements-dev.txt` (o en `[project.optional-dependencies]` del pyproject):
  - `pytest-django` (para poder usar `pytest` con Django y `--ds=batalla_naval.settings`)
  - `coverage` / `pytest-cov` (ver sección 4)

Configuración mínima en **pyproject.toml** (o **pytest.ini**):
- `DJANGO_SETTINGS_MODULE = batalla_naval.settings`
- Opciones de pytest: `addopts = -v`, `testpaths = bn`, `python_files = tests.py`

---

## 2. Análisis estático

- **Ruff**: lint + formateo en un solo tool (sustituye flake8, isort, etc.).
  - Configuración en **pyproject.toml** bajo `[tool.ruff]` y `[tool.ruff.format]`.
  - Reglas: línea 88, excluir migraciones y `.venv`; habilitar reglas habituales (E, F, I, B, C4, UP).
  - Formato: comillas dobles, indent 4.
- **mypy**: comprobación de tipos.
  - Configuración en **pyproject.toml** bajo `[tool.mypy]` o en **mypy.ini**.
  - Usar el plugin **django-stubs** (`django-stubs`) para modelos y vistas Django.
  - Opciones: `strict` opcional; `ignore_missing_imports` para terceros si hace falta; excluir `migrations/`.

Dependencias de desarrollo:
- `ruff`
- `mypy`
- `django-stubs` (y `types-*` si se usan)

Comandos objetivo:
- `ruff check .` y `ruff format .`
- `mypy bn batalla_naval` (excluyendo migrations)

---

## 3. Anotaciones de tipo

Añadir anotaciones de forma incremental en los módulos que más aporten:

- **bn/views.py**
  - Tipar vistas: `request: HttpRequest` y retorno `HttpResponse | HttpResponseRedirect`.
  - Usar `from django.http import HttpRequest, HttpResponse, HttpResponseRedirect`.
- **bn/decoradores.py**
  - Tipar el decorador: `vista: Callable[..., HttpResponse | HttpResponseRedirect]` y retorno del wrapper con el mismo tipo (o usar `Callable[..., Any]` si se prefiere menos estricto).
- **bn/forms.py**
  - Métodos `clean_*` y `clean()`: anotar retorno (p. ej. `int`, `str`, `dict` según el campo).
- **bn/celda.py**
  - `Celda.__init__`: anotar parámetros (x, y: int; barco opcional como tupla; bools).
  - `__eq__(self, other: object) -> bool`, `__hash__(self) -> int`.
  - Propiedades `texto` y `render`: `-> str`.
  - `es_vecino(self, other: Celda) -> bool` si existe.
- **bn/fields.py**
  - `from_db_value`, `to_python`, `get_prep_value`: anotar valor de entrada y salida (Any o más específico según el tipo almacenado).
- **bn/excepciones.py**
  - Las excepciones pueden quedarse sin anotar o anotar `__init__` donde tengan argumentos (p. ej. `RadarUsado2VecesContra`).
- **bn/models.py**
  - Métodos públicos que devuelven bool, int, list, dict: anotar retorno (p. ej. `def debe_iniciarse(self) -> bool`).
  - No hace falta anotar cada campo del modelo si mypy con django-stubs los infiere.

Orden sugerido: `excepciones` → `celda` → `fields` → `decoradores` → `forms` → `views` → `models` (parcial).

---

## 4. Cobertura de tests

- **Herramienta**: `coverage.py` con el plugin Django (o `pytest-cov` si se usa pytest).
- **Configuración** en **pyproject.toml** bajo `[tool.coverage.run]` y `[tool.coverage.report]`:
  - `source = bn, batalla_naval`
  - `omit = */migrations/*, .venv/*`
  - Branch coverage opcional.
- **Comando**:
  - `coverage run -m django test bn --settings=batalla_naval.settings` (o `coverage run -m pytest bn -p no:warnings` si se usa pytest).
  - `coverage report` y `coverage html` para informe en terminal y HTML.
- **Umbral opcional**: fallar si la cobertura está por debajo de un mínimo (p. ej. 70–80 %) con `coverage report --fail-under=70` (o equivalente en pytest-cov).

Añadir a **requirements-dev.txt** (o optional-deps): `coverage`, `pytest-cov` (si se usa pytest).

---

## 5. Estructura de archivos a crear/tocar

| Acción | Archivo |
|--------|---------|
| Crear | `pyproject.toml` (metadata, ruff, mypy, coverage, pytest) |
| Crear | `requirements-dev.txt` (ruff, mypy, django-stubs, coverage, pytest-django, pytest-cov) |
| Modificar | `bn/views.py` (anotaciones) |
| Modificar | `bn/decoradores.py` (anotaciones) |
| Modificar | `bn/forms.py` (anotaciones) |
| Modificar | `bn/celda.py` (anotaciones) |
| Modificar | `bn/fields.py` (anotaciones) |
| Modificar | `bn/excepciones.py` (anotaciones mínimas) |
| Modificar | `bn/models.py` (anotaciones en métodos clave) |
| Opcional | `.gitignore`: `htmlcov/`, `.coverage`, `.mypy_cache/` |

---

## 6. Orden de implementación sugerido

1. Añadir **pyproject.toml** con ruff, mypy, coverage y pytest (opcional).
2. Añadir **requirements-dev.txt** e instalar dependencias de desarrollo.
3. Configurar **Ruff** y ejecutar `ruff check .` y `ruff format .`; corregir salidas.
4. Añadir **anotaciones de tipo** módulo a módulo (excepciones → celda → fields → decoradores → forms → views → models).
5. Configurar **mypy** (y django-stubs); corregir errores hasta que `mypy bn batalla_naval` sea limpio o se documenten excepciones.
6. Configurar **coverage**; ejecutar tests con cobertura y generar reporte; opcionalmente añadir `--fail-under` en CI o en un script local.

Si indicas que priorizas solo algunas de estas partes (por ejemplo solo ruff + cobertura, sin mypy), se puede acotar el plan.
