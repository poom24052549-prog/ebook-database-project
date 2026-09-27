Set WshShell = CreateObject("WScript.Shell")
' Run Flask app in the background without showing any command prompt window
WshShell.Run "pythonw app.py", 0, False
WScript.Sleep 1000
' Open default browser directly to the web app
WshShell.Run "http://127.0.0.1:5000"
