PROTOCOL = 260

N_CONNECT = 0
N_SERVINFO = 1
N_WELCOME = 2
N_INITCLIENT = 3
N_POS = 4
N_TEXT = 5
N_SOUND = 6
N_CDIS = 7
N_SHOOT = 8
N_EXPLODE = 9
N_SUICIDE = 10
N_DIED = 11
N_DAMAGE = 12
N_HITPUSH = 13
N_SHOTFX = 14
N_EXPLODEFX = 15
N_TRYSPAWN = 16
N_SPAWNSTATE = 17
N_SPAWN = 18
N_FORCEDEATH = 19
N_GUNSELECT = 20
N_TAUNT = 21
N_MAPCHANGE = 22
N_MAPVOTE = 23
N_TEAMINFO = 24
N_ITEMSPAWN = 25
N_ITEMPICKUP = 26
N_ITEMACC = 27
N_TELEPORT = 28
N_JUMPPAD = 29
N_PING = 30
N_PONG = 31
N_CLIENTPING = 32
N_TIMEUP = 33
N_FORCEINTERMISSION = 34
N_SERVMSG = 35
N_ITEMLIST = 36
N_RESUME = 37
N_EDITMODE = 38
N_EDITENT = 39
N_EDITF = 40
N_EDITT = 41
N_EDITM = 42
N_FLIP = 43
N_COPY = 44
N_PASTE = 45
N_ROTATE = 46
N_REPLACE = 47
N_DELCUBE = 48
N_REMIP = 49
N_EDITVSLOT = 50
N_UNDO = 51
N_REDO = 52
N_NEWMAP = 53
N_GETMAP = 54
N_SENDMAP = 55
N_CLIPBOARD = 56
N_EDITVAR = 57
N_MASTERMODE = 58
N_KICK = 59
N_CLEARBANS = 60
N_CURRENTMASTER = 61
N_SPECTATOR = 62
N_SETMASTER = 63
N_SETTEAM = 64
N_BASES = 65
N_BASEINFO = 66
N_BASESCORE = 67
N_REPAMMO = 68
N_BASEREGEN = 69
N_ANNOUNCE = 70
N_LISTDEMOS = 71
N_SENDDEMOLIST = 72
N_GETDEMO = 73
N_SENDDEMO = 74
N_DEMOPLAYBACK = 75
N_RECORDDEMO = 76
N_STOPDEMO = 77
N_CLEARDEMOS = 78
N_TAKEFLAG = 79
N_RETURNFLAG = 80
N_RESETFLAG = 81
N_INVISFLAG = 82
N_TRYDROPFLAG = 83
N_DROPFLAG = 84
N_SCOREFLAG = 85
N_INITFLAGS = 86
N_SAYTEAM = 87
N_CLIENT = 88
N_AUTHTRY = 89
N_AUTHKICK = 90
N_AUTHCHAL = 91
N_AUTHANS = 92
N_REQAUTH = 93
N_PAUSEGAME = 94
N_GAMESPEED = 95
N_ADDBOT = 96
N_DELBOT = 97
N_INITAI = 98
N_FROMAI = 99
N_BOTLIMIT = 100
N_BOTBALANCE = 101
N_MAPCRC = 102
N_CHECKMAPS = 103
N_SWITCHNAME = 104
N_SWITCHMODEL = 105
N_SWITCHTEAM = 106
N_INITTOKENS = 107
N_TAKETOKEN = 108
N_EXPIRETOKENS = 109
N_DROPTOKENS = 110
N_DEPOSITTOKENS = 111
N_STEALTOKENS = 112
N_SERVCMD = 113
N_DEMOPACKET = 114

teammodes = [2, 4, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]

gamemodes = {
    0: "ffa",
    1: "coop_edit",
    2: "teamplay",
    3: "instagib",
    4: "insta_team",
    5: "efficiency",
    6: "effic_team",
    7: "tactics",
    8: "tac_team",
    9: "capture",
    10: "regen_capture",
    11: "ctf",
    12: "insta_ctf",
    13: "protect",
    14: "insta_protect",
    15: "hold",
    16: "insta_hold",
    17: "effic_ctf",
    18: "effic_protect",
    19: "effic_hold",
    20: "collect",
    21: "insta_collect",
    22: "effic_collect"
}

MM_AUTH = 255
MM_OPEN = 0
MM_VETO = 1
MM_LOCKED = 2
MM_PRIVATE = 3
MM_PASSWORD = 4

unicode_characters = [
    # Basic Latin (deliberately omitting most control characters)
    '\x00',
    # Latin-1 Supplement (selected letters)
    'À', 'Á', 'Â', 'Ã', 'Ä', 'Å', 'Æ',
    'Ç',
    # Basic Latin (cont.)
    '\t', '\n', '\v', '\f', '\r',
    # Latin-1 Supplement (cont.)
    'È', 'É', 'Ê', 'Ë',
    'Ì', 'Í', 'Î', 'Ï',
    'Ñ',
    'Ò', 'Ó', 'Ô', 'Õ', 'Ö', 'Ø',
    'Ù', 'Ú', 'Û',
    # Basic Latin (cont.)
    ' ', '!', '"', '#', '$', '%', '&', '\'', '(', ')', '*', '+', ',', '-', '.', '/',
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    ':', ';', '<', '=', '>', '?', '@',
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
    '[', '\\', ']', '^', '_', '`',
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    '{', '|', '}', '~',
    # Latin-1 Supplement (cont.)
    'Ü',
    'Ý',
    'ß',
    'à', 'á', 'â', 'ã', 'ä', 'å', 'æ',
    'ç',
    'è', 'é', 'ê', 'ë',
    'ì', 'í', 'î', 'ï',
    'ñ',
    'ò', 'ó', 'ô', 'õ', 'ö', 'ø',
    'ù', 'ú', 'û', 'ü',
    'ý', 'ÿ',
    # Latin Extended-A (selected letters)
    'Ą', 'ą',
    'Ć', 'ć', 'Č', 'č',
    'Ď', 'ď',
    'Ę', 'ę', 'Ě', 'ě',
    'Ğ', 'ğ',
    'İ', 'ı',
    'Ł', 'ł',
    'Ń', 'ń', 'Ň', 'ň',
    'Ő', 'ő', 'Œ', 'œ',
    'Ř', 'ř',
    'Ś', 'ś', 'Ş', 'ş', 'Š', 'š',
    'Ť', 'ť',
    'Ů', 'ů', 'Ű', 'ű',
    'Ÿ',
    'Ź', 'ź', 'Ż', 'ż', 'Ž', 'ž',
    # Cyrillic (selected letters, deliberately omitting letters visually identical to characters in Basic Latin)
    'Є',
    'Б',      'Г', 'Д', 'Ж', 'З', 'И', 'Й',      'Л',           'П',      'У', 'Ф', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ', 'Ы', 'Ь', 'Э', 'Ю', 'Я',
    'б', 'в', 'г', 'д', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'п', 'т',      'ф', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я',
    'є',
    'Ґ', 'ґ',
]