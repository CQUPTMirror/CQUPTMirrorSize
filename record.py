#! /usr/bin/env python
# coding: utf8
import os
import json
import time
import threading
import requests
def getSize(mirrorsSize, sonDir, lastupdatetime):
    mirror = {'mirrorName':'', 'storage':'', 'lastUpdate':'', 'realName':'', 'link':''}
    size = 0
    try:
        for root, dirs, files in os.walk(os.path.join(dir, sonDir)):
            size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
    except OSError, e:
            log = open('/data/config/error.log', 'a', 1024)
            currenttime = time.strftime('%Y-%m-%d %X', time.localtime( time.time() ) )
            log.write('[Error]: ' + str(currenttime) + ' ' + str(e) + "\n")
            log.close()
    mirror['mirrorName'] = sonDir.capitalize()
    mirror['realName'] = sonDir
    mirror['link'] = sonDir + '.mirrors.cqupt.edu.cn'
    mirror['storage'] = str('%.2f' % (size/1024.0/1024/1024))+'G'
    mirror['lastUpdate'] = lastupdatetime
    mirrorsSize.append(mirror)

def addNpm(mirrorsSize, lastupdatetime):
    mirror = {'mirrorNmae':'Npm', 'storage':'-', 'lastupdatetime':int(lastupdatetime/1000), 'realName':'npm', 'link':'npm.mirrors.cqupt.edu.cn'}
    mirrorsSize.append(mirror)

if __name__ == '__main__':
    dir = '/data/mirror'
    log_dir = '/var/log/rsync'
    size = 0
    data = {'mirror_list':'', 'update_time':0, 'update_cost_time':0}
    mirrorsSize = []
    threadList = []
    start_time = time.time()
    #从npm的registry获取更新信息
    npmUpdateTime = json.loads(requests.get('http://registry.mirror.cqupt.edu.cn/').text)['last_exist_sync_time']
    for sonDir in os.listdir(dir):
        name = os.popen('ls -r '+ log_dir + ' | grep '+ sonDir + ' | head -1').readline()[:-1]
        if name != '':
            lastupdatetime = int(os.path.getmtime(os.path.join('/var/log/rsync', name)))
        else:
            lastupdatetime = int(npmUpdateTime/1000)
        t = threading.Thread(target=getSize, args=(mirrorsSize , sonDir, lastupdatetime,))
        t.start()
        threadList.append(t)
    for t in threadList:
        t.join()
    addNpm(mirrorsSize, npmUpdateTime)
    end_time = time.time()
    data['mirror_list'] = mirrorsSize
    data['update_time'] = int(time.time())
    data['update_cost_time'] = int(end_time - start_time)
    f = open('/data/config/main.json', 'w', 1024)
    f.write(json.dumps(data))
    f.close()
    log = open('/data/config/success.log', 'a', 1024)
    currenttime = time.strftime('%Y-%m-%d %X', time.localtime( time.time() ) )
    log.write('[Info] Updated at: ' + str(currenttime) + ' cost ' + str(data['update_cost_time']) + "s\n")
    log.close()
    exit(0)
