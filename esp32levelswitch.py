def jsonpayload(esp32LevelSwitchFile):
    with open(esp32LevelSwitchFile, 'r') as f:
       try:
         esp32LevelSwitchJSONPayload = f.read()
         f.close()
         return esp32LevelSwitchJSONPayload
       except Exception as e:
   	     print ("**** esp32LevelSwitchJSONPayload error ****")
   	     return None