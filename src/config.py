from reception_handlers import *
from dispatch_handlers import *
from constants import *

dhandlers = [total_send, causal_send]

rhandlers = [total_receive,
             total_id,
             total_n,
             causal_receive,
             causal_vc,
             join,
             leave,
             head_leave,
             view,
             resend,
             buffer,
             named_group,
             delivery]

callbacks = {JOIN: None,
             LEAVE: None,
             CMSG: None}
