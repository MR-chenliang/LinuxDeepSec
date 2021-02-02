

#pylint: disable-msg=C0111
from volatility import renderers

import volatility.poolscan as poolscan
import volatility.plugins.common as common
import volatility.protos as protos
from volatility.renderers.basic import Address


class PoolScanSocket(poolscan.PoolScanner):
    """Pool scanner for tcp socket objects"""

    def __init__(self, address_space):
        poolscan.PoolScanner.__init__(self, address_space)

        self.struct_name = "_ADDRESS_OBJECT"
        self.pooltag = "TCPA"

        self.checks = [('CheckPoolSize', dict(condition = lambda x: x >= 0x15C)),
                   ('CheckPoolType', dict(non_paged = True, free = True)),
                   ## Valid sockets have time > 0
                   #('CheckSocketCreateTime', dict(condition = lambda x: x > 0)),
                   ('CheckPoolIndex', dict(value = lambda x : x < 5))
                   ]

class SockScan(common.AbstractScanCommand):
    """Pool scanner for tcp socket objects"""

    scanners = [PoolScanSocket]
    # Declare meta information associated with this plugin

    meta_info = dict(
        author = 'Brendan Dolan-Gavitt',
        copyright = 'Copyright (c) 2007,2008 Brendan Dolan-Gavitt',
        contact = 'bdolangavitt@wesleyan.edu',
        license = 'GNU General Public License 2.0',
        url = 'http://moyix.blogspot.com/',
        os = 'WIN_32_XP_SP2',
        version = '1.0',
        )

    @staticmethod
    def is_valid_profile(profile):
        return (profile.metadata.get('os', 'unknown') == 'windows' and
                profile.metadata.get('major', 0) == 5)

    text_sort_column = "port"

    def unified_output(self, data):

        return renderers.TreeGrid([(self.offset_column(), Address),
                                  ('PID', int),
                                  ('Port', int),
                                  ('Proto', int),
                                  ('Protocol', str),
                                  ('Address', str),
                                  ('Create Time', str)
                                  ], self.generator(data))

    def generator(self, data):
        for sock_obj in data:
            yield (0,
                           [Address(sock_obj.obj_offset),
                           int(sock_obj.Pid),
                           int(sock_obj.LocalPort),
                           int(sock_obj.Protocol),
                           str(protos.protos.get(sock_obj.Protocol.v(), "-")),
                           str(sock_obj.LocalIpAddress),
                           str(sock_obj.CreateTime)])

    def render_text(self, outfd, data):

        self.table_header(outfd, [(self.offset_column(), '[addrpad]'),
                                  ('PID', '>8'),
                                  ('Port', '>6'),
                                  ('Proto', '>6'),
                                  ('Protocol', '15'),
                                  ('Address', '15'),
                                  ('Create Time', '')
                                  ])

        for sock_obj in data:
            self.table_row(outfd,
                           sock_obj.obj_offset,
                           sock_obj.Pid,
                           sock_obj.LocalPort,
                           sock_obj.Protocol,
                           protos.protos.get(sock_obj.Protocol.v(), "-"),
                           sock_obj.LocalIpAddress,
                           sock_obj.CreateTime)
