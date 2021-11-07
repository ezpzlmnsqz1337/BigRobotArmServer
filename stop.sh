ps axf | grep http.server | grep -v grep | awk '{print "kill -9 " $1}' | sh
ps axf | grep websocket-server | grep -v grep | awk '{print "kill -9 " $1}' | sh