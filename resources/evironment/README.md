[TOC]
##Windows
### Python
Utilizamos la última versión de Python 2 por la compatibilidad con más paquetes de análisis, se puede ver una explicación detallada en [Should I use Python 2 or Python 3 for my development activity?](https://wiki.python.org/moin/Python2orPython3)

Para instalarlo simplemente descargamos de la página oficial [Downloads en Python.org](https://www.python.org/downloads/) la última versión para Windows, actualmente la [2.7.12](https://www.python.org/ftp/python/2.7.12/python-2.7.12.msi).

Dejamos que se instale con las opciones por defecto.

Para poder ejecutarlo desde cualquier sitio se puede añadir a la variable path `C:\Python27` pero esto no permitirá trebajar con varios entornos de python a la vez.

Hay un tutorial muy interesante para aprender desde cero de las [DjangoGirls](https://djangogirls.org/) en la página [Tutorial de Django Girls](https://tutorial.djangogirls.org/es/)

#### Eclipse
Para eclipse se puede utilizar PyDev, simplemente siguiendo el manual en [PyDev.org - Manual 101 Install](http://www.pydev.org/manual_101_install.html).

Después de esto es necesario configurar el intérprete, del mismo modo siguiendo el manual [PyDev.org - Manual 101 Interpreter](http://www.pydev.org/manual_101_interpreter.html).
### Django

Podemos trabajar en un 'entorno virtual' para aislar la configuración para el proyecto.

1. Para obtener la herramienta viertualenv si tenemos instalado Python 2.7.12:
    1. Actualiza pip: [Upgrading pip](https://pip.pypa.io/en/stable/installing/#upgrading-pip) 
        Ejecuta desde la carpeta de instalación de python `python -m pip install -U pip`
    1. Instala virtualenv: [virtualenv Installation](https://virtualenv.pypa.io/en/stable/installation/)
    1. Ejecuta desde la carpeta `Scripts` en la carpeta de instalación de python `pip install virtualenv`
1. Crear el `virtualenv` en la carpeta que se quiera
	1. Se crea una carpeta con nombre en minúsculas
	1. Desde la carpeta creada se ejecuta ` python -m virtualenv myvenv` (`myenv` es el nombre que le quieras dar al entorno, mejor dejarlo corto porque se usa bastante)
	1. Este comando crea un directorio myenv que contiene el entorno virtual y lo iniciamos ejecutando: `myvenv\Scripts\activate`
1. Instalamos la versión de django correspondiente. En la [página de FAQ de django](https://docs.djangoproject.com/en/1.10/faq/install/#faq-python-version-support) podemos ver qué versiones son compatibles según nuestra versión de python.
	1. Tenemos que asegurarnos que estamos dentro del virtualenv que hemos creado, es decir que hemos ejecutado correctamente el paso anterior. Estaremos seguros sin en la consolo aparece `(myenv)` como primera palabra de la línea.
	2. Ejecutamos `pip install django==1.8`

Por ejemplo podemos crear un proyecto de prueba, para eso desde el virtualenv ejecutamos `python myvenv\Scripts\django-admin.py startproject mysite .`

##Linux
### Python
Tenemos instalado tanto Python 2 como Python 3 en el CPD1 tal cual está en la distribución Linux Mint que utilizamos, con `python --version` obtenermos la versión instalada que en este caso es la 2.7.12 y con `python3 --version` la de python 3 que en este caso es la 3.5.2

###Django
Utilizamos un entorno virtual al igual que en Windows. En este caso al ser un paquete Debian/Ubuntu es necesario previamente instalar el paquete venv.
1. Instalamos el paquete venv para python: `sudo apt-get python3-venv install` para Python 3 y `sudo apt-get install virtualenv python-virtualenv` para Python 2.
2. Desde el directorio de desarrollo creamos en entorno con `python -m virtualenv myvenv` para Python 2 o `python3 -m venv myvenv` para python 3.
3. Activamos el entorno con `source myvenv/bin/activate` y aparecerá un (myenv) al principio de la línea.
4. Instalamos Django desde el entorno con `pip install django==1.9`
5. Creamos un proyecto de prueba con `django-admin startproject mysite .` que crea toda la estructura necesaria
6. Modificamos la configuración cambiando el huso horario por `TIME_ZONE='Europe/Berlin` editando el archivo correspondiente con `pico mysite/settings.py` y añadiendo al final una entrada llamada `STATIC_ROOT = os.path.join(BASE_DIR, 'static')`.
7. Generamos una base de datos con `python manage.py migrate`
8. Levantamos el servidor con `python manage.py runserver`


##Servers
###CPD1
* **2016/10/03** Sistema opegativo instalado [Linux Mint 18 Sarah Cinnamon 64-bit](Linux Mint 18 Sarah) con la configuración por defecto. El equipo cuenta con un solo disco duro de estado sólido, está pendiente poner otro para los datos, de momento con la instalación tiene utilizado un 5%, es decir unos 98GB libres.
___
1. **2016/10/04** `sudo apt-get update` para actualizar la lista de paquetes disponibles y sus versiones
1. **2016/10/04** `sudo apt-get ugrade`para actualizar todos los paquetes (se tira un ratito...)
1. **2016/10/04** Instalamos [OpenSSH](http://www.openssh.com/) para poder acceder a la máquina 
	1. Comprobamos los paquetes instalados con `dpkg -l`
	1. Instalamos openssh-server `sudo apt-get install openssh-server`. Con esto ya se puede acceder a la máquina por SSH, por ejemplo usando [Putty](http://www.putty.org/)
	1. Cambiamos algunas configuraciones para que sea un pelín más seguro:
		1. Cambiamos el puerto SSH 	para que al conectarse sea neceario especificar el puerto, editamos el archivo de configuración con `sudo nano /etc/ssh/sshd_config` y cambiamos el puerto en la línea `Port 22`.
		2. Desactivamos el acceso root, será necesario acceder con usuario y luego cambiar a su. Para ello editamos el archivo de configuración con `sudo nano /etc/ssh/sshd_config` y cambiamos `PermitRootLogin prohibit-password` por `PermitRootLogin no`
3. **2016/10/04** Desde el escritorio aceptamos la actualización del *Update Manager*, luego la de todos los paquetes que aparecen con actualizaciones y por último la del *kernel* hasta que dejamos el sistema como *Your system is up to date*.
4. **2016/10/04** Instalamos Git siguiendo la documentación oficial [Getting Started - Installing Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git). Simplemente ejecutamos `sudo apt-get install git-all`

###Base de datos
Actualmente la base de datos que utilizamos está en Amazon AWS, hay más información al respecto en [resources/data](https://github.com/teanocrata/OpenSmartCountry/tree/master/resources/data)