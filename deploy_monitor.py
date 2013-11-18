#!/usr/bin/env python

import sys
import getopt
import pdb

from node import Server

import ConfigParser

config = ConfigParser.SafeConfigParser()
config.read('monitor.ini')

class Scripting():
    def __init__(self, argv):
        self.entry = None
        self.keywords = None
        self.address = None
        self.rootNode = Server()
        self.handle_opts(argv)
        self.piece = self.rootNode.piece(self.keywords, address=self.address)
        self.config = None
        self.parsing()

    def parsing(self):
        self.config = ConfigParser.SafeConfigParser()
        self.config.read('monitor.ini')

    def title(self, server):
        tags = "#######################"
        print colors.GREEN + tags + "  " + str(server) + "  " + tags + colors.END

    def deploy(self):
        if self.entry != 'check':   
            self.check()
        if hasattr(self, self.entry):
            deploying = getattr(self, self.entry)
            return deploying()

    def list(self):
        for server in self.piece:
            print colors.GREEN + str(server) + colors.END

    def check(self):
        scripts = self.config.options('script')
        shell = ""
        for script in scripts:
            shell += """
                echo -n "is_installed_%s:";
                test -x /usr/local/nagios/libexec/%s \
                && echo True || echo False;
                echo \;""" % (script, script)

        for server in self.piece:
            raw_status = server.execute("""
                    %s

                    echo -n "is_installed_Linux_pm:"
                    INC=`perl -e 'print \"@INC\"'`;
                    find ${INC} -name 'Linux.pm' -print 2> /dev/null \
                    | grep -q 'Linux.pm' && echo True || echo False;
                    echo \;
                    
                    echo -n "is_installed_nagios_plugin:";
                    test -d /usr/local/nagios/libexec && echo True || echo False;
                    echo \;

                    echo -n "is_installed_nrpe:";
                    test -d /usr/local/nagios/etc && echo True || echo False;
                    echo \;

                    echo -n "is_installed_utils_pm:";
                    test -e /usr/local/nagios/libexec/utils.pm \
                    && echo True || echo False;
                    echo \;

                    echo -n "version_perl:";
                    perl -v |  egrep v[0-9\.]+ -o
                    echo \;

                    echo -n "is_ping_opened:";
                    /sbin/iptables -nvL | grep icmp | grep -q '0.0.0.0\|%s' &>/dev/null\
                    && echo True || echo False
                    echo \;

                    echo -n "is_5666_opened:";
                    /sbin/iptables -nvL | grep 5666 | grep -q '%s' &>/dev/null\
                    && echo True || echo False
                    echo \;

                    echo -n "is_configured_nrpe:";
                    grep -q '%s' /etc/xinetd.d/nrpe &>/dev/null \
                    && echo True || echo False
                    echo \;
                    """ % (shell, server.s.ip_monitor, server.s.ip_monitor, server.s.ip_monitor))

            server.status = dict([ x.split()[0].split(':') for x in raw_status.split(';') if x ])

            if self.entry == 'check':
                self.title(server)
                names = server.status.keys()
                names.sort()
                for name in names:
                    print '%-40s    %s' % (name, server.status[name])

    def upgrade_perl(self):
        base_dir = self.config.get('basic', 'base_dir')
        file_name = self.config.get('tools', 'perl')
        file = base_dir + "/client/tools/" + file_name
        print file
        UUID = None
        for server in self.piece:
            if server.status['version_perl'] == 'v5.8.5':
                UUID = server.download(file, uuid=UUID)

        for server in self.piece:
            if server.status['version_perl'] == 'v5.8.5':
                server.execute("""
                        cd /tmp/ && \
                        tar zxf perl-5.8.9.tar.gz && \
                        cd perl-5.8.9 && \
                        ./Configure -de &> /dev/null && \
                        make &> /dev/null && \
                        make test &> /dev/null && \
                        make install &> /dev/null
                        """)
        

    def config_iptables(self):
        for server in self.piece:
            self.title(server)
            if server.status['is_ping_opened'] == 'False':
                server.execute("""
                        /sbin/iptables -I INPUT -i eth0 -p icmp -j ACCEPT
                        """)
            if server.status['is_5666_opened'] == 'False':
                server.execute("""
                        /sbin/iptables -I INPUT -s %s -p tcp --dport 5666 -j ACCEPT
                        """ % server.s.ip_monitor)

    def deploy_script(self):
        base_dir = self.config.get('basic', 'base_dir')
        scripts = self.config.options('script')
        for script in scripts:
            UUID = None
            file_name = self.config.get('script', script)
            file = base_dir + "/client/libexec/" + file_name
            AP = "\/usr\/local\/nagios\/libexec\/%s" % file_name
            OP = "/usr/local/nagios/libexec/%s" % file_name
            for server in self.piece:
                if server.status['is_installed_%s' % script] == 'False':
                    UUID = server.download(file, uuid=UUID)
            for server in self.piece:
                if server.status['is_installed_%s' % script] == 'False':
                    server.execute("""
                            mv /tmp/%s /usr/local/nagios/libexec/ &&
                            chmod +x /usr/local/nagios/libexec/%s;
                            grep -q nagios /etc/sudoers && \
                            (grep %s /etc/sudoers &> /dev/null \
                            || sed -i '/nagios/s/$/,%s/g' /etc/sudoers) \
                            || echo \"nagios ALL=NOPASSWD: %s\" \
                            >> /etc/sudoers
                            """ % (file_name, file_name, AP, AP, OP) )
        for server in self.piece:
            self.title(server)
            server.execute("""
                    sed -i \
                    's/^Defaults    requiretty/#Defaults    requiretty/g'\
                    /etc/sudoers
                    """)

    def install_tools(self):
        base_dir = self.config.get('basic', 'base_dir')

        for server in self.piece:
            self.title(server)
            # Install Sys-Statistics-Linux
            UUID = None
            file_name = self.config.get('tools', 'Linux_pm')
            file = base_dir + "/client/tools/" + file_name
            if server.status['is_installed_Linux_pm'] == 'False':
                UUID = server.download(file, uuid=UUID)
            if server.status['is_installed_Linux_pm'] == 'False':
                server.execute("""
                        cd /tmp && \
                        tar zxf Sys-Statistics-Linux-0.66.tar.gz && \
                        cd Sys-Statistics-Linux-0.66 && \
                        perl Makefile.PL &> /dev/null; \
                        make &> /dev/null && \
                        make test &> /dev/null && make install &> /dev/null
                        """)

            # create user: nagios
            server.execute("""
                    chattr -i /etc/shadow /etc/passwd; \
                    groupadd nagios; \
                    useradd -M -s /sbin/nologin nagios -g nagios; \
                    mkdir -p /usr/local/nagios/libexec/;
                    """)

            # Install nagios-plugins
            UUID = None
            file_name = self.config.get('tools', 'nagios_plugin')
            file = base_dir + "/client/tools/" + file_name
            if server.status['is_installed_nagios_plugin'] == 'False':
                UUID = server.download(file, uuid=UUID)
            if server.status['is_installed_nagios_plugin'] == 'False':
                server.execute("""
                    cd /tmp && \
                    tar zxf nagios-plugins-1.4.15.tar.gz && \
                    cd nagios-plugins-1.4.15 && \
                    ./configure --with-nagios-user=nagios \
                    --with-nagios-group=nagios \
                    --with-openssl=/usr/bin/openssl \
                    --enable-perl-modules \
                    --enable-redhat-pthread-workaround \
                    &>/dev/null && \
                    make &>/dev/null && \
                    make install &>/dev/null
                    """)

            # Install nrpe
            UUID = None
            UUID2 = None
            file_name = self.config.get('tools', 'nrpe')
            file_name2 = self.config.get('tools', 'xinetd_nrpe')
            file = base_dir + "/client/tools/" + file_name
            file2 = base_dir + "/client/" + file_name2
            if server.status['is_installed_nrpe'] == 'False':
                UUID = server.download(file, uuid=UUID)
                UUID2 = server.download(file, uuid=UUID2)
            if server.status['is_installed_nrpe'] == 'False':
                server.execute("""
                        cd /tmp && \
                        tar zxf nrpe-2.12.tar.gz && \
                        cd nrpe-2.12 && \
                        ./configure  > /dev/null 2>&1 ; \
                        make all > /dev/null 2>&1 && \
                        make install-plugin &>/dev/null && \
                        make install-daemon  &>/dev/null && \
                        make install-daemon-config &>/dev/null && \
                        make install-xinetd  &>/dev/null;
                        sed s/NAGIOSIP/%s/g /tmp/nrpe > /etc/xinetd.d/nrpe:
                        killall nrpe ;
                        /etc/init.d/xinetd restart && \
                        chkconfig --level 345 xinetd on
                        """ % server.s.ip_monitor)

            # Install utils_pm
            UUID = None
            file_name = self.config.get('tools', 'utils_pm')
            file = base_dir + "/client/tools/" + file_name
            if server.status['is_installed_utils_pm'] == 'False':
                UUID = server.download(file, uuid=UUID)
                server.execute("""
                        mv /tmp/%s /usr/local/nagios/libexec
                        """ % file_name)

    def test_script(self):
        for server in self.piece:
            self.title(server)
            commands = self.config.items('test_commands')
            command_lines = ""
            for (command, command_line) in commands:
                command_lines += (command_line + ';')
            print server.execute(command_lines)

    def update_nrpe(self):
        for server in self.piece:
            self.title(server)
            nrpes = self.config.items('nrpe')
            shell = ""
            for name, value in nrpes:
                nrpe_line = "command[" + name + "]=" + value
                shell += """
                        sed -i '/command[%s/d' \
                        /usr/local/nagios/etc/nrpe.cfg;
                        echo "%s" >> \
                        /usr/local/nagios/etc/nrpe.cfg;
                        """ % (name, nrpe_line)
            server.execute(shell)
            
    def review_nrpe(self):
        for server in self.piece:
            self.title(server)
            print server.execute("""
                    egrep -v '^#|^$' \
                    /usr/local/nagios/etc/nrpe.cfg \
                    | egrep '^command\[.*\]'
                    """)

    def auto(self):
        self.upgrade_perl()
        self.install_tools()
        self.config_iptables()
        self.deploy_script()
        self.update_nrpe()

    def Usage(self):
        print
        print 'deploy_monitor.py usage:'
        print '\t%-17s %s' % ('-h, --help', 'print this help info.')
        print '\t%-17s %s' % ('-e, --entry', 'specify action entry will be executed')
        print '\t%-17s %s' % ('-k, --keywords', 'sepecify words used to filter servers')
        print '\t%-17s %s' % ('-a, --address', 'specify a server will be deployed')
        print
        print 'example:'
        print '\t%-37s %s' % ('-e list', 'list all avaliable action entries')
        print '\t%-37s %s' % ('-k vn,tlbb -e list', 'list all servers of vn tlbb projects')
        print '\t%-37s %s' % ('-k vn,tlbb -e auto', 'automatically deploy all servers of vn tlbb project')
        print '\t%-37s %s' % ('-k vn,tlbb -a 172.16.1.1 -e auto', 'automatically deploy a specified server of vn tlbb project')
        print 
        print 'all action entries:'
        print '\t%-17s %s' % ('list','list all servers suited for your keywords')
        print '\t%-17s %s' % ('auto','do everything automatically.')
        print '\t%-17s %s' % ('check','check current status')
        print '\t%-17s %s' % ('upgrade_perl','upgrade perl from v5.8.5 to v5.8.9')
        print '\t%-17s %s' % ('config_iptables','open ping and 5666 for nagios monitor servers')
        print '\t%-17s %s' % ('deploy_script','deploy all monitor scripts')
        print '\t%-17s %s' % ('test_script','test script')
        print '\t%-17s %s' % ('install_tools','instal nrpe and nagios plug-in')
        print '\t%-17s %s' % ('review_nrpe','review all your commands currently defined in nrpe.cfg')
        print '\t%-17s %s' % ('update_nrpe','update your nrpe commands')
        print 
    
    def handle_opts(self, argv):
        try:
            opts, args = getopt.getopt(argv[1:], 'hve:k:a:', ['help', 'version', 'entry=', 'keywords=', 'address='])
        except getopt.GetoptError, err:
            print str(err)
            Usage()
            sys.exit(2)
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                self.Usage()
                sys.exit(1)
            elif opt in ('-e', '--entry'):
                self.entry = arg
            elif opt in ('-k', '--keywords'):
                self.keywords = arg
            elif opt in ('-a', '--address'):
                self.address = arg
            else:
                print 'Unkonwn options.'
                sys.exit(3)

class colors:
    RED = '\033[01;31m'
    GREEN = '\033[01;32m'
    YELLOW = '\033[01;33m'
    PINK = '\033[01;34m'
    END = '\033[0m'

    def disable(self):
        self.RED = ''
        self.GREEN = ''
        self.YELLOW = ''
        self.PINK = ''
        self.END = ''
    
if __name__ == '__main__':
    deploying = Scripting(sys.argv)
    deploying.deploy()

