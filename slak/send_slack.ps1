$pythonExe = "C:/Users/PC_User/OneDrive/anakonda/python.exe"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$postScript = Join-Path $scriptDir "post_message.py"

& $pythonExe $postScript @args
