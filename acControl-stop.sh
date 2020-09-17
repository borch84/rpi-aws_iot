ps -ef | grep acControl | grep -v grep | awk '{print $2}' | xargs kill
