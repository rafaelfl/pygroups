import socket, threading, json, time, re
import utilities, config
from GroupException import GroupException
from Member import Member
from constants import * 

class PyGroup:
    def __init__ (self):
        self._address = utilities.get_ip()
        self._port = DEFAULT_PORT
        self._members = list()
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._status = NOT_A_MEMBER
        self._total_id = 0 
        self._total_n = 0
        self._vetorclock = [0] 
        self._counter = 0 
        self._dispatchers = config.dhandlers
        self._receivers = config.rhandlers
        self._can_receive = False
        self._is_receiving = False
        self._is_sending = False
        self._msg_buffer = list()
        self._listen_thread = None
        self._callbacks = config.callbacks
        self._group_name = str()

    def _listen (self): 
        while self._can_receive:
            if utilities.is_ready(self._socket):
                self._is_receiving = True
                try: 
                    data, address = self._socket.recvfrom(DATA_LENGTH)
                except ConnectionResetError: # Alguém desconectou e não avisou.
                    self._is_receiving = False
                    break
                if data:
                    header, body = utilities.split_data(data.decode(ENCODING))
                    #utilities.sniffer(header, body)
                    for block in header:
                        try:
                            tag, tag_data = block.split(SPLIT_SEPARATOR)
                            if self._status in [MEMBER, MAIN_MEMBER]: # Requisito 17/06/2019
                                if not self._ismember(address) and address != utilities.HELPER:
                                    if tag not in [JOIN, NAME]:
                                        continue
                            else:
                                if tag not in [VIEW]:
                                    continue
                            for handler in self._receivers: 
                                handler(self, tag, tag_data, body)
                        except GroupException: # Pedido de cessão dos protocolos
                            break
                self._is_receiving = False

    def _sendto (self, data, address):
        self._socket.sendto(bytes(data, ENCODING), tuple(address))

    def _command (self, tag, tag_data, address):
        self._socket.sendto(bytes(SIMPLE_MSG.format(tag, json.dumps(tag_data), str()), ENCODING), tuple(address))

    def _myself (self): 
        return (utilities.get_ip(), self._socket.getsockname()[1])

    def _target (self): 
        return (self._address, self._port)

    def _ismember (self, address):
        return list(address) in [member['address'] for member in self._members]

    def _mynumber (self): 
        return self._members.index(Member(self._myself(), self._status)) 

    def join (self, group_name):
        if self._status == NOT_A_MEMBER:
            self._group_name = group_name
            print("Connecting...")
            self._address, self._port = utilities.get_address(group_name)
            print("Connected.")
            try:
                self._socket.bind(self._target())
                self._status = MAIN_MEMBER 
                self._members.append(Member(self._myself(), MAIN_MEMBER))
                if callable(self._callbacks[JOIN]):
                    self._callbacks[JOIN](list(self._myself()), str())
            except:
                self._sendto(str(), self._target())
                self._status = JOINING
                self._command(JOIN, self._myself(), self._target())
            self.receiverOn()
        else:
            raise GroupException("Você não pode executar esta operação.")

    def leave (self):
        print("Desconnecting...")
        utilities.block_while(self._is_sending)
        if self._status not in [NOT_A_MEMBER, MAIN_MEMBER]:
            self._command(BUFFER, utilities.encode(json.dumps(self._msg_buffer)), self._target())
            self._command(LEAVE, Member(self._myself(), self._status), self._target())
        elif self._status == MAIN_MEMBER:
            if len(self._members) > 1:
                self._command(BUFFER, utilities.encode(json.dumps(self._msg_buffer)), self._members[1]['address'])
            for member in self._members:
                self._command(MAIN_LEAVE, (Member(self._myself(), self._status), self._total_n), member['address'])
        elif self._status == NOT_A_MEMBER:
            raise GroupException("Você não é um membro.")
        self.receiverOff()
        time.sleep(ACK_TIMEOUT)
        print("Desconnected.")
        self._socket.close()
        self._members = list() 
        self._status = NOT_A_MEMBER 

    def send (self, text): 
        if self._status != NOT_A_MEMBER:
            self._is_sending = True 
            data = SIMPLE_MSG.format(CMSG, json.dumps(self._myself()), text) 
            for handler in self._dispatchers:
                data = handler(self, data)
            if data != None:
                self._msg_buffer.append(data)
            else:
                raise GroupException("Falha no envio da mensagem.")
                return
            for member in self._members:
                self._sendto(data, member['address'])
            self._is_sending = False 
        else:
            raise GroupException("Você não é um membro.")

    def sendTo (self, text, address): 
        if self._status != NOT_A_MEMBER:
            self._is_sending = True
            data = SIMPLE_MSG.format(CMSG, json.dumps(self._myself()), text)
            self._sendto(data, address)
            self._is_sending = False
        else:
            raise GroupException("Você não é um membro.")

    def receiverOn (self): 
        if not self._can_receive and self._status != NOT_A_MEMBER:
            self._can_receive = True
            self._listen_thread = threading.Thread(target = self._listen)
            self._listen_thread.start()
        else:
            raise GroupException("Este processo já está em andamento.")

    def receiverOff (self): 
        self._can_receive = False

    def isMember (self):
        return self._status not in [NOT_A_MEMBER, JOINING]

    def name (self):
        return self._group_name

    def callback (self, tag, func):
        if tag in self._callbacks:
            self._callbacks[tag] = func
        else:
            raise GroupException("Esta tag não pode receber uma callback.")
