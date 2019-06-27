from PyGroups import *
group = PyGroup()
group.callback(CMSG, utilities.default_msg)
group.callback(JOIN, utilities.default_join)
group.callback(LEAVE, utilities.default_leave)
group.join("ECP")
