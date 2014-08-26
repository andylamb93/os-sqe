import os
import StringIO
from fabric.context_managers import settings
from fabric.operations import put, run

import urlparse
from ci import ZUUL_URL, ZUUL_PROJECT, ZUUL_REF, \
    NEXUS_VLAN_START, NEXUS_VLAN_END, SCREEN_LOG_PATH, \
    NEXUS_INTF_NUM, NEXUS_IP, NEXUS_USER, NEXUS_PASSWORD, \
    PARENT_FOLDER_PATH
from ci.lib.devstack import DevStack
from ci.lib.test_case import MultinodeTestCase


TEST_LIST_FILE = os.path.join(PARENT_FOLDER_PATH, 'cisco_plugin_tests.txt')
Q_PLUGIN_EXTRA_CONF_FILES = 'ml2_conf_cisco.ini'
LOCALCONF_CONTROLLER = '''
[[local|localrc]]
HOST_IP={HOST_IP}

MULTI_HOST=1

disable_service n-net heat h-api h-api-cfn h-api-cw h-eng cinder c-api c-sch c-vol
enable_service neutron
enable_service tempest
enable_service q-svc
enable_service q-agt
enable_service q-dhcp
enable_service q-l3
enable_service q-meta
enable_service n-cpu
enable_service q-vpn
enable_service q-lbaas

MYSQL_PASSWORD=nova
RABBIT_PASSWORD=nova
SERVICE_TOKEN=nova
SERVICE_PASSWORD=nova
ADMIN_PASSWORD=nova

LIBVIRT_TYPE=qemu
NOVA_USE_QUANTUM_API=v2
VOLUME_BACKING_FILE_SIZE=2052M
Q_PLUGIN=ml2
Q_ML2_PLUGIN_MECHANISM_DRIVERS=openvswitch,cisco_nexus
Q_ML2_PLUGIN_TYPE_DRIVERS=vlan
Q_PLUGIN_EXTRA_CONF_PATH=({Q_PLUGIN_EXTRA_CONF_PATH})
Q_PLUGIN_EXTRA_CONF_FILES=({Q_PLUGIN_EXTRA_CONF_FILES})
ML2_VLAN_RANGES=physnet1:{vlan_start}:{vlan_end}
PHYSICAL_NETWORK=physnet1
OVS_PHYSICAL_BRIDGE=br-eth1
TENANT_VLAN_RANGE={vlan_start}:{vlan_end}
ENABLE_TENANT_VLANS=True
ENABLE_TENANT_TUNNELS=False
Q_ML2_TENANT_NETWORK_TYPE=vlan
LOGFILE=/opt/stack/screen-logs/stack.sh.log
SCREEN_LOGDIR=/opt/stack/screen-logs
VERBOSE=True
DEBUG=True
USE_SCREEN=True
API_RATE_LIMIT=False
'''

LOCALCONF_COMPUTE = '''
[[local|localrc]]
HOST_IP={HOST_IP}
SERVICE_HOST={SERVICE_HOST}
MYSQL_HOST={SERVICE_HOST}
RABBIT_HOST={SERVICE_HOST}
GLANCE_HOSTPORT={SERVICE_HOST}:9292

MULTI_HOST=1

MYSQL_PASSWORD=nova
RABBIT_PASSWORD=nova
SERVICE_TOKEN=nova
SERVICE_PASSWORD=nova
ADMIN_PASSWORD=nova

ENABLED_SERVICES=n-cpu,neutron,n-api,n-novnc,q-agt

LIBVIRT_TYPE=qemu
NOVA_USE_QUANTUM_API=v2
VOLUME_BACKING_FILE_SIZE=2052M
Q_PLUGIN=ml2
Q_ML2_PLUGIN_MECHANISM_DRIVERS=openvswitch,cisco_nexus
Q_ML2_PLUGIN_TYPE_DRIVERS=vlan
Q_PLUGIN_EXTRA_CONF_PATH=({Q_PLUGIN_EXTRA_CONF_PATH})
Q_PLUGIN_EXTRA_CONF_FILES=({Q_PLUGIN_EXTRA_CONF_FILES})
ML2_VLAN_RANGES=physnet1:{vlan_start}:{vlan_end}
PHYSICAL_NETWORK=physnet1
OVS_PHYSICAL_BRIDGE=br-eth1
TENANT_VLAN_RANGE={vlan_start}:{vlan_end}
ENABLE_TENANT_VLANS=True
ENABLE_TENANT_TUNNELS=False
Q_ML2_TENANT_NETWORK_TYPE=vlan
LOGFILE=/opt/stack/screen-logs/stack.sh.log
SCREEN_LOGDIR=/opt/stack/screen-logs
VERBOSE=True
DEBUG=True
USE_SCREEN=True
'''

# ML2_CONF_INI = '''
# [ml2_cisco]
# managed_physical_network = physnet1
#
# [ml2_mech_cisco_nexus:{router_ip}]
# {host}={port}
# ssh_port=22
# username={username}
# password={password}
# '''

ML2_CONF_INI = '''
[ml2_cisco]
managed_physical_network = physnet1

[ml2_mech_cisco_nexus:{router_ip}]
server1=2/1
server2=2/2
ssh_port=22
username={username}
password={password}
'''


class ML2MutinodeTest(MultinodeTestCase):

    @classmethod
    def setUpClass(cls):
        MultinodeTestCase.setUpClass()

        cls.controller = DevStack(host_string=cls.outputs['server1_nexus_ci_ip'],
                                  clone_path='~/devstack')
        cls.controller.local_conf = LOCALCONF_CONTROLLER.format(
            neutron_repo=urlparse.urljoin(ZUUL_URL, ZUUL_PROJECT),
            neutron_branch=ZUUL_REF,
            HOST_IP=cls.outputs['server1_nexus_ci_ip'],
            Q_PLUGIN_EXTRA_CONF_PATH=cls.controller._clone_path,
            Q_PLUGIN_EXTRA_CONF_FILES=Q_PLUGIN_EXTRA_CONF_FILES,
            vlan_start=NEXUS_VLAN_START, vlan_end=NEXUS_VLAN_END,
            JOB_LOG_PATH=SCREEN_LOG_PATH)
        cls.controller.clone()
        # Create ml2 config for cisco plugin. Put it to controller node
        with settings(host_string=cls.outputs['server1_nexus_ci_ip']):
            host = run('hostname')
            ml2_conf_io = StringIO.StringIO()
            ml2_conf_io.write(
                ML2_CONF_INI.format(
                    host=host, port=NEXUS_INTF_NUM, router_ip=NEXUS_IP,
                    username=NEXUS_USER,
                    password=NEXUS_PASSWORD))
            put(ml2_conf_io, os.path.join(cls.controller._clone_path,
                                          Q_PLUGIN_EXTRA_CONF_FILES))

        cls.compute = DevStack(host_string=cls.outputs['server2_nexus_ci_ip'],
                               clone_path='~/devstack')
        cls.compute.local_conf = LOCALCONF_COMPUTE.format(
            neutron_repo=urlparse.urljoin(ZUUL_URL, ZUUL_PROJECT),
            neutron_branch=ZUUL_REF,
            HOST_IP=cls.outputs['server2_nexus_ci_ip'],
            SERVICE_HOST=cls.outputs['server1_nexus_ci_ip'],
            Q_PLUGIN_EXTRA_CONF_PATH=cls.controller._clone_path,
            Q_PLUGIN_EXTRA_CONF_FILES=Q_PLUGIN_EXTRA_CONF_FILES,
            vlan_start=NEXUS_VLAN_START, vlan_end=NEXUS_VLAN_END,
            JOB_LOG_PATH=SCREEN_LOG_PATH)
        cls.compute.clone()

    def test_tempest(self):
        self.assertTrue(self.controller.stack())
        self.assertTrue(self.compute.stack())

        # Add port to data network bridge
        for i in range(1, 3):
            man_ip = self.outputs.get('server{0}_nexus_ci_ip'.format(i))
            with settings(host_string=man_ip):
                run('sudo ovs-vsctl add-port br-eth1 eth1')

        self.controller.run_tempest(TEST_LIST_FILE)