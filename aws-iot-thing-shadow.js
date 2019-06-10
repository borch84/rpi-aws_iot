/*
Este ejemplo permite conectar  un raspberry pi a la nube de amazon IoT
*/

var Gpio = require('onoff').Gpio;
var sensor = new Gpio(17,'in','both', {debounceTimeout: 10} );

function unexportOnClose() {
  sensor.unexport();
}

process.on('SIGINT',unexportOnClose);


var awsIot = require('aws-iot-device-sdk');
var host = 'a3s9lktlbmjbgn-ats.iot.us-east-1.amazonaws.com';
var thing_name = process.argv[2]; /*nombre del directorio representa el nombre del thing de aws. El tercer argumento del proceso corresponde al nombre del thing en aws y es el mismo nombre del folder donde se encuentran los certificados.*/
var keyPath = `./${thing_name}/private.pem.key`;
var certPath = `./${thing_name}/certificate.pem.crt`;
var caPath = `./aws-root-ca.pem`;
var shadowDeviceId = `${thing_name}`; //el nombre del client tiene que ser el mismo que el thing por la configuracion del policy. 

var thingShadows = awsIot.thingShadow({
   keyPath: keyPath,
  certPath: certPath,
    caPath: caPath,
  clientId: shadowDeviceId,
      host: host
});
//
// Client token value returned from thingShadows.update() operation
//
var clientTokenUpdate;

sensor.watch((error,value) => {
  if (error) {
    console.error(error);
    return;
  }
  console.log('Estado GPIO17:',value);
  if (value == 1) {
    var reedswitch = {"state":{"reported":{"reedswitch":true}}};  
  }
  if (value == 0) {
    var reedswitch = {"state":{"reported":{"reedswitch":false}}}; 
  }
  
  clientTokenUpdate = thingShadows.update(thing_name, reedswitch);

  if (clientTokenUpdate === null)
  {
    console.log('update shadow failed, operation still in progress');
  }

});



thingShadows.on('connect', function() {
//
    thingShadows.register( thing_name, {}, function() {
      console.log(thing_name, 'fue registrado!');
    });

});

thingShadows.on('status', 
    function(thingName, stat, clientToken, stateObject) {
       console.log('received '+stat+' on '+thingName+': '+
                   JSON.stringify(stateObject));
    });

thingShadows.on('delta', 
    function(thingName, stateObject) {
       console.log('received delta on '+thingName+': '+ JSON.stringify(stateObject));
       var windowOpenState = stateObject.state.windowOpen;
       console.log(stateObject.state.windowOpen);
       console.log('****ACTUALIZANDO EL REPORTED_WINDOW_STATE!');
       var reportedWindowState = {"state":{"reported":{"windowOpen":windowOpenState}}}; 
       thingShadows.update(thing_name, reportedWindowState);
    });

thingShadows.on('timeout',
    function(thingName, clientToken) {
       console.log('received timeout on '+thingName+
                   ' with token: '+ clientToken);
//
// In the event that a shadow operation times out, you'll receive
// one of these events.  The clientToken value associated with the
// event will have the same value which was returned in an earlier
// call to get(), update(), or delete().
//
    });
