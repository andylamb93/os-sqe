from lab.deployers import Deployer


class DeployerExisting(Deployer):

    def sample_config(self):
        return {'cloud': 'arbitrary name', 'hardware-lab-config': 'yaml which describes the lab'}

    def __init__(self, config):
        super(DeployerExisting, self).__init__(config=config)
        self._lab_cfg = config['hardware-lab-config']
        self._cloud_name = config['cloud']

    @staticmethod
    def _its_ospd_installation(lab, list_of_servers):
        import json
        import re
        from lab import logger

        director = lab.get_director()
        body = director.get_file_from_dir('osp_install_run.json', '/etc')
        logger.OSP7_INFO = json.loads(body)

        net = lab.get_ssh_net()
        ssh_ip_pattern = '({0}.*)/{1}'.format(str(net).rsplit('.', 1)[0], net.prefixlen)
        re_ip = re.compile(ssh_ip_pattern)
        lines = director.run('source stackrc && nova list').split('\n')
        for line in lines:
            if '=' in line:
                local_ip = line.split('=')[-1].split()[0]
                #  name = line.split('|')[2]
                ip_a_ans = director.run('ssh -o StrictHostKeyChecking=no {local_ip} ip -o a'.format(local_ip=local_ip))
                ip = re_ip.findall(ip_a_ans)
                filter(lambda srv: srv.ip() == ip, list_of_servers)

    def deploy_cloud(self, list_of_servers):
        from lab.laboratory import Laboratory
        from lab.cloud import Cloud

        if not list_of_servers:
            lab = Laboratory(config_path=self._lab_cfg)
            list_of_servers.append(lab.get_director())
            list_of_servers.extend(lab.get_controllers())
            list_of_servers.extend(lab.get_computes())

        director = list_of_servers[0]

        openrc_path = None
        openrc_body = None
        for openrc_path in ['/home/stack/overcloudrc', 'keystonerc_admin']:
            ans = director.run(command='cat {0}'.format(openrc_path), warn_only=True)
            if 'No such file or directory' not in ans:
                openrc_body = ans
                break

        if not openrc_path:
            raise RuntimeError('Provided lab does not contain any valid cloud')

        for host in list_of_servers:
            host.actuate_hostname()
        return Cloud.from_openrc(name=self._cloud_name, mediator=director, openrc_as_string=openrc_body)

    def wait_for_cloud(self, list_of_servers):
        cloud = self.deploy_cloud(list_of_servers)
        return cloud.verify_cloud()
