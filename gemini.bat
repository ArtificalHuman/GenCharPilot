@echo off

:: Activate the virtual environment
call env\Scripts\activate.bat

:: Prompt for character name
set /p character_name="Please enter the character name: "

:: Run the Python script with the character name
python Models\gemini.py %character_name%

:: Pause to see the output
pause

:: Optionally deactivate the virtual environment
deactivate