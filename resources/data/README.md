# Creación del íncide con los datos de los Requerimientos agroecológicos

Se utiliza el [Bulk API de Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/2.3/docs-bulk.html) , el endpoint al que llamar es _bulk, primero indexamos los documentos tal cual están en la base de datos original, utilizando las claves como _id
Como estamos utilizando ficheros, usaremos el --data-binary en lugar del -d que utilizamos habitualmente, es decir, en orden ejecutamos:

```
curl -s -XPOST https://search-opensmartcountry-trmalel6c5huhmpfhdh7j7m7ey.eu-west-1.es.amazonaws.com/osc/requirements/_bulk --data-binary "@curl_requirements_inicial.js"; echo

curl -s -XPOST https://search-opensmartcountry-trmalel6c5huhmpfhdh7j7m7ey.eu-west-1.es.amazonaws.com/osc/requirements/_bulk --data-binary "@curl_altitud.js"; echo
```