import pymysql
from termcolor import colored

class Lumysql:
    def __init__(self, host="127.0.0.1", port=3306, user="root", password="", database=None) -> None:
        self.connection = pymysql.connect(host=host, port=port, user=user, password=password, database=database, cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.connection.cursor()

    def fetch_all(self, sql, args=()):
        """根据SQL查找数据集, 并返回所有数据

        Args:
            sql (string): 查找的SQL语句
            args (tuple, optional): SQL占位符中的参数元组. Defaults to ().

        Returns:
            _type_: 是否正常返回(bool), 返回的数据列表(list)
        """
        try:
            self.cursor.execute(sql, args)
            results = self.cursor.fetchall()
        except Exception as e:
            print(colored(f"SQL执行出错, 报错: {str(e)}", "red"))
            return False, []
        else:
            return True, results

    def modify(self, sql, args=()):
        """修改数据(insert,update,delete)

        Args:
            sql (string): 执行的SQL
            args (tuple, optional): SQL占位符中的参数元组. Defaults to ().

        Returns:
            _type_: 是否执行成功(bool)
        """
        try:
            self.cursor.execute(sql, args)
            self.connection.commit()
        except Exception as e:
            print(colored(f"SQL执行出错, 报错: {str(e)}", "red"))
            return False
        else:
            return True