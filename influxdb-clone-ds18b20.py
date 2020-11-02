from influxdb import InfluxDBClient
client = InfluxDBClient(host='localhost',port=8086,database='iotdb')
old_data = client.query('select t,time from ds18b20')
new_data = [
    {
        'measurement': 'ds18b20_copy',
        'tags': {'address': '28-000008bf3a26'},
        'time': d['time'],
        'fields': {
            't': d['t'],
        }
    } for d in old_data.get_points()
]
client.write_points(new_data)
