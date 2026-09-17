Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
strDir = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = strDir

pythonwPath = WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%\Python\pythoncore-3.14-64\pythonw.exe")
If Not fso.FileExists(pythonwPath) Then
    pythonwPath = "pythonw.exe"
End If

WshShell.Run """" & pythonwPath & """ """ & strDir & "\main.py""", 0, False
