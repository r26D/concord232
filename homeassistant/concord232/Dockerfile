ARG BUILD_FROM
FROM $BUILD_FROM

ARG CONCORD232_VERSION=0.15.1

RUN apk add --no-cache python3 py3-pip jq

RUN pip3 install --no-cache-dir "concord232==${CONCORD232_VERSION}"

COPY run.sh /
RUN chmod a+x /run.sh

CMD ["/run.sh"]
