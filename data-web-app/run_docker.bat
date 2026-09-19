@echo off
chcp 65001 >nul
echo Starting Data Web Application with Docker Compose...
echo.

docker-compose up -d

echo.
echo Application is starting up...
echo.
echo Once all containers are ready, you can access:
echo - Web App:    http://localhost:8000
echo - API Docs:    http://localhost:8000/docs
echo - pgAdmin:     http://localhost:5050
echo.
echo To view logs: docker-compose logs -f
echo To stop:      docker-compose down
pause
