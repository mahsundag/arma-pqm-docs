FROM mcr.microsoft.com/dotnet/sdk:9.0-alpine AS build

RUN apk add --no-cache git bash python3
RUN dotnet tool install -g docfx
ENV PATH="$PATH:/root/.dotnet/tools"

ARG AZURE_DEVOPS_PAT
WORKDIR /docs
COPY . .

RUN chmod +x scripts/clone-wikis.sh && bash scripts/clone-wikis.sh
RUN docfx build \
    && echo "=== Favicon files in _site ===" \
    && find _site -name "favicon*" -o -name "*.ico" -o -name "*.svg" | head -20 \
    && echo "=== link rel=icon in index.html ===" \
    && grep -i "rel=.icon\|rel=.shortcut\|favicon" _site/index.html || true \
    && echo "=== head section of index.html ===" \
    && sed -n '/<head/,/<\/head>/p' _site/index.html | head -30 || true

FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /docs/_site /usr/share/nginx/html
# Ensure logo and favicon are present even if docfx skips them
COPY --from=build /docs/images/logo.svg /usr/share/nginx/html/images/logo.svg
COPY --from=build /docs/images/favicon.ico /usr/share/nginx/html/images/favicon.ico
COPY --from=build /docs/images/favicon.ico /usr/share/nginx/html/favicon.ico
EXPOSE 80
