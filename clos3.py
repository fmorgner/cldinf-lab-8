#!/usr/bin/python

import os, sys
from mininet.net import Mininet
from mininet.node import OVSSwitch, OVSController, Controller
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.util import quietRun
from mininet.moduledeps import pathCheck
from mininet.util import dumpNodeConnections

class clos3(Topo):

    def __init__(self, leaf, spine):
        Topo.__init__(self)

        self.spineDevs = self.create_devices(self.addHost, "ss", spine )
        self.leafDevs = self.create_devices(self.addHost, "ls", leaf )
        self.hostDevs = self.create_devices(self.addHost, "h", leaf )

        self.hookup(self.spineDevs, self.leafDevs, self.hostDevs)

    def create_devices(self, addFunc, prefix, nofDevices):
        devices = list()

        for devID in range(0, nofDevices):
            devices.append( addFunc( prefix + str(devID + 1) ) )
        return devices

    def hookup(self, spineDevices, leafDevices, hostDevices):
        leafIndex = 0
        for ldev in leafDevices:
            hdev = hostDevices[leafIndex]
            self.addLink(ldev, hdev)
            leafIndex += 1
            for sdev in spineDevices:
                self.addLink(ldev, sdev)

topos = { 'clos3': clos3 }

def addIpAddresses(net):
    for i in range (0, len(net.topo.spineDevs)):
        spineDev=net.getNodeByName(net.topo.spineDevs[i])
        spineDev.cmd("sysctl -w net.ipv4.ip_forward=1")
        for j in range (0, len(spineDev.intfList())):
            myIp="10.{0}.{1}.1".format(i+1,j+1)
            otherIp="10.{0}.{1}.2".format(i+1,j+1)
            spineDev.intfList()[j].link.intf2.setIP(myIp, 30)
            spineDev.intfList()[j].link.intf1.setIP(otherIp, 30)
            clientnet="10.0.{0}.0/30".format(j+1)
            spinenet="10.{0}.0.0/16".format(j+1)
            router="10.{0}.{1}.2".format(i+1,j+1)
            #print(spineDev.name + " ip route add " + clientnet + " via " + router)
            print(spineDev.name + " ip route add " + spinenet + " via " + router)
            spineDev.cmd("ip route add " + clientnet + " via " + router)
            spineDev.cmd("ip route add " + spinenet + " via " + router)
    for i in range (0, len(net.topo.leafDevs)):
        leafDev=net.getNodeByName(net.topo.leafDevs[i])
        leafDev.cmd("sysctl -w net.ipv4.ip_forward=1")
        otherIp="10.1.{0}.1".format(i+1)
        leafDev.cmd("ip route add default via " + otherIp)
        for j in range (0, len(net.topo.spineDevs)):
            spineNet="10.{0}.0.0/16".format(j+1)
            spineRouter="10.{0}.{1}.1".format(j+1,i+1)
            leafDev.cmd("ip route add " + spineNet + " via " + spineRouter)
            #print(leafDev.name + " ip route add " + spineNet + " via " + spineRouter)
    for i in range (0, len(net.topo.hostDevs)):
        hostDev=net.getNodeByName(net.topo.hostDevs[i])
        myIp="10.0.{0}.2".format(i+1)
        hostDev.intfList()[0].link.intf1.setIP(myIp, 30)
        otherIp="10.0.{0}.1".format(i+1)
        hostDev.intfList()[0].link.intf2.setIP(otherIp, 30)
        hostDev.setDefaultRoute("dev " + hostDev.intfList()[0].name + " via " + otherIp)

def layer3net(leaf, spine):
    if os.geteuid() != 0:
        exit("you need to be root to run this script")
    topo = clos3(leaf, spine)
    info( '*** Creating network\n' )
    net = Mininet(topo=topo, controller=OVSController, switch=OVSSwitch)
    addIpAddresses(net)
    net.start()
    #dumpNodeConnections(net.values())

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    layer3net(int(sys.argv[1]),int(sys.argv[2]))
