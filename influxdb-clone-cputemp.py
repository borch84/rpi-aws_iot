from influxdb import InfluxDBClient
client = InfluxDBClient(host='localhost',port=8086,database='iotdb')
old_data = client.query('select CPUTemp,time from cputemp')
new_data = [
    {
        'measurement': 'cputemp_copy',
        'tags': {'cpu_serial': '00000000b380f5db'},
        'time': d['time'],
        'fields': {
            'CPUTemp': d['CPUTemp'],
        }
    } for d in old_data.get_points()
]
client.write_points(new_data)