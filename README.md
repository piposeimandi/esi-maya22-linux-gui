# ESI Maya22 Controller

This project provides a graphical interface to control the ESI Maya22 hardware via terminal commands. The interface allows you to adjust input and output volumes, enable/disable monitoring and headphones, and synchronize output volumes. Configuration is automatically saved to a JSON file.

## Executable Information

The `maya22-control` executable used in this project comes from the [rabits/esi-maya22-linux](https://github.com/rabits/esi-maya22-linux) repository. However, I have optionally included a modified `maya22-control` file that adds an additional option to disable headphones, which the original version does not support.

It is recommended to use the modified executable included in this repository to take advantage of this additional functionality. However, if you prefer to use the original executable, you can download it from the mentioned repository, although you will lose the option to disable headphones.

## Features

- Adjust input volumes (left and right).
- Adjust output volumes (left and right).
- Automatic synchronization of output volumes.
- Enable and disable monitoring.
- Enable and disable headphones.
- Select input channel.
- Automatic configuration saving in a JSON file.

## Requirements

- Python 3.x
- Tkinter (generally included with Python)
- `maya22-control` executable in the same directory as this script

## Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/tu_usuario/tu_repositorio.git
    ```

2. Navigate to the project directory:
    ```bash
    cd tu_repositorio
    ```

3. Ensure the `maya22-control` executable is accessible:
    - Use the modified executable included in this repository.
    - If you choose to use the original executable, download it from the [rabits/esi-maya22-linux](https://github.com/rabits/esi-maya22-linux) repository.
    - Place the executable in the same directory as the Python script.
    - Ensure it is executable:
      ```bash
      chmod +x maya22-control
      ```

## Usage

1. Run the Python script:
    ```bash
    python controlador_esi_maya22.py
    ```

2. The graphical interface will open, and you will be able to adjust volumes, enable/disable monitoring and headphones, and select the input channel.

## Configuration

Configuration is saved in a JSON file named `config.json` in the same directory as the script. Settings are automatically loaded from this file when the application starts.

### Configuration File

The `config.json` file contains the following parameters:

- `headphones_enabled`: Headphones status (0 or 1).
- `monitoring_enabled`: Monitoring status (0 or 1).
- `input_vol_left`: Input volume left (0-127).
- `input_vol_right`: Input volume right (0-127).
- `output_vol_left`: Output volume left (0-145).
- `output_vol_right`: Output volume right (0-145).
- `input_channel`: Selected input channel (`mic`, `hiz`, `line`, `mic_hiz`, `mute`).

## Known Issues

- If you encounter any issues running the commands, make sure that `maya22-control` is correctly located and executable.

## Contributions

Contributions are welcome. If you find any bugs or have improvements to propose, please open an issue or a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact

For any questions or comments, please contact [bajosega@gmail.com](mailto:bajosega@gmail.com).



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
