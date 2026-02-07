@echo off
REM Script to create an admin user for the Job Board Platform
REM Usage: create_admin.bat [username] [email] [password]

echo Creating admin user for Job Board Platform...

REM Check if running in Docker (Windows)
if exist "docker-compose.yml" (
    echo Running with Docker...
    if "%1"=="" (
        docker-compose exec web python manage.py create_admin
    ) else if "%3"=="" (
        echo Usage: %0 [username] [email] [password]
        echo   With no arguments: Interactive mode
        echo   With 3 arguments: Non-interactive mode
        exit /b 1
    ) else (
        docker-compose exec web python manage.py create_admin --username "%1" --email "%2" --password "%3" --no-input
    )
) else (
    REM Local mode
    if "%1"=="" (
        python manage.py create_admin
    ) else if "%3"=="" (
        echo Usage: %0 [username] [email] [password]
        echo   With no arguments: Interactive mode
        echo   With 3 arguments: Non-interactive mode
        exit /b 1
    ) else (
        python manage.py create_admin --username "%1" --email "%2" --password "%3" --no-input
    )
)

echo Admin user created successfully!
echo You can now log in at: http://localhost:8000/admin/
