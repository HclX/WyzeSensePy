import os
import time
import struct
import threading
import select
import datetime
import argparse

import logging
log = logging.getLogger(__name__)

def str_to_hex(s):
    if s:
        return " ".join(["{:02x}".format(ord(x)) for x in s])
    else:
        return "<None>"

TYPE_SYNC   = 0x43
TYPE_ASYNC  = 0x53

def MAKE_CMD(type, cmd):
    return (type << 8) | cmd

class Packet(object):
    _CMD_TIMEOUT = 5

    # Sync packets:
    # Commands initiated from host side
    CMD_GET_ENR               = MAKE_CMD(TYPE_SYNC, 0x02)
    CMD_GET_MAC               = MAKE_CMD(TYPE_SYNC, 0x04)
    CMD_GET_KEY               = MAKE_CMD(TYPE_SYNC, 0x06)
    CMD_INQUIRY               = MAKE_CMD(TYPE_SYNC, 0x27)
    CMD_UPDATE_CC1310         = MAKE_CMD(TYPE_SYNC, 0x12)
    CMD_SET_CH554_UPGRADE     = MAKE_CMD(TYPE_SYNC, 0x0E)

    # Async packets:
    ASYNC_ACK                 = MAKE_CMD(TYPE_ASYNC, 0xFF)

    # Commands initiated from dongle side
    CMD_FINISH_AUTH           = MAKE_CMD(TYPE_ASYNC, 0x14)
    CMD_GET_DONGLE_VERSION    = MAKE_CMD(TYPE_ASYNC, 0x16)
    CMD_EANBLE_SCAN           = MAKE_CMD(TYPE_ASYNC, 0x1C)
    CMD_GET_SENSOR_R1         = MAKE_CMD(TYPE_ASYNC, 0x21)
    CMD_VERIFY_SENSOR         = MAKE_CMD(TYPE_ASYNC, 0x23)
    CMD_DEL_SENSOR            = MAKE_CMD(TYPE_ASYNC, 0x25)
    CMD_GET_SENSOR_COUNT      = MAKE_CMD(TYPE_ASYNC, 0x2E)
    CMD_GET_SENSOR_LIST       = MAKE_CMD(TYPE_ASYNC, 0x30)

    # Notifications initiated from dongle side
    NOTIFY_SENSOR_ALARM       = MAKE_CMD(TYPE_ASYNC, 0x19)
    NOTIFY_SENSOR_SCAN        = MAKE_CMD(TYPE_ASYNC, 0x20)
    NOITFY_SYNC_TIME          = MAKE_CMD(TYPE_ASYNC, 0x32)
    NOTIFY_EVENT_LOG          = MAKE_CMD(TYPE_ASYNC, 0x35)

    def __init__(self, cmd, payload = ""):
        self._cmd = cmd
        if self._cmd == self.ASYNC_ACK:
            assert isinstance(payload, int)
        else:
            assert isinstance(payload, str)
        self._payload = payload

    def __str__(self):
        if self._cmd == self.ASYNC_ACK:
            return "Packet: Cmd=%04X, Payload=ACK(%04X)" % (self._cmd, self._payload)
        else:
            return "Packet: Cmd=%04X, Payload=%s" % (self._cmd, str_to_hex(self._payload))

    @property
    def Length(self):
        if self._cmd == self.ASYNC_ACK:
            return 7
        else:
            return len(self._payload) + 7

    @property
    def Cmd(self):
        return self._cmd
    
    @property
    def Payload(self):
        return self._payload

    def Send(self, fd):
        pkt = struct.pack(">HB", 0xAA55, self._cmd >> 8)
        if self._cmd == self.ASYNC_ACK:
            pkt += struct.pack("BB", (self._payload & 0xFF), self._cmd & 0xFF)
        else:
            pkt += struct.pack("BB", len(self._payload) + 3, self._cmd & 0xFF)
            if self._payload:
                pkt += self._payload
        checksum = sum([ord(c) for c in pkt]) & 0xFFFF
        pkt += struct.pack(">H", checksum)
        log.debug("Sending: %s", str_to_hex(pkt))
        ss = os.write(fd, pkt)
        assert ss == len(pkt)

    @classmethod
    def Parse(cls, s):
        if len(s) < 5:
            log.error("Invalid packet: %s", str_to_hex(s))
            log.error("Invalid packet length: %d", len(s))
            return None

        magic, cmd_type, b2, cmd_id = struct.unpack_from(">HBBB", s)
        if magic != 0x55AA and magic != 0xAA55:
            log.error("Invalid packet: %s", str_to_hex(s))
            log.error("Invalid packet magic: %4X", magic)
            return None

        cmd = MAKE_CMD(cmd_type, cmd_id)
        if cmd == cls.ASYNC_ACK:
            assert len(s) >= 7
            s = s[:7]
            payload = MAKE_CMD(cmd_type, b2)
        else:
            assert len(s) >= b2 + 4
            s = s[: b2 + 4]
            payload = s[5:-2]

        cs_remote = (ord(s[-2]) << 8) | ord(s[-1])
        cs_local = sum([ord(x) for x in s[:-2]])
        if cs_remote != cs_local:
            log.error("Invalid packet: %s", str_to_hex(s))
            log.error("Mismatched checksum, remote=%04X, local=%04X", cs_remote, cs_local)
            return None

        return cls(cmd, payload)

    @classmethod
    def GetVersion(cls):
        return cls(cls.CMD_GET_DONGLE_VERSION)
    
    @classmethod
    def Inquiry(cls):
        return cls(cls.CMD_INQUIRY)
    
    @classmethod
    def GetEnr(cls, r):
        return cls(cls.CMD_GET_ENR, r)

    @classmethod
    def GetMAC(cls):
        return cls(cls.CMD_GET_MAC)
        
    @classmethod
    def GetKey(cls):
        return cls(cls.CMD_GET_KEY)

    @classmethod
    def EnableScan(cls, start):
        assert isinstance(start, bool)
        return cls(cls.CMD_EANBLE_SCAN, "\x01" if start else "\x00")

    @classmethod
    def GetSensorCount(cls):
        return cls(cls.CMD_GET_SENSOR_COUNT)

    @classmethod
    def GetSensorList(cls, count):
        assert count <= 0xFF
        return cls(cls.CMD_GET_SENSOR_LIST, struct.pack("B", count))

    @classmethod
    def FinishAuth(cls):
        return cls(cls.CMD_FINISH_AUTH, "\xFF")

    @classmethod
    def DelSensor(cls, mac):
        assert isinstance(mac, str)
        assert len(mac) == 8
        return cls(cls.CMD_DEL_SENSOR, mac)
    
    @classmethod
    def GetSensorR1(cls, mac, r):
        assert len(r) == 16
        assert isinstance(r, str)
        assert len(mac) == 8
        assert isinstance(mac, str)
        return cls(cls.CMD_GET_SENSOR_R1, mac + r)

    @classmethod
    def VerifySensor(cls, mac):
        assert len(mac) == 8
        assert isinstance(mac, str)
        return cls(cls.CMD_VERIFY_SENSOR, mac + "\xFF\x04")

    @classmethod
    def UpdateCC1310(cls):
        return cls(cls.CMD_UPDATE_CC1310)

    @classmethod
    def Ch554Upgrade(cls):
        return cls(cls.CMD_SET_CH554_UPGRADE)

    @classmethod
    def SyncTimeAck(cls):
        return cls(cls.NOITFY_SYNC_TIME + 1, struct.pack(">Q", int(time.time() * 1000)))

    @classmethod
    def AsyncAck(cls, cmd):
        assert (cmd >> 0x8) == TYPE_ASYNC
        return cls(cls.ASYNC_ACK, cmd)

class SensorEvent(object):
    def __init__(self, mac, timestamp):
        self.MAC = mac
        self.Timestamp = timestamp

    def __str__(self):
        return "[%s][%s]type=%s, state=%s, battery=%d%%, signal=%d" % (
            self.Timestamp.strftime("%Y-%m-%d %H:%M:%S"), self.MAC,
            self.Type, self.State, self.BatteryLevel, self.SignalStrength)

class WyzeSense(object):
    _CMD_TIMEOUT = 2

    class CmdContext():
        def __init__(self, **kwargs):
            for key in kwargs:
                setattr(self, key, kwargs[key])

    def _OnSensorAlarm(self, pkt):
        if len(pkt.Payload) < 18:
            log.info("Unknown alarm packet: %s", str_to_hex(pkt.Payload))
            return

        ts, _, sensor_mac = struct.unpack_from(">QB8s", pkt.Payload)

        evt = SensorEvent(sensor_mac, datetime.datetime.fromtimestamp(ts/1000.0))

        alarm_data = [ord(x) for x in pkt.Payload[17:]]
        if alarm_data[0] == 0x01:
            evt.Type = "switch"
            evt.State = "open" if alarm_data[5] == 1 else "close"
        elif alarm_data[0] == 0x02:
            evt.Type = "motion"
            evt.State = "active" if alarm_data[5] == 1 else "inactive"
        else:
            evt.Type = "uknown"
            evt.State = "unknown"

        evt.BatteryLevel = alarm_data[2]
        evt.SignalStrength = alarm_data[8]
        self.__on_event(self, evt)

    def _OnSyncTime(self, pkt):
        self._SendPacket(Packet.SyncTimeAck())

    def _OnEventLog(self, pkt):
        assert len(pkt.Payload) >= 9
        ts, msg_len = struct.unpack_from(">QB", pkt.Payload)
        # assert msg_len + 8 == len(pkt.Payload)
        tm = datetime.datetime.fromtimestamp(ts/1000.0)
        msg = pkt.Payload[9:]
        log.info("LOG: time=%s, data=%s", tm.isoformat(), str_to_hex(msg))

    def __init__(self, device, event_handler):
        self.__lock = threading.Lock()
        self.__fd = os.open(device, os.O_RDWR | os.O_NONBLOCK)
        self.__sensors = {}
        self.__exit_event = threading.Event()
        self.__thread = threading.Thread(target = self._Worker)
        self.__on_event = event_handler

        self.__handlers = {
            Packet.NOITFY_SYNC_TIME: self._OnSyncTime,
            Packet.NOTIFY_SENSOR_ALARM:  self._OnSensorAlarm,
            Packet.NOTIFY_EVENT_LOG: self._OnEventLog,
        }

        self.__thread.start()

    def _ReadRawHID(self):
        try:
            s = os.read(self.__fd, 0x40)
        except OSError:
            return ""

        if not s:
            log.info("Nothing read")
            return ""

        length = ord(s[0])
        assert length > 0
        if length > 0x3F:
            length = 0x3F

        #log.debug("Raw HID packet: %s", str_to_hex(s))
        assert len(s) >= length + 1
        return s[1: 1 + length]

    def _SetHandler(self, cmd, handler):
        with self.__lock:
            oldHandler = self.__handlers.pop(cmd, None)
            if handler:
                self.__handlers[cmd] = handler
        return oldHandler

    def _SendPacket(self, pkt):
        log.info("===> Sending: %s", str(pkt))
        pkt.Send(self.__fd)

    def _DefaultHandler(self, pkt):
        pass

    def _HandlePacket(self, pkt):
        log.info("<=== Received: %s", str(pkt))
        with self.__lock:
            handler = self.__handlers.get(pkt.Cmd, self._DefaultHandler)
        
        if (pkt.Cmd >> 8) == TYPE_ASYNC and pkt.Cmd != Packet.ASYNC_ACK:
            #log.info("Sending ACK packet for cmd %04X", pkt.Cmd)
            self._SendPacket(Packet.AsyncAck(pkt.Cmd))
        handler(pkt)

    def _Worker(self):
        s = ""
        while True:
            if self.__exit_event.isSet():
                break
            
            s += self._ReadRawHID()
            #if s:
            #    log.info("Incoming buffer: %s", str_to_hex(s))
            start = s.find("\x55\xAA")
            if start == -1:
                time.sleep(0.1)
                continue

            s = s[start:]
            log.debug("Trying to parse: %s", str_to_hex(s))
            pkt = Packet.Parse(s)
            if not pkt:
                s = s[2:]
                continue

            log.debug("Received: %s", str_to_hex(s[:pkt.Length]))
            s = s[pkt.Length:]
            self._HandlePacket(pkt)

    def _DoCommand(self, pkt, handler, timeout=_CMD_TIMEOUT):
        e = threading.Event()
        oldHandler = self._SetHandler(pkt.Cmd + 1, lambda pkt: handler(pkt, e))
        self._SendPacket(pkt)
        result = e.wait(timeout)
        self._SetHandler(pkt.Cmd + 1, oldHandler)

        return result

    def _DoSimpleCommand(self, pkt, timeout=_CMD_TIMEOUT):
        ctx = self.CmdContext(result = None)

        def cmd_handler(pkt, e):
            ctx.result = pkt
            e.set()

        self._DoCommand(pkt, cmd_handler, timeout)
        return ctx.result

    def _Inquiry(self):
        log.debug("Start Inquiry...")
        resp = self._DoSimpleCommand(Packet.Inquiry())
        if not resp:
            log.debug("Inquiry timed out...")
            return None

        assert len(resp.Payload) == 1
        result = ord(resp.Payload[0])
        log.debug("Inquiry returns %d", result)
        return result

    def _GetEnr(self, r):
        log.debug("Start GetEnr...")
        assert len(r) == 4
        assert all(isinstance(x,  (int, long)) for x in r)
        r_string = struct.pack("<LLLL", *r)

        resp = self._DoSimpleCommand(Packet.GetEnr(r_string))
        if not resp:
            log.debug("GetEnr timed out...")
            return None

        assert len(resp.Payload) == 16
        log.debug("GetEnr returns %s", str_to_hex(resp.Payload))
        return resp.Payload

    def _GetMac(self):
        log.debug("Start GetMAC...")
        resp = self._DoSimpleCommand(Packet.GetMAC())
        if not resp:
            log.debug("GetMac timed out...")
            return None

        assert len(resp.Payload) == 8
        log.debug("GetMAC returns %s", resp.Payload)
        return resp.Payload
    
    def _GetKey(self):
        log.debug("Start GetKey...")
        resp = self._DoSimpleCommand(Packet.GetKey())
        if not resp:
            log.debug("GetKey timed out...")
            return None

        assert len(resp.Payload) == 16
        log.debug("GetKey returns %s", resp.Payload)
        return resp.Payload
    
    def _GetVersion(self):
        log.debug("Start GetVersion...")
        resp = self._DoSimpleCommand(Packet.GetVersion())
        if not resp:
            log.debug("GetVersion timed out...")
            return None

        log.debug("GetVersion returns %s", resp.Payload)
        return resp.Payload

    def _GetSensors(self):
        log.debug("Start GetSensors...")

        resp = self._DoSimpleCommand(Packet.GetSensorCount())
        if not resp:
            log.debug("GetSensorCount timed out...")
            return None

        assert len(resp.Payload) == 1
        count = ord(resp.Payload[0])

        ctx = self.CmdContext(count=count, index=0, sensors=[])
        if count > 0:
            log.debug("%d sensors reported, waiting for each one to report...", count)
            def cmd_handler(pkt, e):
                assert len(pkt.Payload) == 8
                log.debug("Sensor %d/%d, MAC:%s", ctx.index + 1, ctx.count, pkt.Payload)

                ctx.sensors.append(pkt.Payload)
                ctx.index += 1
                if ctx.index == ctx.count:
                    e.set()

            if not self._DoCommand(Packet.GetSensorList(count), cmd_handler, timeout=self._CMD_TIMEOUT * count):
                log.debug("GetSensorList timed out...")
                return None
        else:
            log.debug("No sensors bond yet...")
        return ctx.sensors

    def _FinishAuth(self):
        resp = self._DoSimpleCommand(Packet.FinishAuth())
        if not resp:
            log.debug("FinishAuth timed out...")
            return False
        
        return True

    def Start(self):
        res = self._Inquiry()
        if not res:
            log.error("Inquiry failed")
            return False

        self.ENR = self._GetEnr([0x30303030] * 4)
        if not self.ENR:
            log.error("GetEnr failed")
            return False
        
        self.MAC = self._GetMac()
        if not self.MAC:
            log.error("GetMAC failed")
            return False
        log.debug("Dongle MAC is [%s]", self.MAC)

        res = self._GetVersion()
        if not res:
            log.error("GetVersion failed")
            return False
        self.Version = res
        log.debug("Dongle version: %s", self.Version)

        res = self._FinishAuth()
        if not res:
            log.error("FinishAuth failed")
            return False
        return True

    def List(self):
        sensors = self._GetSensors()
        for x in sensors:
            log.debug("Sensor found: %s", x)

        return sensors

    def Stop(self):
        self.__exit_event.set()
        os.close(self.__fd)
        self.__fd = None
        self.__thread.join()

    def Scan(self, timeout=60):
        log.debug("Start Scan...")

        ctx = self.CmdContext(evt=threading.Event(), result=None)
        def scan_handler(pkt):
            assert len(pkt.Payload) == 11
            ctx.result = (pkt.Payload[1:9], ord(pkt.Payload[9]), ord(pkt.Payload[10]))
            ctx.evt.set()
        
        oldHandler = self._SetHandler(Packet.NOTIFY_SENSOR_SCAN, scan_handler)
        res = self._DoSimpleCommand(Packet.EnableScan(True))
        if not res:
            log.debug("EnableScan timed out...")
            return None

        if ctx.evt.wait(timeout):
            s_mac, s_type, s_ver = ctx.result
            log.debug("Sensor found: mac=[%s], type=%d, version=%d", s_mac, s_type, s_ver)
            res = self._DoSimpleCommand(Packet.GetSensorR1(s_mac, 'Ok5HPNQ4lf77u754'))
            if not res:
                log.debug("GetSensorR1 timeout...")
        else:
            log.debug("Sensor discovery timeout...")

        res = self._DoSimpleCommand(Packet.EnableScan(False))
        if not res:
            log.debug("EnableScan timedout...")

        if ctx.result:
            s_mac, s_type, s_ver = ctx.result
            res = self._DoSimpleCommand(Packet.VerifySensor(s_mac))
            if not res:
                log.debug("VerifySensor timeout...")
        
        return (s_mac, s_type, s_ver)

    def Delete(self, mac):
        resp = self._DoSimpleCommand(Packet.DelSensor(mac))
        if not resp:
            log.debug("CmdDelSensor timed out...")
            return False

        log.debug("CmdDelSensor returns %s", str_to_hex(resp.Payload))
        assert len(resp.Payload) == 9
        ack_mac = resp.Payload[:8]
        ack_code = ord(resp.Payload[8])
        if ack_mac != mac:
            log.debug("CmdDelSensor: MAC mismatch, requested:%s, returned:%s", mac, ack_mac)
            return False

        if ack_code != 0xFF:
            log.debug("CmdDelSensor: Unexpected ACK code: %02X", ack_code)
            return False

        log.debug("CmdDelSensor: %s deleted", mac)
        return True

def Open(device, event_handler):
    ws = WyzeSense(device, event_handler)
    if ws.Start():
        return ws
    else:
        return None
