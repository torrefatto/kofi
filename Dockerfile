FROM python:3.8 AS builder

ADD . /src
WORKDIR /src
RUN python setup.py bdist_wheel


FROM python:3.8
ARG UID=1337
ARG GID=1337

WORKDIR /srv
COPY --from=builder /src/dist/*whl /tmp
RUN mkdir /var/kofi \
    && groupadd -g ${GID} kofi \
    && useradd -d /var/kofi -u ${UID} -g ${GID} kofi \
    && chown kofi:kofi /tmp/*whl \
 && chown kofi:kofi /var/kofi
USER kofi
RUN pip install --user /tmp/*whl \
 && rm /tmp/*whl

EXPOSE 1312

ENTRYPOINT ["/var/kofi/.local/bin/kofi"]
