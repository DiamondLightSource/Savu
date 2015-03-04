import sqlite3
import logging
import time

class SQLiteHandler(logging.Handler):
    """
    Logging handler for SQLite.

    Based on Vinay Sajip's DBHandler class (http://www.red-dove.com/python_logging.html)
    
    This version sacrifices performance for thread-safety:
    Instead of using a persistent cursor, we open/close connections for each entry.
    
    AFAIK this is necessary in multi-threaded applications, 
    because SQLite doesn't allow access to objects across threads.
    """

    initial_sql = """CREATE TABLE IF NOT EXISTS log(
                        Relative decimal,
                        Created date,
                        Name text,
                        LogLevel int,
                        LogLevelName text,    
                        Message text,
                        Module text,
                        FuncName text,
                        LineNo int,
                        Exception text,
                        Process int,
                        Thread text,
                        ThreadName text
                   )"""

    insertion_sql = """INSERT INTO log(
                        Relative,
                        Created,
                        Name,
                        LogLevel,
                        LogLevelName,
                        Message,
                        Module,
                        FuncName,
                        LineNo,
                        Exception,
                        Process,
                        Thread,
                        ThreadName
                   )
                   VALUES (
                        %(relativeCreated)f,
                        "%(dbtime)s",
                        "%(name)s",
                        %(levelno)d,
                        "%(levelname)s",
                        "%(message)s",
                        "%(module)s",
                        "%(funcName)s",
                        %(lineno)d,
                        "%(exc_text)s",
                        %(process)d,
                        "%(thread)s",
                        "%(threadName)s"
                   );
                   """

    def __init__(self, db='app.db'):
    
        logging.Handler.__init__(self)
        self.db = db
        # Create table if needed:
        conn = sqlite3.connect(self.db)
        conn.execute(SQLiteHandler.initial_sql)
        conn.commit()

    def formatDBTime(self, record):
        tt = time.localtime(record.created)
        record.dbtime = time.strftime("%Y-%m-%d %H:%M:%S", tt) + ".%010.6f" % (record.msecs)

    def emit(self, record):
       
        # Use default formatting:
        self.format(record)
        # Set the database time up:
        self.formatDBTime(record)
        if record.exc_info:
            record.exc_text = logging._defaultFormatter.formatException(record.exc_info)
        else:
            record.exc_text = ""
        # Insert log record:
        sql = SQLiteHandler.insertion_sql % record.__dict__
        conn = sqlite3.connect(self.db)
        conn.execute(sql)
        conn.commit()


def main():
    def print_all_log(oLog):
        # Print all log levels
        oLog.debug('debug')
        oLog.info('info')
        oLog.warning('warning')
        oLog.error('error')
        oLog.critical('critical')
    
                
    logger = logging.getLogger('simple_example')
    logger.setLevel(logging.DEBUG)
    
    sqlh = SQLiteHandler()
    logger.addHandler(sqlh)
    # In main Thread
    print_all_log(logger)
    


if __name__ == '__main__':
    main()