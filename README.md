# Plataforma web Colaborativa

Este Trabajo de Fin de Grado se centra en el desarrollo de una plataforma web de trabajo colaborativo para la gestión de archivos y tareas tanto de manera individual como entre grupos de trabajo, utilizando tecnologías modernas y escalables, además de manteniendo unas buenas prácticas de desarrollo de software, intentando generar una buena base para posibles evoluciones del proyecto.

## Autor
Álvaro Díez Sáenz

## Tutor
Rubén Ruiz González

## Despliegue

Para el despliegue se ha probado el servicio "GITPOD", pero durante el uso se descubrió que este solo permitía un uso durante 50 horas.
https://5000-ads1010-tfgplataformawe-k5ny3kagqls.ws-eu115.gitpod.io/

Así que finalmente la aplicación se encuentra desplegada en un VPS personal.
http://185.166.215.219/

## Instalación

Para realizar la instalación en un entorno local se puede seguir todo el manual de instalación disponible en los Anexos del trabajo.

### Prerrequisitos

Se recomienda tener instalados los siguientes programas en tu sistema:
- Python 3.10
- Pip (Gestor de paquetes de Python)
- Virtualenv

### Instalación

Vamos a enfocar la instalación para Windows. Los pasos serán muy similares en Linux, pero con los comandos apropiados.

1. Clonar repositorio
 ```bash
    git clone https://github.com/ads1010/TFG-Plataforma-web-colaborativa
    cd TFG-Plataforma-web-colaborativa
```
2. Recomendable Crear entorno virtual
 ```bash
    python -m venv ./venv
 ```

3. Activar el entorno virual
```bash
   venv\Scripts\activate  # Para Windows
```

4. Instalar dependencias
```bash
   pip install -r requirements.txt
```

5. Ejecución
```bash
python app.py
```

## Licencia

Este proyecto se encuentra bajo la Licencia MIT. Puedo consultar el archivo [LICENSE](LICENSE).

| Permissions | Limitations | Conditions |
| --- | --- | --- |
| ✔️ Commercial use | ❌ Liability | ℹ️ License and copyright notice |
| ✔️ Modification | ❌ Warranty |  |
| ✔️ Distribution |  |  |
| ✔️ Private use |  |  |

## Contacto
Para cualquier consulta o sugerencia, por favor contacta a [ads1010@alu.ubu.es](mailto:ads1010@alu.ubu.es).
