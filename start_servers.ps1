# Start both servers using windows terminal

$directory = Get-Location

start wt "new-tab -p `"Command Prompt`" cmd /k python -m computercraft.server ; split-pane -p `"Command Prompt`" cmd /k python -m http.server -d $directory"

start wt "new-tab -p `"Command Prompt`" cmd /k python $directory\info_server.py"