# Rust Workspace — Aplicaciones Oficiales de ChurrOS

Este directorio contiene el workspace de **Cargo** con todas las aplicaciones oficiales de ChurrOS desarrolladas en **Rust** utilizando **`gtk4-rs`** y **`libadwaita-rs`**.

---

## 📦 Estructura del Workspace

```text
rust/
├── Cargo.toml                 # Configuración del workspace y perfil release (LTO, strip)
├── Cargo.lock
├── churros-welcome/           # App de bienvenida (binario: churros-welcome)
├── preferences/               # Centro de configuración (binario: churros-settings)
├── popups/                    # Popups nativos del panel (binario: churros-popup)
├── control-center/            # Centro de control rápido (binario: churros-control-center)
└── services/                  # Librería compartida (churros_services)
```

---

## 🚀 Crates del Workspace

| Crate | Binario resultante | `deploy` | Descripción |
| :--- | :--- | :--- | :--- |
| **[`churros-welcome`](churros-welcome/)** | `/usr/bin/churros-welcome` | `true` | Pantalla de bienvenida al inicio del sistema Live con accesos rápidos. |
| **[`preferences`](preferences/)** | `/usr/bin/churros-settings` | `true` | Panel de configuración del sistema (33 páginas GTK4 dedicadas). |
| **[`popups`](popups/)** | `/usr/bin/churros-popup` | `true` | Popups nativos (audio, red, bluetooth, brillo, batería, power) con toggle por PID. |
| **[`control-center`](control-center/)** | `/usr/bin/churros-control-center`| `true` | Menú desplegable de ajustes rápidos con sliders y conmutadores. |
| **[`services`](services/)** | `libchurros_services.rlib` | `false` | Capa backend de integración con `wpctl`, `nmcli`, `bluetoothctl`, etc. |

---

## 🛠️ Compilación y Despliegue

Los binarios se compilan automáticamente durante la construcción de la ISO mediante [`scripts/build-rust.sh`](../scripts/build-rust.sh):

```bash
# Compilar todo el workspace en modo release:
cargo build --release --manifest-path rust/Cargo.toml

# O mediante la CLI general:
./churros build
```

El script copia los ejecutables de los crates que tengan `deploy = true` en su `Cargo.toml` directamente a `archiso/airootfs/usr/bin/`.

---

## 🧪 Desarrollo Local y Vista Previa

Para probar cualquier aplicación en la máquina del desarrollador sin construir la ISO ni alterar la configuración del sistema anfitrión, utiliza la herramienta de vista previa:

```bash
# Abrir apps individuales en modo preview aislado:
./churros apps welcome
./churros apps settings
./churros apps control-center
./churros apps popup audio
./churros apps popup network
```

En este modo, la variable de entorno `CHURROS_DEV=1` intercepta y cancela cualquier comando del sistema que intente modificar volumen, conexiones de red o energía, registrándolo en stderr de forma segura.

---

## 📖 Documentación Relacionada

- [Guía de Aplicaciones Oficiales](../docs/apps.md)
- [Documentación del Panel de Preferencias](../docs/preferences.md)
- [Documentación de Popups](../docs/popups.md)
- [Documentación de la Capa de Servicios](../docs/services.md)
