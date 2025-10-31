FROM cirrusci/flutter:stable AS build

WORKDIR /build
COPY . /build

ARG API_BASE_URL
RUN flutter pub get && \
    flutter build web --release --dart-define=API_BASE_URL=${API_BASE_URL}

FROM nginx:alpine
COPY --from=build /build/build/web /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80


