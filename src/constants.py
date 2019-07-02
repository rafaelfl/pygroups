NOT_A_MEMBER = 0
JOINING = -1
MAIN_MEMBER = 1
MEMBER = 2

DATA_LENGTH = 4096
ACK_TIMEOUT = 5
NO_TIMEOUT = None

PRINT_DELAY = 0.25
SHORT_DELAY = 0.25
DEFAULT_PORT = 15000
MAX_GROUPS = 10

SPLIT_SEPARATOR = '?'
HEADER_REGEX = '\[\\w*\]\?[^;-]*'
BODY_REGEX = '(?<=;).*'
JOIN_MSG = 'Entrou no grupo.'
VIEW_MSG = 'Vista do grupo atualizada.'
LEAVE_MSG = 'Saiu do grupo.'
REQUEST_MSG = 'Requisição.'
ERROR_MSG = 'NO PLS NO'
ENCODING = 'utf-8'
CMSG = "[CMSG]"
JOIN = "[JOIN]"
VIEW = "[VIEW]"
LEAVE = "[LEAVE]"
MAIN_LEAVE = "[MLEAVE]"
N_REQUEST = "[NREQUEST]"
N_ANSWER = "[NANSWER]"
ID_ATT = "[IDATT]"
TOTAL = "[TOTAL]"
RESEND = "[RESEND]"
BUFFER = "[BUFFER]"
NAME = "[NAME]"
CAUSAL = "[CAUSAL]"
VC_ATT = "[VCATT]"
COUNTER_ATT = "[CTATT]"
SIMPLE_MSG = "{0}?{1};{2}"
ATTACH_MSG = "{0}?{1}-{2}"
