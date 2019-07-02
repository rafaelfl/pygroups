import socket, time, select, re, base64, json, random
from PacketManager import PacketManager
from constants import *

def get_ip ():
    return socket.gethostbyname(socket.getfqdn())

ADDRESSER = (get_ip(), DEFAULT_PORT - 1)
HELPER = (get_ip(), DEFAULT_PORT - 2)

def get_address (group_name):
    address = ADDRESSER
    data = SIMPLE_MSG.format(NAME, json.dumps((address, group_name)), str()) 
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.settimeout(ACK_TIMEOUT)
    s.bind(address)
    for port in range(DEFAULT_PORT, DEFAULT_PORT + MAX_GROUPS):
        s.sendto(bytes(data, ENCODING), ('255.255.255.255', port))
    groups = list()
    while True:
        try:
            rdata, raddress = s.recvfrom(DATA_LENGTH)
            addr, name = json.loads(rdata)
            if name == group_name:
                rdata = addr
                break
            else:
                groups.append(addr)
        except socket.timeout:
            if groups:
                rdata = (get_ip(), max(groups, key = lambda x: x[1])[1] + 1)
            else:
                rdata = (get_ip(), DEFAULT_PORT)
            break
    return rdata

def is_ready (socket):
    return bool(select.select((socket, ), list(), list(), 0)[0])

def split_data (data):
    header = re.findall(HEADER_REGEX, data)
    body = re.search(BODY_REGEX, data).group()
    return (header, body)

def block_while (condition):
    while condition: pass

def encode (data):
    return base64.b64encode(bytes(data, ENCODING)).decode()

def decode (data):
    return base64.b64decode(bytes(data, ENCODING)).decode()

def __static__ (f):
    f.var = False
    return f

@__static__
def sniffer (header, body):
    block_while(sniffer.var)
    sniffer.var = True
    time.sleep(PRINT_DELAY)
    print("\nHeader:", str().join(header))
    print("Body:", body)
    sniffer.var = False

def refuse_once (group):
    pm = PacketManager(group._socket)
    pm.refuse()

def delay_once (group, t):
    pm = PacketManager(group._socket)
    pm.delay(t)

def default_msg (address, text):
    print('\n#### MENSAGEM RECEBIDA #####\n%s : %s' % (address, text))

def default_join (address, text):
    print('\n#### MENSAGEM RECEBIDA #####\n%s : %s' % (address, JOIN_MSG))

def default_leave (address, text):
    print('\n#### MENSAGEM RECEBIDA #####\n%s : %s' % (address, LEAVE_MSG))
