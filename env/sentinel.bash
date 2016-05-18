############## Sentinel Project Commands #####################
#
# Sentinel is an interface for interacting with Dash governance
#
# ATTENTION: 
# **** change these each project, so that the default is correct usually ****
#

cmd_sentinel()
{
  if [ "$1" = "help" ]; then
    echo "Sentinel project commands";
    echo "-----------------------------------";
    echo "";
    echo "Commands:";
    echo "  cd";
    echo "  start";
    echo "  open";
    echo "";
    echo "";
  fi;

  #---- generic commands
  if [ "$1" = "start" ]; then cd ~/Desktop/projects/sentinel && ./sentinel-cli; return; fi;
  if [ "$1" = "cd" ]; then cd ~/Desktop/projects/sentinel; return; fi;
  if [ "$1" = "open" ]; then cd ~/Desktop/projects/sentinel; sublime cli.py return; fi;
}

alias sentinel=cmd_sentinel;