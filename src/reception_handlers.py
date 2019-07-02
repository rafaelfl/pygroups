import re, json, time, socket
import utilities
from GroupException import GroupException
from Member import Member
from constants import *

def delivery (instance, tag, tag_data, body):
    if tag == CMSG:
        #print('###### Mensagem ###### {0} : {1}'.format(tag_data, body))
        if callable(instance._callbacks[CMSG]):
            instance._callbacks[CMSG](json.loads(tag_data), body)
        

def total_receive (instance, tag, tag_data, body):
    if tag == TOTAL:
        x = json.loads(tag_data)
        if x == instance._total_id + 1:
            instance._total_id += 1
        elif x > instance._total_id + 1:
            for i in range(instance._total_id + 1, x + 1):
                for member in instance._members:
                    instance._command(RESEND, (instance._myself(), i), member['address'])
            raise GroupException
        else:
            raise GroupException

def total_id (instance, tag, tag_data, body):
    if tag == ID_ATT:
        instance._total_id = json.loads(tag_data)

def total_n (instance, tag, tag_data, body):
    if tag == N_REQUEST:
        instance._total_n += 1
        instance._command(N_ANSWER, instance._total_n, json.loads(tag_data))

def resend (instance, tag, tag_data, body):
    if tag == RESEND:
        address, k = json.loads(tag_data)
        for msg in instance._msg_buffer:
            if msg.find("{0}?{1}".format(TOTAL, k)) != -1:
                instance._sendto(msg, address)

def causal_receive (instance, tag, parameters, body):
    if tag == CAUSAL:
        x = json.loads(parameters)
        for i in range(len(x[0])):
            instance._vetorclock[i] = max(x[0][i], instance._vetorclock[i])
            if(x[0][(x[1]-1)] == (instance._vetorclock[(x[1]-1)]+1)) and (x[0][i] <= instance._vetorclock[i]):
                pass
            elif(x[0][x[1]-1] >= (instance._vetorclock[x[1]-1]+1)) or (x[0][i] > instance._vetorclock[i]):
                for member in instance._members:
                    instance._socket.sendto(bytes(SIMPLE_MSG.format(RESEND, json.dumps((instance._myself(), i)), repr(REQUEST_MSG)), ENCODING), tuple(member['address']))
                #raise GroupException
            elif(x[0][x[1]-1] <= instance._vetorclock[x[1]-1]):
                raise GroupException
            else:
                raise GroupException

def causal_vc (instance, tag, parameters, body):
    if tag == VC_ATT:
        instance._vetorclock = json.loads(parameters)

def causal_counter (instance, tag, parameters, body):
    if tag == COUNTER_ATT:
        instance._counter = json.loads(parameters)

def buffer (instance, tag, tag_data, body):
    if tag == BUFFER:
        a_buffer = json.loads(utilities.decode(tag_data))
        instance._msg_buffer = list(set(instance._msg_buffer + a_buffer))

def join (instance, tag, tag_data, body):
    if tag == JOIN:
        new_member = Member(json.loads(tag_data), MEMBER)
        instance._members.append(new_member)
        instance._vetorclock.append(0)
        for member in instance._members:
            if member['address'] != list(instance._myself()):
                instance._command(VIEW, instance._members, member['address'])
        instance._command(ID_ATT, instance._total_id, new_member['address'])
        instance._socket.sendto(bytes(SIMPLE_MSG.format(VC_ATT, json.dumps(instance._vetorclock), REQUEST_MSG), ENCODING), tuple(new_member["address"]))
        instance._command(COUNTER_ATT, instance._counter, new_member['address'])
        instance._counter += 1
        if callable(instance._callbacks[JOIN]):
            instance._callbacks[JOIN](json.loads(tag_data), str())

def view (instance, tag, tag_data, body):
    if tag == VIEW:
        members = json.loads(tag_data)
        if len(instance._members) > len(members):
            instance._vetorclock.pop(instance._members.index([x for x in instance._members if x not in members].pop())) 
            if callable(instance._callbacks[LEAVE]):
                instance._callbacks[LEAVE](instance._members[-1]['address'], str())
        if len(instance._members) < len(members):
            instance._vetorclock.append(0)
            if callable(instance._callbacks[JOIN]):
                instance._callbacks[JOIN](members[-1]['address'], str())
        instance._members = members
        if instance._status in [NOT_A_MEMBER, JOINING]:
            instance._status = MEMBER
            
def leave (instance, tag, tag_data, body):
    if tag == LEAVE:
        ex_member = json.loads(tag_data)
        instance._members.remove(ex_member)
        for member in [ex_member] + instance._members:
            if member["address"] != list(instance._myself()):
                instance._command(VIEW, instance._members, member['address'])
        if callable(instance._callbacks[LEAVE]):
            instance._callbacks[LEAVE](ex_member['address'], str())

def head_leave (instance, tag, tag_data, body):
    if tag == MAIN_LEAVE:
        old_main, _total_n = json.loads(tag_data)
        if old_main['address'] != list(instance._myself()):
            instance._members.remove(old_main)
            is_new_main = bool(Member(instance._myself(), instance._status) == instance._members[0])
            instance._members[0]['status'] = MAIN_MEMBER
            instance._members[0]['address'][1] = old_main['address'][1]
            if is_new_main:
                address, port = instance._myself()
                instance._socket.close()
                instance._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                while True:
                    try:
                        instance._socket.bind((address, old_main['address'][1]))
                        break
                    except OSError:
                        pass
                instance._address = address
                instance._port = old_main['address'][1]
                instance._status = MAIN_MEMBER
                instance._total_n = _total_n
            else:
                instance._address, instance._port = instance._members[0]['address']
        if callable(instance._callbacks[LEAVE]):
            instance._callbacks[LEAVE](old_main['address'], str())

def named_group (instance, tag, tag_data, body):
    if tag == NAME:
        address, group_name = json.loads(tag_data)
        if instance.isMember():
            instance._sendto(json.dumps((instance._target(), instance.name())), address)
            
