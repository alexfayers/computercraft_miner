# Start both servers using windows terminal

start wt "new-tab -p `"Command Prompt`" cmd /k python -m computercraft.server ; split-pane -p `"Command Prompt`" cmd /k python -m http.server"