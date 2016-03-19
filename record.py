#! /usr/bin/env python
# coding: utf8
import os
import json
import time
import threading
def getSize(mirrorsSize, sonDir):
    mirror = {'mirrorName':'', 'storage':'', 'lastUpdate':''}
    size = 0
    try:
        for root, dirs, files in os.walk(os.path.join(dir, sonDir)):
            size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
    except OSError, e:
            log = open('error.log', 'a', 1024)
            currenttime = time.strftime('%Y-%m-%d %X', time.localtime( time.time() ) )
            log.write('[Error]: ' + str(currenttime) + ' ' + str(e) + "\n")
            log.close()
    mirror['mirrorName'] = sonDir
    mirror['storage'] = str('%.2f' % (size/1024.0/1024/1024))+'G'
    mirror['lastUpdate'] = int(time.time())
    print mirror
    mirrorsSize.append(mirror)

if __name__ == '__main__':
    dir = '/data/mirror'
    size = 0
    data = {'mirror_list':'', 'update_time':0, 'update_cost_time':0}
    mirrorsSize = []
    start_time = time.time()
    for sonDir in os.listdir(dir):
        threading.Thread(target=getSize, args=(mirrorsSize, sonDir,)).start()
    end_time = time.time()
    data['mirror_list'] = mirrorsSize
    data['update_time'] = int(time.time())
    data['update_cost_time'] = int(end_time - start_time)
    f = open('main.json', 'w', 1024)
    f.write(json.dumps(data))
    f.close()
    log = open('success.log', 'a', 1024)
    currenttime = time.strftime('%Y-%m-%d %X', time.localtime( time.time() ) )
    log.write('[Info] Updated at: ' + str(currenttime) + ' cost ' + str(data['update_cost_time']) + "s\n")
    log.close()
