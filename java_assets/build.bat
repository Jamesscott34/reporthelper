@echo off
echo Building Document Generator...
echo.

REM Check if Maven is installed
mvn --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Maven is not installed or not in PATH
    echo Please install Maven and try again
    pause
    exit /b 1
)

REM Clean and compile
echo Cleaning previous build...
mvn clean

echo Compiling...
mvn compile

echo Packaging...
mvn package

if %errorlevel% equ 0 (
    echo.
    echo Build successful!
    echo JAR file created in target/document-generator-1.0.0.jar
    echo.
    echo You can now run the application with:
    echo java -jar target/document-generator-1.0.0.jar
) else (
    echo.
    echo Build failed! Check the error messages above.
)

pause
