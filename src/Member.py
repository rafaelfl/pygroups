class Member (dict):
    def __init__ (self, address, status):
        super(Member, self).__init__((('address', list(address)), ('status', status)))
