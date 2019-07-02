import re, json, time, socket
from GroupException import GroupException
from constants import *

def total_send (instance, fancy_data):
    receiving = instance._can_receive
    if receiving: instance.receiverOff()
    instance._command(N_REQUEST, instance._myself(), instance._target())
    message_queue = list()
    while True:
        instance._socket.settimeout(ACK_TIMEOUT) 
        try:
            data, address = instance._socket.recvfrom(DATA_LENGTH) # !TRATAR TIMEOUT
        except socket.timeout:
            if receiving: instance.receiverOn()
            return
        finally:
            instance._socket.settimeout(NO_TIMEOUT)
        if data:
            block = re.findall(HEADER_REGEX, data.decode(ENCODING))[0]
            body = re.findall(BODY_REGEX, data.decode(ENCODING)).pop()
            tag, tag_data = block.split(SPLIT_SEPARATOR)
            if tag == N_ANSWER:
                N = json.loads(tag_data)
                if receiving: instance.receiverOn()
                for message in message_queue: instance._socket.sendto(data, instance._myself())
                break
            elif tag == N_REQUEST:
                instance._total_n += 1
                instance._command(N_ANSWER, instance._total_n, json.loads(tag_data))
            else:
                message_queue.append(data)
    return ATTACH_MSG.format(TOTAL, N, fancy_data)
               
def causal_send (instance, fancy_data):
    instance._vetorclock[instance._mynumber()] += 1
    return ATTACH_MSG.format(CAUSAL, json.dumps((instance._vetorclock, instance._counter)), fancy_data)
