FROM golang:1.14-buster AS easy-novnc-build
WORKDIR /src
RUN go mod init build && \
    go get github.com/geek1011/easy-novnc@v1.1.0 && \
    go build -o /bin/easy-novnc github.com/geek1011/easy-novnc

FROM ubuntu:20.04

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    tigervnc-standalone-server \
    supervisor \
    bspwm \
    udev

COPY --from=easy-novnc-build /bin/easy-novnc /usr/local/bin/
COPY ./supervisord.conf /etc/supervisord.conf
COPY ./99-SaleaeLogic.rules /etc/udev/rules.d/99-SaleaeLogic.rules
EXPOSE 8080

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
    libglib2.0-0 \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libgtk3-perl \
    libgbm1 \
    libasound2 \
    libfuse2

# Download the Logic2 software
ARG LOGIC2_VERSION=2.4.14
ADD https://downloads.saleae.com/logic2/Logic-${LOGIC2_VERSION}-linux-x64.AppImage /Logic2.AppImage
RUN chmod +x /Logic2.AppImage

CMD ["supervisord" ]