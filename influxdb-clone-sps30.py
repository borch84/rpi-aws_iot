from influxdb import InfluxDBClient
client = InfluxDBClient(host='localhost',port=8086,database='iotdb')
old_data = client.query('select auto_clean_interval_days,error,"nc0.5","nc1.0","nc10.0","nc2.5","nc4.5","pm1.0","pm10.0","pm2.5","pm4.0",tps,time from sps30')
new_data = [
    {
        'measurement': 'sps30_copy',
        'tags': {'serial': '4FBFC0FBE824FFEA'},
        'time': d['time'],
        'fields': {
            'auto_clean_interval_days': d['auto_clean_interval_days'],
            'error': d['error'],
            'nc0.5': d['nc0.5'],
            'nc1.0': d['nc1.0'],
            'nc10.0': d['nc10.0'],
            'nc2.5': d['nc2.5'],
            'nc4.5': d['nc4.5'],
            'pm1.0': d['pm1.0'],
            'pm2.5': d['pm2.5'],
            'pm4.0': d['pm4.0'],
            'tps': d['tps']
        }
    } for d in old_data.get_points()
]
client.write_points(new_data)
