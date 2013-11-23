#!/usr/bin/env python
import sys
import time
import random
import cmd
import paramiko
import threading
import ConfigParser
import fabric

config_file = ConfigParser.SafeConfigParser()
config_file.read('/tmp/duanchao/config.ini')

pkey_path = '/home/dagtlbb/.ssh/id_rsa'
s = paramiko.SSHClient()
s.load_system_host_keys()

yuenan_iplist = {'CCS': '180.148.132.3'}
malai_iplist = {'CCS': '14.192.68.61'}
taiwan_iplist = {'CCS': '211.72.205.100'}
xianggang_iplist = {'CCS': '210.5.189.118'}
beimei_iplist = {'CCS': '74.201.81.35'}
taiguo_iplist = {'CCS': '119.46.128.69'}


def multi_thread(main_proc, slave_proc):
    multi_thread = []
    main = threading.Thread(target=main_proc)
    main.setDaemon(True)
    multi_thread.append(main)
    slave = threading.Thread(target=slave_proc)
    multi_thread.append(slave)
    for i in range(2):
        multi_thread[i].start()
    multi_thread[1].join()
    multi_thread[0].join()
    print "\x1b[0;31m%s\x1b[0m" % ('command compelete~')


class First(cmd.Cmd):
    prompt = '[Please choose the area]>>'

    def do_yuenan(self, line):
        second_loop(yuenan_iplist, 'YueNan')

    def do_malai(self, line):
        second_loop(malai_iplist, 'MaLai')

    def do_taiwan(self, line):
        second_loop(taiwan_iplist, 'TaiWan')

    def do_xianggang(self, line):
        second_loop(xianggang_iplist, 'XiangGang')

    def do_beimei(self, line):
        second_loop(beimei_iplist, 'BeiMei')

    def do_taiguo(self, line):
        second_loop(taiguo_iplist, 'TaiGuo')

    def do_EOF(self):
        return True

    def emptyline(self):
        print


class Second(cmd.Cmd):
    def __init__(self, area):
        cmd.Cmd.__init__(self)
        cmd.Cmd.prompt = '[' + area + ']>>'

    def do_choose_area(self, line):
        First().cmdloop()

    def do_shell(self, line):
        stdin, stdout, stderr = s.exec_command(line)
        print "\n\x1b[0;32m%s\x1b[0m" % (stdout.read())
        print "\n\x1b[0;35m%s\x1b[0m" % (stderr.read())

    def emptyline(self):
        print


def second_loop(iplist, area_name):
    s.connect(hostname=iplist['CCS'], username='dagtlbb', key_filename=pkey_path)
    command = []
    script = []
    for i in config_file.sections():
        command.append(config_file.get(i, 'command'))
        script.append(config_file.get(i, 'script'))
    exec_command_func = [lambda self, line, i=i: exec_script(i) for i in script]
    for i in range(len(command)):
        setattr(Second, 'do_' + command[i], exec_command_func[i])
    Second(area_name).cmdloop()


def exec_script(script_name):
    stdin, stdout, stderr = s.exec_command('/home/dagtlbb/admin/test/' + script_name)
    print "\n\x1b[0;32m%s\x1b[0m" % (stdout.read())
    print "\n\x1b[0;35m%s\x1b[0m" % (stderr.read())


def show_story(self):
    story_df = open('/tmp/duanchao/story.txt', 'r')
    random_num = random.randint(1, 4)
    for i in story_df:
        if i.startswith(str(random_num)):
            for j in range(len(i)):
                if j % 50 == 0:
                    print "\n"
                sys.stdout.write(i[j])
                sys.stdout.flush()


if __name__ == '__main__':
    First().cmdloop()