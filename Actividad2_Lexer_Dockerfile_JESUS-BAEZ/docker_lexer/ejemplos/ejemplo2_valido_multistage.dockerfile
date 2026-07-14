# Ejemplo 2: Dockerfile multi-stage, válido, con banderas y digest de imagen
FROM golang:1.22-alpine AS builder
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN go build -o /out/servidor ./cmd/servidor

FROM alpine@sha256:c158987ec3d3c9040c9d7b0f501a37b6e9d8c1a11cff96b5c8c5d8f37c96f6cc
RUN apk add --no-cache ca-certificates
COPY --from=builder /out/servidor /usr/local/bin/servidor
VOLUME ["/data"]
EXPOSE 9090/tcp
ARG BUILD_VERSION=1.0.0
ENV APP_ENV=production
ENTRYPOINT ["/usr/local/bin/servidor"]
