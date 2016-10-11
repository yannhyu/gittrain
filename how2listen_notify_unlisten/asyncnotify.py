#!/usr/bin/python -tt
# asyncnotify.py
import psycopg2
from select import select
import psycopg2.extensions
from twisted.internet import threads

class AsyncNotify():
    '''
    Class to trigger a function via PostgreSQL NOTIFY messages. 
    Refer to the documentation for information on LISTEN, NOTIFY and UNLISTEN. 
    http://www.postgresql.org/docs/9.5/static/sql-notify.html

    This obscure feature is very useful. You can create a trigger function on a
    table that executes the NOTIFY command. Then any time something is inserted,
    updated or deleted your Python function will be called using this class.
    '''
    def __init__(self, dsn):
        '''The dsn is passed here. This class requires the psycopg2 driver.'''
        #import psycopg2
        print 'AsyncNotify init here ...'
        self.conn = psycopg2.connect(dsn)
        #self.conn.set_isolation_level(0)
        self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        self.curs = self.conn.cursor()
        self.__listening = False

    def __listen(self):
        print 'Waiting for notifications ...'
        print 'self.conn.status : ', self.conn.status

        if self.__listening:
            print 'already listening...'
            return 'already listening!'
        else:
            print 'not already listening... start now...'
            print 'self.conn.status : ', self.conn.status
            self.__listening= True
            while self.__listening:
                if select([self.conn],[],[],10) == ([],[],[]):
                    print "Timeout"
                else:
                    self.conn.poll()
                    print 'self.conn.notifies :', self.conn.notifies
                    while self.conn.notifies:
                        #pid, notify = self.conn.notifies.pop()
                        #print 'pid :', pid
                        #print 'notify :', notify
                        #self.gotNotify(pid, notify)
                        notify = self.conn.notifies.pop()
                        pid = notify.pid
                        channel = notify.channel
                        print 'pid :', pid
                        print 'channel :', channel
                        print 'payload :', notify.payload
                        self.gotNotify(pid, channel)      

    def addNotify(self, notify):
        '''Subscribe to a PostgreSQL NOTIFY'''
        sql = "LISTEN %s" % notify
        self.curs.execute(sql)

    def removeNotify(self, notify):
        '''Unsubscribe a PostgreSQL LISTEN'''
        sql = "UNLISTEN %s" % notify
        self.curs.execute(sql)

    def stop(self):
        '''Call to stop the listen thread'''
        self.__listening = False

    def run(self):
        '''Start listening in a thread and return that as a deferred'''
        #from twisted.internet import threads
        return threads.deferToThread(self.__listen)

    def gotNotify(self, pid, notify):
        '''Called whenever a notification subscribed to by addNotify() is detected.
           Unless you override this method and do someting this whole thing is rather pointless.
        '''
        pass


"""
self.conn.notifies : [Notify(12877, 'test1', '')]
pid : 12877
notify : test1
got asynchronous notification 'test1' from process id '12877'
self.conn.notifies : []
self.conn.notifies : []
self.conn.notifies : []



        if self.__listening:
            print 'already listening...'
            return 'already listening!'
        else:
            print 'not already listening... starting now...'
            print 'self.conn.status : ', self.conn.status
            self.__listening= True
            while self.__listening:
                if select([self.conn],[],[],10)!=([],[],[]):
                    print "Timeout"
                else:
                    self.conn.poll()
                    print 'self.conn.notifies :', self.conn.notifies
                    while self.conn.notifies:
                        #pid, notify = self.conn.notifies.pop()
                        #print 'pid :', pid
                        #print 'notify :', notify
                        #self.gotNotify(pid, notify)
                        notify = self.conn.notifies.pop()
                        pid = notify.pid
                        channel = notify.channel
                        print 'pid :', pid
                        print 'channel :', channel
                        print 'payload :', notify.payload
                        self.gotNotify(pid, channel)
"""        