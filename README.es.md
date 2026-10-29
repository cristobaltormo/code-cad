# Code-CAD

[English](README.md) | Español

Marco de ingeniería Code-CAD paramétrico y skills para impresión 3D funcional con Claude Code, Antigravity y `build123d`.

Los generadores de IA tradicionales de "texto a 3D" producen mallas poligonales irregulares e imprecisas que no pueden fabricarse con tolerancias mecánicas reales. Code-CAD sustituye la aproximación por mallas por modelado paramétrico B-Rep (Boundary Representation). Mediante scripts matemáticos en Python con `build123d` (impulsado por el núcleo industrial OpenCASCADE), un agente de IA diseña piezas dimensionalmente exactas con curvas analíticas reales, interfaces normalizadas para tornillería e insertos y tolerancias de fabricación verificadas.

```
+-----------------------------------------------------------------------+
|                    PROMPT / ESPECIFICACIÓN DEL USUARIO                |
|           (Medidas de calibre, datasheets, planos técnicos)           |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                        AGENTE IA (Claude Code)                        |
|   1. Aplica reglas DFAM (múltiplos de boquilla, chaflanes, holguras)  |
|   2. Escribe el script paramétrico en Python usando build123d         |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                       EJECUCIÓN Y TOPOLOGÍA                           |
|   1. Ejecución en terminal: comprueba que sea un sólido manifold      |
|   2. Calcula caja envolvente, volumen y masa estimada (PLA/PETG)      |
|   3. Exporta STEP (curvas sin pérdida) y STL (malla poligonal)        |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                  VERIFICACIÓN VISUAL EN 4 VISTAS SVG                  |
|   1. Proyección ortográfica e isométrica con eliminación de ocultas   |
|   2. El agente inspecciona el SVG para verificar puertos y holguras   |
|   3. Autocorrige errores antes de enviar el archivo al laminador      |
+-----------------------------------------------------------------------+
```

---

## Por qué Code-CAD: De un 7/10 a un 10/10

| Aspecto | Enfoque básico con IA (7/10) | Marco de ingeniería Code-CAD (10/10) |
|---|---|---|
| **Alcance** | Limitado a carcasas básicas de chips/PCB | Universal: Carcasas, soportes mecánicos, conductos/adaptadores, clips flexibles, repuestos, Gridfinity |
| **Núcleo geométrico** | Mallas aproximadas en STL/OBJ | Sólidos B-Rep OpenCASCADE exportados a STEP (NURBS) y STL |
| **Feedback visual** | Generación a ciegas (el LLM adivina cotas) | Generador de 4 vistas técnicas en SVG con líneas ocultas para inspección visual |
| **Reglas de fabricación** | Grosor de pared fijo y genérico | Motor DFAM completo: múltiplos de boquilla, chaflán antipata de elefante, agujeros lágrima |
| **Tornillería** | Agujeros cilíndricos simples | Torres para insertos roscados de latón Ruthex (M2-M5), avellanados y tuercas cautivas |
| **Verificación** | El usuario prueba a mano en el laminador | Validación CLI automatizada: estanqueidad, volumen, peso y dimensiones de caja envolvente |

---

## Estructura del repositorio

```
code-cad/
├── .claude/
│   └── commands/
│       └── cad.md                  # Comando /cad para Claude Code
├── CLAUDE.md                       # Reglas de trabajo para Claude Code en cualquier proyecto CAD
├── SKILL.md                        # Definición portable de skill para Antigravity y agentes IA
├── DFAM_GUIDE.md                   # Manual de ingeniería: tolerancias, boquillas y contracción
├── INSTALL.md                      # Instalación del entorno y dependencias
├── pyproject.toml                  # Configuración de paquete Python
├── requirements.txt                # Dependencias (build123d, numpy, scipy)
├── cad_tools/                      # Biblioteca de utilidades paramétricas
│   ├── __init__.py
│   ├── inspect.py                  # Validador CLI, cálculo de masa y proyección de 4 vistas SVG
│   ├── fasteners.py                # Torres para insertos roscados (M2-M5), avellanados y tuercas
│   ├── joints.py                   # Pestañas snap-fit en voladizo y cierres de fricción
│   ├── features.py                 # Agujeros horizontales en lágrima y ranuras de ventilación
│   └── gridfinity.py               # Perfiles estándar de 42 mm para bandejas y cajas Gridfinity
├── prompts/                        # Biblioteca de prompts listos para usar
│   ├── 01_kickoff_master.md        # Prompt maestro para cualquier diseño 3D
│   ├── 02_electronics_enclosure.md # Prompt para placas electrónicas y sensores
│   ├── 03_structural_part.md       # Prompt para piezas mecánicas de alta carga
│   ├── 04_reverse_engineering.md   # Replicar piezas rotas con calibre y fotos
│   └── 05_adapters_and_ducting.md  # Adaptadores de manguera, aspiración y conductos
└── examples/                       # Ejemplos de referencia compilables
    ├── 01_electronics_enclosure/   # Carcasa paramétrica con torretas, USB-C y ventilación
    ├── 02_structural_l_bracket/    # Escuadra de 90 grados con nervio de refuerzo y avellanados
    ├── 03_shop_vac_adapter/        # Reductor de aspiración cónico con ajuste a presión
    └── 04_compliant_cable_clip/    # Clip de cable flexible monopieza sin soportes
```

---

## Inicio rápido

### 1. Preparar el entorno
```bash
git clone git@gitea-lan:cristobal/code-cad.git
cd code-cad

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Validar un ejemplo
Ejecuta cualquiera de los modelos de referencia para validar su geometría y generar los archivos:
```bash
python3 examples/01_electronics_enclosure/case.py
```

El script genera un informe completo en la terminal:
```markdown
### Model Inspection: enclosure_base

| Metric | Value |
|---|---|
| Bounding Box (X x Y x Z) | 60.8 x 33.8 x 16.0 mm |
| Solid Volume | 10.76 cm3 (10760.0 mm3) |
| Surface Area | 94.16 cm2 |
| Estimated Weight (PLA 100%) | 13.34 g |
| Estimated Weight (PETG 100%) | 13.67 g |
| Valid BREP Topology | Yes |
| Closed Manifold Shell | Yes |

#### Exported Files
- STEP: `exports/enclosure_base.step`
- STL: `exports/enclosure_base.stl`
- Multi-view SVG: `exports/enclosure_base_views.svg`
```

---

## Uso con Claude Code y agentes de IA

### Con Claude Code
Inicia Claude Code en este directorio:
```bash
claude
```
Ejecuta el comando `/cad`:
```
/cad Escuadra de 90 grados reforzada para fijar una fuente de alimentacion de 500g a la pared con tornillos M4
```

### En otros entornos de agentes
Copia `SKILL.md` al directorio de skills de tu agente (por ejemplo, `~/.agents/skills/code-cad/SKILL.md`) o pega el contenido de `prompts/01_kickoff_master.md` en el chat inicial.

---

## Resumen de reglas de ingeniería DFAM

Para una guía detallada, consulta [DFAM_GUIDE.md](DFAM_GUIDE.md).

- **Múltiplos de pared:** Diseña siempre las paredes como múltiplos exactos del ancho de extrusión de la boquilla (por ejemplo, 0.84 mm, 1.26 mm, 1.68 mm, 2.10 mm, 2.50 mm para boquilla de 0.4 mm).
- **Pata de elefante:** Aplica un chaflán a 45 grados de 0.8 mm en todas las aristas que toquen la cama de impresión.
- **Agujeros horizontales:** En orificios horizontales mayores de 4 mm, usa perfil de lágrima a 45 grados para evitar puentes caídos sin necesidad de soportes.
- **Alivio de tensiones:** Redondea con radio >= 2.0 mm las esquinas interiores de 90 grados para evitar concentración de tensiones y fracturas por fatiga.
- **Compensación de agujeros:** Suma entre +0.20 mm y +0.35 mm al diámetro nominal en orificios verticales para compensar la contracción térmica del plástico y el trazado poligonal.

---

## Licencia

Licencia MIT. Diseñado y mantenido por Cristóbal Tormo.
