FROM ubuntu:14.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends software-properties-common && add-apt-repository -y ppa:webupd8team/java && \
    apt-get update && \
    (echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | sudo /usr/bin/debconf-set-selections) && \
    apt-get install --no-install-recommends -y oracle-java8-installer && \
    rm -rf /var/cache/oracle-jdk8-installer && \
    echo "networkaddress.cache.ttl=60" >> /usr/lib/jvm/java-8-oracle/jre/lib/security/java.security && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME /usr/lib/jvm/java-8-oracle

RUN groupadd -g 1000 elasticsearch && useradd elasticsearch -u 1000 -g 1000

# https://artifacts.elastic.co/GPG-KEY-elasticsearch
RUN apt-key adv --keyserver pgp.mit.edu --recv-keys 46095ACC8548582C1A2699A9D27D666CD88E42B4 

# https://www.elastic.co/guide/en/elasticsearch/reference/current/setup-repositories.html
# https://www.elastic.co/guide/en/elasticsearch/reference/5.0/deb.html
RUN set -x \
	&& apt-get update && apt-get install -y --no-install-recommends apt-transport-https && rm -rf /var/lib/apt/lists/* \
	&& echo 'deb https://artifacts.elastic.co/packages/5.x/apt stable main --keyserver https://pgp.mit.edu/' > /etc/apt/sources.list.d/elastic-5.x.list

ENV ELASTICSEARCH_VERSION 5.0.0

RUN set -x \
	&& apt-get update \
	&& apt-get install -y --no-install-recommends elasticsearch=$ELASTICSEARCH_VERSION \
	&& rm -rf /var/lib/apt/lists/*

ENV PATH /usr/share/elasticsearch/bin:$PATH

WORKDIR /usr/share/elasticsearch

RUN set -ex \
	&& for path in \
		./data \
		./logs \
		./backups \
		./config \
		./config/scripts \
	; do \
		mkdir -p "$path"; \
		chown -R elasticsearch:elasticsearch "$path"; \
	done

COPY logging.yml /usr/share/elasticsearch/config/
COPY elasticsearch.yml /usr/share/elasticsearch/config/

USER elasticsearch

CMD ["elasticsearch"]

EXPOSE 9200 9300