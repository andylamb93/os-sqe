#from fabric.api import run, settings
from fabric.contrib.files import sed, uncomment, append

from fabric.operations import reboot, run, sudo, put
from fabric.context_managers import settings
with settings(host_string='10.0.197.13', user='localadmin', password= "password",
              abort_on_prompts=False):
    #ENVIRONMENT
    #controller: configure network interfaces
    # result=append('/etc/network/interfaces', '# The public network interface', use_sudo=True)
    # result=append('/etc/network/interfaces', 'auto eth0', use_sudo=True) #guess
    # result=append('/etc/network/interfaces', 'iface eth0 inet manual', use_sudo=True)
    # result=append('/etc/network/interfaces', 'up ip link set dev $IFACE up', use_sudo=True)
    # result=append('/etc/network/interfaces', 'down ip link set dev $IFACE down', use_sudo=True)
    # reboot(wait=180) #then login?
    # #configure name res
    # result=append('/etc/hosts', '10.0.197.13   controller', use_sudo=True)
    # result=append('/etc/hosts', '10.0.197.12   compute1', use_sudo=True)
    # #NTP
    # result=sudo('apt-get install chrony') #then change ntp server?
    # result=sudo('service chrony restart')
    # #OpenStack packages
    # result=sudo('apt-get install software-properties-common')
    # result=sudo('add-apt-repository cloud-archive:liberty')
    # result=sudo('apt-get update && apt-get dist-upgrade')
    # result=sudo('apt-get install python-openstackclient')
    # #SQL Database
    #result=sudo('apt-get install mariadb-server python-pymysql') #E: can't find python-pymysql on vm, password stuff?

    #NoSQL database
    #sudo('apt-get install mongodb-server mongodb-clients python-pymongo')
    #uncomment('/etc/mongodb.conf', bind_ip, use_sudo=True, char='#', shell=False) #unfinished
    #Message queue
    # result=sudo('apt-get install rabbitmq-server')
    # result=sudo('rabbitmqctl add_user openstack password')
    # result=sudo('rabbitmqctl set_permissions openstack ".*" ".*" ".*"')
    #
    # result = run('echo "create database if not exists keystone" | mysql -u root -ppassword')
    # result=run('mysql -u root -ppassword < "script.sql"')
    # result=run('mysql "script.sql"')
    # #Need to exit database?
    # result=sudo('echo "manual" > /etc/init/keystone.override')
    # print result
    # result=sudo('apt-get install keystone apache2 libapache2-mod-wsgi memcached python-memcache')
    # writing: http://docs.fabfile.org/en/1.11/api/contrib/files.html
    #result=uncomment('/etc/keystone/keystone.conf', admin_token, use_sudo=True, char='#', shell=False)
    #result=sed('/etc/keystone/keystone.conf', ADMIN_TOKEN,  password, shell=False)
    # result=uncomment('/etc/keystone/keystone.conf', 'connection =', use_sudo=True, char='#', shell=False)
    # result=sed('/etc/keystone/keystone.conf', '#connection = ', 'connection = mysql+pymysql://keystone:KEYSTONE_DBPASS@controller/keystone', shell=False)
    # result=uncomment('/etc/keystone/keystone.conf', 'servers = localhost:11211', use_sudo=True, char='#', shell=False)
    # result=uncomment('/etc/keystone/keystone.conf', 'provider = uuid', use_sudo=True, char='#', shell=False)
    # result=uncomment('/etc/keystone/keystone.conf', 'driver = sql', use_sudo=True, char='#', shell=False)
    # #   DO NOT change verbosity!
    # result=sudo('su -s /bin/sh -c "keystone-manage db_sync" keystone')
    # #Configure Apache http server
    # result=append('/etc/apache2/apache2.conf', 'ServerName controller', use_sudo=True)
    # result=put('wsgi-keystone.conf', '/etc/apache2/sites-available/wsgi-keystone.conf', use_sudo=True) #must upload file to js first
    # result=sudo('ln -s /etc/apache2/sites-available/wsgi-keystone.conf /etc/apache2/sites-enabled')
    # result=sudo('service apache2 restart') #stop keystone, restart apache2, start keystone
    # result=sudo('rm -f /var/lib/keystone/keystone.db')
    # #result=sudo('')
    token = '397a642b27e87069f90a'
    command = 'export OS_TOKEN={token} && export OS_URL=http://controller:35357/v3 && ' \
               'export OS_IDENTITY_API_VERSION=3 && '.format(token=token)
    # #  result = sudo('export OS_TOKEN=password')
    # # result = sudo('export OS_URL=http://controller:35357/v3')
    # # result = sudo('export OS_IDENTITY_API_VERSION=3')
    # #service creation
    # result = sudo(command + 'openstack service create --name keystone --description "OpenStack Identity" identity --os-username keystone --os-auth-url http://controller:35357/v3 --os-project-name keystone')
    # result = sudo(command + 'openstack endpoint create --region RegionOne\
    # identity public http://controller:5000/v2.0')
    # result = sudo(command + 'openstack endpoint create --region RegionOne\
    # identity internal http://controller:5000/v2.0')
    # result = sudo(command + 'openstack endpoint create --region RegionOne\
    # identity admin http://controller:5000/v2.0')
    # result = sudo(command + 'openstack project create --domain default \
    # --description "Admin Project" admin')
    # result = sudo(command + 'openstack user create --domain default \
    # --password-prompt admin')
    # result = sudo(command + 'openstack role create admin')
    # result = sudo(command + 'openstack role add --project admin --user admin admin')
    # result = sudo(command + 'openstack project create --domain default \
    # --description "Service Project" service')
    # result = sudo(command + 'openstack project create --domain default \
    #  --description "Demo Project" demo')
    # result = sudo(command + 'openstack user create --domain default \
    #  --password-prompt demo')
    # result = sudo(command + 'openstack role create user')
    # result = sudo(command + 'openstack role add --project demo --user demo user')
    #verify operation
    #result=sed('/etc/keystone/keystone.conf', 'admin_token_auth', '', shell=False)
    #edited keystone-paste manually
    ##result = sudo('unset OS_TOKEN OS_URL')
    # result = sudo('openstack --os-auth-url http://controller:35357/v3 \
    #  --os-project-domain-id default --os-user-domain-id default \
    # --os-project-name admin --os-username admin --os-auth-type password \
    # token issue')
    ##IMAGE
    result=put('scriptglance.sql', '/tmp/scriptglance.sql')
    result = run('echo "create database if not exists glance" | mysql -u root -ppassword')
    result=run('mysql -u root -ppassword < "/tmp/scriptglance.sql"')
    # result=run('mysql "/tmp/scriptglance.sql"')
    #Need to exit database?
    sudo(' source admin-openrc.sh')
    sudo('openstack user create --domain default --password-prompt glance')
    sudo('openstack role add --project service --user glance admin')
    sudo('openstack service create --name glance \
    --description "OpenStack Image service" image')
    sudo('openstack endpoint create --region RegionOne \
    image public http://controller:9292')
    sudo('openstack endpoint create --region RegionOne \
    image internal http://controller:9292')
    sudo('openstack endpoint create --region RegionOne \
    image admin http://controller:9292')

def cmd(cmd, is_sudo=True):
    result = sudo(cmd) if is_sudo else run(cmd)
    print result
    if result.return_code == 1:
        raise Exception('ERROR')