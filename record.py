#! /usr/bin/env python
# coding: utf8
import os
import json
import time
import threading
import requests

class CQUPTMirrorSize():

    def __init__(self, mirrorDir='/data/mirror', logDir='/var/log/rsync', recordLogDir='/data/config'):
        self.recordLogDir = recordLogDir
        self.mirrorDir = mirrorDir
        self.logDir = logDir
        self.data = {'mirror_list': '', 'update_time': 0, 'update_cost_time': 0}
        self.mirrors = []
        self.threadList = []
        self.mirrorList = []
        self.startTime = time.time()
        self.endTime = 0


    #获取镜像源列表
    def getMirrorsList(self):
        for sonDir in os.listdir(self.mirrorDir):
            self.mirrorList.append(sonDir)
        return self.mirrorList

    #new线程
    def new_treads(self, callback, args=(), threadName=None):
            t = threading.Thread(target=callback, args=args, name=threadName)
            t.start()
            self.threadList.append(t)

    #获取镜像大小
    def getSize(self, sonDir):
        mirror = {'mirrorName': '', 'storage': '', 'lastUpdate': '', 'realName': '', 'link': ''}
        size = 0
        try:
            for root, dirs, files in os.walk(os.path.join(self.mirrorDir, sonDir)):
                size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
        except OSError, e:
            log = open(self.recordLogDir+'/error.log', 'a', 1024)
            currentTime = time.strftime('%Y-%m-%d %X', time.localtime(time.time()))
            log.write('[Error]: ' + str(currentTime) + ' ' + str(e) + "\n")
            log.close()
        name = os.popen('ls -r ' + self.logDir + ' | grep ' + sonDir + ' | head -1').readline()[:-1]
        if name != '':
            lastUpdateTime = int(os.path.getmtime(os.path.join(self.logDir, name)))
        else:
            lastUpdateTime = 0
        mirror['mirrorName'] = sonDir.capitalize()
        mirror['realName'] = sonDir
        mirror['link'] = sonDir + '.mirrors.cqupt.edu.cn'
        mirror['storage'] = str('%.2f' % (size / 1024.0 / 1024 / 1024)) + 'G'
        mirror['lastUpdate'] = lastUpdateTime
        self.mirrors.append(mirror)

    #怎么搞才不会耦合呢
    def getJSSize(self):
        npmUpdateTime = json.loads(requests.get('http://registry.mirror.cqupt.edu.cn/').text)['last_exist_sync_time']
        mirror = {'mirrorName': 'Npm', 'storage': '-', 'lastUpdate': int(npmUpdateTime / 1000), 'realName': 'npm',
                  'link': 'npm.mirrors.cqupt.edu.cn'}
        self.mirrors.append(mirror)
        jsList = [
            {'name':'node', 'dir':'/data/cnpm-fss/.tmp/nfs/dist/', 'link':'npm.mirror.cqupt.edu.cn/dist/node'},
            {'name':'iojs', 'dir':'/data/cnpm-fss/.tmp/nfs/dist/', 'link':'npm.mirror.cqupt.edu.cn/dist/iojs'}
        ]
        for x in jsList:
            mirror = {'mirrorName': '', 'storage': '', 'lastUpdate': '', 'realName': '', 'link': ''}
            size = 0
            try:
                for root, dirs, files in os.walk(os.path.join(x['dir'], x['name'])):
                    size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
            except OSError, e:
                log = open(self.recordLogDir + '/error.log', 'a', 1024)
                currentTime = time.strftime('%Y-%m-%d %X', time.localtime(time.time()))
                log.write('[Error]: ' + str(currentTime) + ' ' + str(e) + "\n")
                log.close()
            mirror['mirrorName'] = x['name'].capitalize()
            mirror['realName'] = x['name']
            mirror['link'] = x['link']
            mirror['storage'] = str('%.2f' % (size / 1024.0 / 1024 / 1024)) + 'G'
            name = os.popen('ls -r /data/cnpm-fss/.tmp/logs | grep ' + x['name'] + ' | head -1').readline()[:-1]
            if name != '':
                lastUpdateTime = int(os.path.getmtime(os.path.join('/data/cnpm-fss/.tmp/logs', name)))
            else:
                lastUpdateTime = 0
            mirror['lastUpdate'] = lastUpdateTime
            self.mirrors.append(mirror)

    def writeLog(self):
        for t in self.threadList:
            t.join()
        self.endTime = time.time()
        self.data['mirror_list'] = self.mirrors
        self.data['update_time'] = int(time.time())
        self.data['update_cost_time'] = int(self.endTime - start_time)
        f = open(self.recordLogDir +'/main.json', 'w', 1024)
        f.write(json.dumps(self.data))
        f.close()
        log = open(self.recordLogDir + '/success.log', 'a', 1024)
        currentTime = time.strftime('%Y-%m-%d %X', time.localtime(time.time()))
        log.write('[Info] Updated at: ' + str(currentTime) + ' cost ' + str(self.data['update_cost_time']) + "s\n")
        log.close()

if __name__ == '__main__':
    start_time = time.time()
    mirrorClass = CQUPTMirrorSize()
    mirrorList = mirrorClass.getMirrorsList()
    for x in mirrorList:
        mirrorClass.new_treads(callback=mirrorClass.getSize, threadName=x, args=(x, ))
    mirrorClass.new_treads(callback=mirrorClass.getJSSize)
    mirrorClass.writeLog()
    exit(0)