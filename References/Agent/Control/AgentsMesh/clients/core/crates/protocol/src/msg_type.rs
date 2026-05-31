#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
#[repr(u8)]
pub enum MsgType {
    Snapshot = 0x01,
    Output = 0x02,
    Input = 0x03,
    Resize = 0x04,
    Ping = 0x05,
    Pong = 0x06,
    Control = 0x07,
    RunnerDisconnected = 0x08,
    RunnerReconnected = 0x09,
    Resync = 0x0a,
    AcpEvent = 0x0b,
    AcpCommand = 0x0c,
    AcpSnapshot = 0x0d,
}

impl MsgType {
    pub fn from_u8(val: u8) -> Option<Self> {
        match val {
            0x01 => Some(Self::Snapshot),
            0x02 => Some(Self::Output),
            0x03 => Some(Self::Input),
            0x04 => Some(Self::Resize),
            0x05 => Some(Self::Ping),
            0x06 => Some(Self::Pong),
            0x07 => Some(Self::Control),
            0x08 => Some(Self::RunnerDisconnected),
            0x09 => Some(Self::RunnerReconnected),
            0x0a => Some(Self::Resync),
            0x0b => Some(Self::AcpEvent),
            0x0c => Some(Self::AcpCommand),
            0x0d => Some(Self::AcpSnapshot),
            _ => None,
        }
    }
}
