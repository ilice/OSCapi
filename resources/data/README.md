# Base de datos
## Elastic Search
Utilizamos inicialmente Elastic Search, en particular utilizaremos [Amazon Elasticsearch Service](https://aws.amazon.com/es/elasticsearch-service/). 
Empezamos con la capa gratuita de AWS *(The AWS Free Tier includes usage of up to 750 hours per month of a t2.micro instance type and up to 10 GB of Magnetic or General Purpose EBS storage. Lean more. [Amazon Elasticsearch Service Free Tier](http://aws.amazon.com/free/). All T2 instance types need EBS storage.)*

Para configurar el dominio seguimos la guía que proporciona Amazon: Getting Started with Amazon Elasticsearch Service Domains](http://docs.aws.amazon.com/es_es/elasticsearch-service/latest/developerguide/es-gsg.html).

En el momento de creación del dominio, AWS soporta las versiones 1.5 y 2.3 de Elastic Search. La última versión estable de Elasticsearch es la 2.4.1.

Básicamente para tener los datos necesitamos:
1. Tener una cuenta en AWS
1. Crear un Amazon ES domain
1. Configurar una política de acceso al Amazon ES domain
1. Cargar los datos

##Creación del Amazon ES domain
Una vez estamos conetados a la consola de Amazon, en la sección Analytics seleccionamos **Elasticsearch Service**. Si no tenemos ningun Amazon ES domain creado previamente aparece un botón para crear un nuevo Amazon ES domain que nos guía a través de la creación.
1. **Define domain**: Como nombre del dominio utilizamos `opensmartcountry` y como versión la `2.3`
2. **Configure cluster**: PAra utilizar la capa gratuita creamos `1` instancia del tipo `t2.micro.elasticsearch` con almacenamiento tipo `ESB`, volumen tipo `Magnetic` y tamaño `10`Gb, el resto con la configuración por defecto.
3. **Setup access policy**: Utilizamos el acceso por IP que es la configuración más sencilla y con un nivel de seguridad aceptable para lo que estamos haciendo. Simplemente introducimos las IP que queremos que tengan acceso separadas por comas, en particular las de las oficinas para el desarrollo y las del hosting para que la página pueda cargar los datos.
4. **Review**: pulsamos siguiente

En unos 10 minutos tenemos la instancia funcionando: https://search-opensmartcountry-trmalel6c5huhmpfhdh7j7m7ey.eu-west-1.es.amazonaws.com/
##Modificación de las IP con acceso al Amazon ES domain
Es necesario acceder con un IAM user con permisos para poder realizar esta acción, se accede a través de la [Consola de Administración de AWS](https://aws.amazon.com/es/console/), se selecciona dentro de los servicios (en eu-west-1) el Elasticsearch Service, después el domain `opensmartcountry`, se pulsa sobre **Modify access policy** y se añade la nueva ip en la lista `"aws:SourceIp"`.
##Carga de datos
### Creación del íncide con los datos de los Requerimientos agroecológicos
Se utiliza el [Bulk API de Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/2.3/docs-bulk.html) , el endpoint al que llamar es _bulk, primero indexamos los documentos tal cual están en la base de datos original, utilizando las claves como _id
Como estamos utilizando ficheros, usaremos el --data-binary en lugar del -d que utilizamos habitualmente, es decir, en orden ejecutamos:
```
curl -XDELETE "elastic_endpoint/osc"
curl -s -XPOST "elastic_endpoint/osc/requirements/_bulk" --data-binary "@curl_requirements_inicial.js"
curl -s -XPOST "elastic_endpoint/osc/requirements/_bulk" --data-binary "@curl_altitud.js"
```
Sustituyendo `elastic_endpoint` por la url de la base de datos que estamos utilizando, por ejemplo `http://localhost:9200`
### Estaciones de inforiego
Las estaciones de inforiego se indexan en el index `inforiego`con el type `info_riego_station` ejecutando desde un navegador `.../inforiego_rest.php?accion=actualizaEstaciones`, si el resultado es `success` la actualización se ha completado correctamente.

Previamente es necesario establecer el mapping ya que en caso contrario las coordenadas no las toma como geo_point. Para eso podemos utilizar la extensión de chrome **[Sense](https://chrome.google.com/webstore/detail/sense-beta/lhjgkmllcaadmopgmanpapmpjgmfcfig?utm_source=chrome-app-launcher-info-dialog) que básicamente pone las cosas fáciles**. Para configurarla simplemente ponemos en la barra el endpoint de elastic.

#### Mapping para las estaciones de inforiego
Desde la consola de Sense ejecutamos
```
PUT inforiego
{
    mappings : {
		info_riego_station : {
			properties : {
				ALTITUD : {
					type : "long"
				},
				ESTACION : {
					type : "string"
				},
				ESTACIONCORTO : {
					type : "string"
				},
				FECHAINSTAL : {
					type : "date",
					format : "dd/MM/yyyy"
				},
				IDESTACION : {
					type : "string"
				},
				IDPROVINCIA : {
					type : "string"
				},
				LATITUD : {
					type : "string"
				},
				LONGITUD : {
					type : "string"
				},
				X_UTM : {
					type : "string"
				},
				Y_UTM : {
					type : "string"
				},
				lat_lon : {
					type : "geo_point",
					lat_lon : true
				}
			}
		}
	}
}
```
Ahora sólo hay que ejecutar desde el navegador  `.../inforiego_rest.php?accion=actualizaEstaciones`

#### Modificación de las coordenadas de algunas estaciones de inforiego incorrectas

Algunas de las estaciones de inforiego tienen mal las coordenadas en origen, se ha reportado el problema pero de momento no lo han solucionado por lo que es necesario ejecutar (desde el Sense es una buena opción) las sentenias Query DSL en [update_inforiego_stations.qdsl](OpenSmartCountry/resources/data/update_inforiego_stations.qdsl)

#### Mapping para los datos diarios de inforiego
```
PUT inforiego/_mapping/info_riego_daily
{
	properties : {
		AÑO : {
			type : "long"
		},
		DIA : {
			type : "long"
		},
		DIRVIENTO : {
			type : "double"
		},
		DIRVIENTOVELMAX : {
			type : "double"
		},
		ETBC : {
			type : "double"
		},
		ETHARG : {
			type : "double"
		},
		ETPMON : {
			type : "double"
		},
		ETRAD : {
			type : "double"
		},
		FECHA : {
			type : "date",
			format : "dd/MM/yyyy"
		},
		HORMINHUMMAX : {
			type : "date",
			format : "HHmm"
		},
		HORMINHUMMIN : {
			type : "date",
			format : "HHmm"
		},
		HORMINTEMPMAX : {
			type : "date",
			format : "HHmm"
		},
		HORMINTEMPMIN : {
			type : "date",
			format : "HHmm"
		},
		HORMINVELMAX : {
			type : "date",
			format : "HHmm"
		},
		HUMEDADD : {
			type : "double"
		},
		HUMEDADMAX : {
			type : "double"
		},
		HUMEDADMEDIA : {
			type : "double"
		},
		HUMEDADMIN : {
			type : "double"
		},
		IDESTACION : {
			type : "string"
		},
		IDPROVINCIA : {
			type : "string"
		},
		N : {
			type : "double"
		},
		PEBC : {
			type : "double"
		},
		PEHARG : {
			type : "double"
		},
		PEPMON : {
			type : "double"
		},
		PERAD : {
			type : "double"
		},
		PRECIPITACION : {
			type : "double"
		},
		RADIACION : {
			type : "double"
		},
		RECORRIDO : {
			type : "double"
		},
		RMAX : {
			type : "double"
		},
		RN : {
			type : "double"
		},
		TEMPD : {
			type : "double"
		},
		TEMPMAX : {
			type : "double"
		},
		TEMPMEDIA : {
			type : "double"
		},
		TEMPMIN : {
			type : "double"
		},
		VD : {
			type : "double"
		},
		VELVIENTO : {
			type : "double"
		},
		VELVIENTOMAX : {
			type : "double"
		},
		VN : {
			type : "double"
		},
		altitud : {
			type : "double"
		},
		lat_lon : {
			type : "geo_point",
			lat_lon : true
		}
	}
}
```

Tras tener el mapping se pueden insertar los datos utilizando la URL variando los datos de fechas y localización `.../php/inforiego_rest.php?accion=actualizaDiario&fecha_ini=01/01/2013&fecha_fin=10/01/2013&latitud=40.439983&longitud=-5.737026`

