# Controlador ESI Maya22

Este proyecto proporciona una interfaz gráfica para controlar el hardware ESI Maya22 a través de comandos en la terminal. La interfaz permite ajustar volúmenes de entrada y salida, activar/desactivar el monitoreo y audífonos, y sincronizar volúmenes de salida. La configuración se guarda automáticamente en un archivo JSON.

## Información del Ejecutable

El ejecutable `maya22-control` utilizado en este proyecto proviene del repositorio [rabits/esi-maya22-linux](https://github.com/rabits/esi-maya22-linux). Sin embargo, opcionalmente he incluido un archivo `maya22-control` modificado que añade una opción adicional para deshabilitar los audífonos, cosa que la versión original no soporta.

Se recomienda utilizar el ejecutable modificado incluido en este repositorio para aprovechar esta funcionalidad adicional. No obstante, si prefieres utilizar el ejecutable original, puedes descargarlo desde el repositorio mencionado, aunque perderás la opción de desactivar los audífonos.

## Características

- Ajuste de volúmenes de entrada (izquierda y derecha).
- Ajuste de volúmenes de salida (izquierda y derecha).
- Sincronización automática de volúmenes de salida.
- Activación y desactivación del monitoreo.
- Habilitación y deshabilitación de audífonos.
- Selección de canal de entrada.
- Guardado automático de configuración en un archivo JSON.

## Requisitos

- Python 3.x
- Tkinter (generalmente incluido con Python)
- Ejecutable `maya22-control` en la misma ubicación que este script

## Instalación

1. Clona este repositorio:
    ```bash
    git clone https://github.com/piposeimandi/esi-maya22-linux-gui
    ```

2. Navega al directorio del proyecto:
    ```bash
    cd tu_repositorio
    ```

3. Asegúrate de que el ejecutable `maya22-control` sea accesible:
    - Usa el ejecutable modificado incluido en este repositorio.
    - Si decides usar el ejecutable original, descárgalo desde el repositorio [rabits/esi-maya22-linux](https://github.com/rabits/esi-maya22-linux).
    - Coloca el ejecutable en el mismo directorio que el script Python.
    - Asegúrate de que sea ejecutable:
      ```bash
      chmod +x maya22-control
      ```

## Uso

1. Ejecuta el script Python:
    ```bash
    python controlador_esi_maya22.py
    ```

2. La interfaz gráfica se abrirá y podrás ajustar los volúmenes, activar/desactivar el monitoreo y los audífonos, y seleccionar el canal de entrada.

## Configuración

La configuración se guarda en un archivo JSON llamado `config.json` en el mismo directorio que el script. Los ajustes se cargan automáticamente desde este archivo al iniciar la aplicación.

### Archivo de Configuración

El archivo `config.json` contiene los siguientes parámetros:

- `headphones_enabled`: Estado de los audífonos (0 o 1).
- `monitoring_enabled`: Estado del monitoreo (0 o 1).
- `input_vol_left`: Volumen de entrada izquierdo (0-127).
- `input_vol_right`: Volumen de entrada derecho (0-127).
- `output_vol_left`: Volumen de salida izquierdo (0-145).
- `output_vol_right`: Volumen de salida derecho (0-145).
- `input_channel`: Canal de entrada seleccionado (`mic`, `hiz`, `line`, `mic_hiz`, `mute`).

## Problemas Conocidos

- Si encuentras algún problema al ejecutar los comandos, asegúrate de que `maya22-control` esté correctamente ubicado y sea ejecutable.

## Contribuciones

Las contribuciones son bienvenidas. Si encuentras algún error o tienes mejoras para proponer, por favor abre un issue o un pull request.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para obtener más detalles.

## Contacto

Para cualquier pregunta o comentario, por favor contacta a [bajosega@gmail.com](mailto:bajosega@gmail.com).
