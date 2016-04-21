
import _mysql
import config 
db=_mysql.connect(config.hostname, config.username, config.password, config.database)

