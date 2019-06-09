var Gpio = require('onoff').Gpio;
var sensor = new Gpio(17,'in','both');

sensor.watch((error,value) => {
	if (error) {
		console.error(error);
		return;
	}
	console.log(value);
});

function unexportOnClose() {
	sensor.unexport();
}

process.on('SIGINT',unexportOnClose);
