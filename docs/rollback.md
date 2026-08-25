# Rollback

ChurrOS incluye un sistema de rollback basado en **snapshots btrfs**: antes de
cada transacción de pacman se guarda una copia del sistema que permite volver
atrás si una actualización rompe algo.

## Cómo funciona

La instalación por defecto usa btrfs con subvolúmenes:

| Mount | Subvolumen |
|-------|------------|
| `/`     | `@`    |
| `/home` | `@home` |

Los snapshots se guardan en un subvolumen contenedor `@snapshots` (creado en el
nivel superior, id=5) aislado de `@`, de modo que un snapshot nunca contiene
snapshots anidados.

- Un **hook de pacman** (`/etc/pacman.d/hooks/50-churros-snapshot.hook`,
  `PreTransaction`) crea un snapshot de `@` y `@home` **antes** de cada
  `pacman -Syu`, `-S` o `-R`. Si el snapshot falla (p. ej. el sistema no es
  btrfs), la transacción continúa igual.
- Los snapshots de `/boot` heredan el flag No_COW, así que siguen siendo
  legibles por GRUB.
- Se conservan los últimos **5** snapshots por defecto; los más antiguos se
  eliminan automáticamente.

## Comandos

La herramienta `churros-snapshot` (root) gestiona todo:

```bash
sudo churros-snapshot create [RAZON]      # snapshot manual
sudo churros-snapshot list                # lista (tabla)
sudo churros-snapshot list --json         # salida JSON (la usa la UI)
sudo churros-snapshot info <stamp>        # metadatos de un snapshot
sudo churros-snapshot delete <stamp>      # elimina un snapshot
sudo churros-snapshot cleanup [KEEP]      # borra los más antiguos hasta dejar KEEP
sudo churros-snapshot restore -d <disco> <stamp>   # restaura desde ISO live
```

El `stamp` es la fecha/hora del snapshot (`20260824-163000`).

## Restaurar

El subvolumen raíz está montado en uso, así que **no se puede restaurar desde
el sistema en marcha**. Para volver a un snapshot:

1. Arranca la ISO live de ChurrOS.
2. Abre una terminal y ejecuta (root):
   ```bash
   sudo churros-snapshot restore -d /dev/sdX <stamp>
   ```
   (`/dev/sdX` es el disco donde está instalado el sistema; se puede ver con
   `lsblk`.)
3. Reinicia: el sistema quedará en el estado del snapshot. El estado anterior
   queda resguardado como `@broken-<fecha>` (y `@home.broken-<fecha>`) por si
   hay que recuperar algo; se puede borrar después.

## Interfaz

`churros-settings` → **Actualizaciones** incluye la sección **Rollback
(snapshots btrfs)** que lista los snapshots, permite crearlos y eliminarlos, y
muestra la guía de restauración.

## Consideraciones

- Solo aplica a instalaciones **btrfs** (la opción por defecto). En ext4 el
  hook se ignora sin error.
- Los snapshots consumen espacio: con los 5 conservados y `compress=zstd:1` el
  costo típico es bajo, pero conviene revisar `sudo churros-snapshot cleanup`
  si el disco está justo.
