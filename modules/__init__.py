import pymysql

pymysql.install_as_MySQLdb() #drop-in replace mysqldb because aws' lambda doesn't like it