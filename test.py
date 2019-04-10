import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('config.ini')

ip = config.get('SQL', 'ip')
print(ip)
