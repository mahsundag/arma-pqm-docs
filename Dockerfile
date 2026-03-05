FROM mcr.microsoft.com/dotnet/sdk:9.0-alpine AS build
RUN dotnet tool install -g docfx
ENV PATH="$PATH:/root/.dotnet/tools"
WORKDIR /docs
COPY . .
RUN docfx build

FROM nginx:alpine
COPY --from=build /docs/_site /usr/share/nginx/html
EXPOSE 80
