# Creación del íncide con los datos de los Requerimientos agroecológicos

Se utiliza el [Bulk API de Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/2.3/docs-bulk.html) , el endpoint al que llamar es _bulk, primero indexamos los documentos tal cual están en la base de datos original, utilizando las claves como _id
Como estamos utilizando ficheros, usaremos el --data-binary en lugar del -d que utilizamos habitualmente, es decir, en orden ejecutamos:

```
curl -XDELETE "elastic_endpoint/osc"
curl -s -XPOST "elastic_endpoint/osc/requirements/_bulk" --data-binary "@curl_requirements_inicial.js"
curl -s -XPOST "elastic_endpoint/osc/requirements/_bulk" --data-binary "@curl_altitud.js"
```
Sustituyendo `elastic_endpoint` por la url de la base de datos que estamos utilizando, por ejemplo `http://localhost:9200`
# Modificación de las coordenadas de algunas estaciones de inforiego incorrectas

Se utiliza Kibana Sense para ejecutar las sentenias Query DSL en [update_inforiego_stations.qdsl](OpenSmartCountry/resources/data/update_inforiego_stations.qdsl)