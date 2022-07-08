import click
from deluge_client import DelugeRPCClient
from urllib.parse import urlencode
import sqlite3

@click.group()
def cli():
    pass

def write(tor_query,sql_conn):
    c = sql_conn.cursor()
    c.execute('''create table torrents
                 ([hash] text primary key,
                  [name] text,
                  [save_path] text,
                  [magnet] text)''')

    for entry in tor_query:
        myhash = entry.decode('utf-8')
        name = tor_query[entry][b'name'].decode('utf-8')
        path = tor_query[entry][b'save_path'].decode('utf-8')
        thash = 'magnet:?xt=urn:btih:'+myhash.upper()
        magnet = thash +'&' + urlencode({'dn' : name})
        trackers = ''
        for tr in tor_query[entry][b'trackers']:
            trackers += '&' + urlencode({'tr' : tr[b'url'].decode('utf-8')})
        magnet += trackers
        #print('"%s"' % name,path,magnet)
        c.execute("insert into torrents values(?,?,?,?)", (myhash,name,path,magnet ))
        sql_conn.commit()


@cli.command('get-database')
@click.option('--out','-o','out',help='output file',required=True)
@click.option('--address','-a','addr',help='daemon address',required=False,
    default='localhost')
@click.option('--port','-p','port',help='daemon port',required=False,
    default=58846)
@click.option('--user','-u','user',help='username',required=False,
    default='')
@click.option('--password','-k','passw',help='password',required=False,
    default='')
def get_db(out,addr,port,user,passw):
    client = DelugeRPCClient(addr, port,user,passw)
    client.connect()
    print("connected:",client.connected)
    query = client.call('core.get_torrents_status', {}, ['name','save_path','trackers'])
    
    conn = sqlite3.connect(out)
    write(query,conn)

@cli.command('read-database')
@click.option('--in','-i','indb',help='input file',required=True)
def read_db(indb):
    conn = sqlite3.connect(indb)
    c = conn.cursor()
    for entry in c.execute('select * from torrents'):
        print(entry)

if __name__ == "__main__":
    cli()
