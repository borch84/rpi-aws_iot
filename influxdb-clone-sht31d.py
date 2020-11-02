from influxdb import InfluxDBClient
client = InfluxDBClient(host='localhost',port=8086,database='iotdb')
sht31d_data = client.query('select h,t,time from sht31d')
new_data = [
    {
        'measurement': 'sht31d_copy',
        'tags': {'sensor_id': '1'},
        'time': d['time'],
        'fields': {
            'h': d['h'],
            't': d['t']
        }
    } for d in sht31d_data.get_points()
]
client.write_points(new_data)
