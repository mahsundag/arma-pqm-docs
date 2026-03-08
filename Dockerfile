FROM mcr.microsoft.com/dotnet/sdk:9.0-alpine AS build

RUN apk add --no-cache git bash python3
RUN dotnet tool install -g docfx
ENV PATH="$PATH:/root/.dotnet/tools"

ARG AZURE_DEVOPS_PAT
WORKDIR /docs
COPY . .

RUN chmod +x scripts/clone-wikis.sh && bash scripts/clone-wikis.sh
RUN docfx build

FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /docs/_site /usr/share/nginx/html
EXPOSE 80
