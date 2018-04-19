import pyodbc
import pandas.io.sql as psql

class DBAccessor:
    """DB Access"""

    config = "DRIVER={SQL Server};SERVER=ECOLOGDB2016;DATABASE=ECOLOGDBver3"

    @classmethod
    def ExecuteQuery(self, query):
        cnn = pyodbc.connect(self.config)
        cur = cnn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
        cnn.close()
        return rows

    @classmethod
    def ExecuteQueryDF(self, query):
        with pyodbc.connect(self.config) as conn:
            df = psql.read_sql(query, conn)
        return df