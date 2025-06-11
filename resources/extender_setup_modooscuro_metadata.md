# 🛠️ Ampliación de tabla `setups` en Babelcomics

## 1. Código Python (SQLAlchemy)

```python
from sqlalchemy import Column, Boolean

# Dentro de la clase Setup (ya definida con Base)
# Agregar estos campos:

modoOscuro = Column(Boolean, nullable=False, default=False)
actualizarMetadata = Column(Boolean, nullable=False, default=False)
```

---

## 2. SQL para migración manual (SQLite)

```sql
-- Ejecutar esto en SQLite para agregar las columnas si ya tenés datos existentes:

ALTER TABLE setups ADD COLUMN modoOscuro BOOLEAN NOT NULL DEFAULT 0;
ALTER TABLE setups ADD COLUMN actualizarMetadata BOOLEAN NOT NULL DEFAULT 0;
```
