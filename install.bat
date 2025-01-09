@echo off
:: Setting up Virtual Enviroment
echo Setting up Virtual environment...
python venv env
call env\Scripts\activate.bat
echo Installing requirements...
pip install -r requirements.txt
:: Prompt for GEMINI_API
echo Creating .env file...
set /p GEMINI_API="Enter your GEMINI API key (leave blank for 'Not set'): "
if "%GEMINI_API%"=="" set GEMINI_API="Not set"
:: Prompt for CHAI_API
set /p CHAI_API="Enter your CHAI API key (leave blank for 'Not set'): "
if "%CHAI_API%"=="" set CHAI_API="Not set"
:: Create the .env file
(
    echo GEMINI_API=%GEMINI_API%
    echo CHAI_API=%CHAI_API%
) > .env
echo .env file created successfully.
deactivate