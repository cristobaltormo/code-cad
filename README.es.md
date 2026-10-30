# Code-CAD

[English](README.md) | Español

Una skill de Claude Code que diseña piezas imprimibles en 3D **verificadas**.
Pide un objeto ("un soporte de pared para mi Raspberry Pi 5", "un soporte para
un iPhone 16 Pro", "un portapilas para 4 x 18650") y:

1. **busca las medidas reales** de cada objeto implicado: base de datos
   integrada de piezas verificadas + investigación web contra planos y
   datasheets oficiales, con fuentes y nivel de confianza;
2. **explora diseños existentes** en Printables / MakerWorld / Thingiverse para
   copiar patrones que funcionan (no mallas) y evitar fallos conocidos;
3. escribe una **especificación** (`spec.json`) con medidas y tolerancias
   *antes* de modelar;
4. modela la pieza en Python con build123d (B-Rep exacto -> STEP, STL, 3MF);
5. **dos agentes independientes** (verificador dimensional y revisor de
   impresión) miden y revisan los archivos exportados en su propio contexto;
6. **libera** los STL/STEP sólo a través de una puerta que exige que todas las
   comprobaciones hayan pasado sobre los hashes exactos de esos archivos.

## Inicio rápido

```bash
./install.sh        # venv + dependencias
claude
```

```
/cad soporte de pared para una Raspberry Pi 5, PETG, Bambu P1S
```

Los resultados quedan en `projects/<nombre>/release/` junto con `RELEASE.md`
(cotas críticas medidas, orientación y ajustes de impresión, hashes).
`./install.sh --global` enlaza la skill y los agentes en `~/.claude` para usar
`/cad` desde cualquier carpeta.

## Comandos `cad`

```
cad new <nombre>          crea projects/<nombre>/ (spec.json + plantilla)
cad lookup <palabras>     medidas de referencia verificadas
cad build <proyecto>      STEP/STL/3MF, renders PNG/SVG, secciones, controles automáticos
cad verify <proyecto>     controles del spec sobre el STEP exportado
cad printability <proy.>  voladizos, puentes, paredes, contacto con la cama, chaflanes
cad measure ...           calibre virtual: bbox | holes | ray | section | clearance | walls
cad attest / status / release
```

Detalles completos, base de datos de referencia y reglas DFAM: ver
[README.md](README.md), [DFAM_GUIDE.md](DFAM_GUIDE.md) y
`.claude/skills/cad/SKILL.md`.

## Licencia

MIT. Marco original de Cristóbal Tormo.
