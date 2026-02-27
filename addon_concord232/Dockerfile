# https://developers.home-assistant.io/docs/add-ons/configuration#add-on-dockerfile
ARG BUILD_FROM
FROM $BUILD_FROM

# jq is used by run.sh to read /data/options.json
RUN apk add --no-cache jq

# Install directly from the GitHub repo so local fixes are always included.
# Update the version label below to bust Docker's layer cache on each release.
RUN echo "concord232==0.15.9" && \
    pip3 install --no-cache-dir \
    "https://github.com/r26D/concord232/archive/refs/heads/main.tar.gz"

COPY run.sh /
RUN chmod a+x /run.sh

CMD ["/run.sh"]
