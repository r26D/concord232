# https://developers.home-assistant.io/docs/add-ons/configuration#add-on-dockerfile
ARG BUILD_FROM
FROM $BUILD_FROM

ARG CONCORD232_VERSION=0.15.1

# jq is used by run.sh to read /data/options.json
RUN apk add --no-cache jq

# Python and pip are pre-installed in the base-python image
RUN pip3 install --no-cache-dir "concord232==${CONCORD232_VERSION}"

COPY run.sh /
RUN chmod a+x /run.sh

CMD ["/run.sh"]
