from influxdb import InfluxDBClient
client = InfluxDBClient(host='localhost',port=8086,database='iotdb')
ph_data = client.query('select ph,time from ph99')
new_data = [
    {
        'measurement': 'ph99_copy',
        'tags': {'sensor_id': '99'},
        'time': d['time'],
        'fields': {
            'ph': d['ph'],
        }
    } for d in ph_data.get_points()
]
client.write_points(new_data)
