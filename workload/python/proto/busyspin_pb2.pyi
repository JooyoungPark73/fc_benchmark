from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class FaasRequest(_message.Message):
    __slots__ = ("message", "runtimeInMilliSec", "memoryInMebiBytes", "ioSizeInBytes")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    RUNTIMEINMILLISEC_FIELD_NUMBER: _ClassVar[int]
    MEMORYINMEBIBYTES_FIELD_NUMBER: _ClassVar[int]
    IOSIZEINBYTES_FIELD_NUMBER: _ClassVar[int]
    message: str
    runtimeInMilliSec: int
    memoryInMebiBytes: int
    ioSizeInBytes: int
    def __init__(self, message: _Optional[str] = ..., runtimeInMilliSec: _Optional[int] = ..., memoryInMebiBytes: _Optional[int] = ..., ioSizeInBytes: _Optional[int] = ...) -> None: ...

class FaasReply(_message.Message):
    __slots__ = ("message", "durationInMicroSec", "memoryUsageInKb", "ioTimeInMicroSec")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DURATIONINMICROSEC_FIELD_NUMBER: _ClassVar[int]
    MEMORYUSAGEINKB_FIELD_NUMBER: _ClassVar[int]
    IOTIMEINMICROSEC_FIELD_NUMBER: _ClassVar[int]
    message: str
    durationInMicroSec: int
    memoryUsageInKb: int
    ioTimeInMicroSec: int
    def __init__(self, message: _Optional[str] = ..., durationInMicroSec: _Optional[int] = ..., memoryUsageInKb: _Optional[int] = ..., ioTimeInMicroSec: _Optional[int] = ...) -> None: ...
