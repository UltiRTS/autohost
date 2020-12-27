
def cmdWrite(ctl, cmd):
    if not type(cmd) is dict:
        raise Exception('Passed ' + type(cmd) + ' needed dictionary')

    result = ctl
            
    for key in cmd:
        arg = cmd[key]

        if type(key) is str and type(arg) is str:
            key = key.replace('--','')
            arg = arg.replace('--','')

            result += ' --' + key
            if len(arg) > 0:
                result += ' ' + arg
        
        else:
            raise Exception('All cmds must be strings')

    return result

def cmdRead(cmd_string):
    if not type(cmd_string) is str:
        raise Exception('Passed ' + type(key) + ' needed string')
    
    split = cmd_string.split('--')
    ctl = split[0].rstrip()
    cmd = {}

    for i in range(1, len(split)):
        cmd_args = split[i].rstrip().split(' ', 1)
        arg = ''

        if len(cmd_args) > 1:
            arg = cmd_args[1]

        cmd[cmd_args[0]] = arg
        
    return ctl, cmd 

#cmd = {'start': '', 'poll': '0.5', 'room': '1124', 'msg': 'this is a test message --poll 0.25'}
#encoded = cmdWrite('lobbyctl', cmd)
#ctl, decoded = cmdRead(encoded)
#print(cmdRead('sysctl --host aaa --type ffa')[1]["type2"])
#print(cmd)
#print(encoded)
#print(ctl)
#print(decoded)
