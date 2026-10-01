# syntax=docker/dockerfile@sha256:2780b5c3bab67f1f76c781860de469442999ed1a0d7992a5efdf2cffc0e3d769
ARG BUILD_FROM=ghcr.io/home-assistant/amd64-homeassistant-base:2026.07.0
FROM ${BUILD_FROM}

LABEL io.hass.type="core" \
    io.hass.arch="amd64" \
    io.hass.machine="qemux86-64" \
    io.hass.version="2026.11.0.dev0" \
    org.opencontainers.image.title="Remote Shelly HAOS development image" \
    org.opencontainers.image.source="https://github.com/drHouse-gif/Shelly-Remote-WebSocket-for-Home-Assistant" \
    org.opencontainers.image.revision="726a64d62c7a95bb27cec5a72163df3e1c2d822a" \
    org.opencontainers.image.licenses="Apache-2.0"

ENV S6_SERVICES_GRACETIME=240000 \
    UV_SYSTEM_PYTHON=true \
    UV_NO_CACHE=true

COPY core/rootfs /
COPY --from=ghcr.io/alexxit/go2rtc:1.9.14@sha256:675c318b23c06fd862a61d262240c9a63436b4050d177ffc68a32710d9e05bae /usr/local/bin/go2rtc /bin/go2rtc

WORKDIR /usr/src/homeassistant
COPY core/requirements.txt ./requirements.txt
COPY core/homeassistant/package_constraints.txt ./homeassistant/package_constraints.txt
COPY packaging/haos/generated/requirements-runtime.txt ./requirements-runtime.txt
RUN pip3 install --no-cache-dir "uv==0.12.20" \
    && uv pip install --no-build -r requirements.txt -r requirements-runtime.txt

COPY core/homeassistant ./homeassistant
COPY core/script ./script
COPY core/pyproject.toml core/README.rst core/LICENSE* ./
COPY aioshelly/aioshelly /opt/aioshelly/aioshelly
COPY aioshelly/pyproject.toml aioshelly/README.md aioshelly/LICENSE /opt/aioshelly/
RUN uv pip install --no-deps -e . /opt/aioshelly \
    && python3 -m script.translations develop --all \
    && python3 -m compileall -q homeassistant \
    && sed -i 's|--config /config$|--config /config --skip-pip-packages aioshelly|' /etc/services.d/home-assistant/run

COPY packaging/haos/generated/provenance.json /REMOTE_SHELLY_BUILD.json
COPY packaging/haos/check_image.py /usr/local/bin/check_remote_image.py
WORKDIR /config
