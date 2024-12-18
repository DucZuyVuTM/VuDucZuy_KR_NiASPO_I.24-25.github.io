# Dockerfile tại thư mục root
FROM docker/compose:latest

# Copy toàn bộ project vào container
WORKDIR /app
COPY . .

# Chạy docker-compose để xây dựng và chạy các dịch vụ
CMD ["docker-compose", "up", "--build"]
