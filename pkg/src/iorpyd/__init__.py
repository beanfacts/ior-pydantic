from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
from enum import Enum


class AccessType(str, Enum):
    READ = "read"
    WRITE = "write"


def pprint_size(size: int) -> str:
    """
    Show size in human-readable format.
    """
    suffixes = [
        ("EiB", 2 ** 60),
        ("PiB", 2 ** 50),
        ("TiB", 2 ** 40),
        ("GiB", 2 ** 30),
        ("MiB", 2 ** 20),
        ("KiB", 2 ** 10),
        ("bytes", 1)
    ]
    
    for suffix, factor in suffixes:
        if size >= factor:
            return f"{size / factor:.2f} {suffix}"
    
    return "0 bytes"


def pprint_num(num: float) -> str:
    """
    Show number in human-readable format with SI suffix.
    """
    suffixes = [
        ("E", 1e18),
        ("P", 1e15),
        ("T", 1e12),
        ("G", 1e9),
        ("M", 1e6),
        ("K", 1e3)
    ]
    
    for suffix, factor in suffixes:
        if num >= factor:
            return f"{num / factor:.2f} {suffix}"
    
    return f"{num:.2f}"


def _parse_time(time_str: str) -> datetime:
    try:
        return datetime.strptime(time_str, "%a %b %d %H:%M:%S %Y")
    except ValueError:
        # Post-processed format
        return datetime.fromisoformat(time_str)


def _parse_size_str(size: str) -> int:
    """
    Converts the IOR size string (e.g., "4 MiB") to an integer number of
    bytes.
    """
    size, unit = size.strip().split()
    units = {
        "bytes": 1,
        "byte": 1,
        "KiB": 2 ** 10,
        "MiB": 2 ** 20,
        "GiB": 2 ** 30,
        "TiB": 2 ** 40,
        "PiB": 2 ** 50,
        "EiB": 2 ** 60
    }
    
    if unit not in units:
        raise ValueError(f"Unknown unit {unit}")
    
    return int(float(size) * units[unit])


class IORParameters(BaseModel):
    test_id: int = Field(alias="testID")
    refnum: int
    api: str
    platform: str
    test_file_name: str = Field(alias="testFileName")
    deadline_for_stonewall: int = Field(alias="deadlineForStonewall")
    stonewalling_wear_out: int = Field(alias="stoneWallingWearOut")
    max_time_duration: int = Field(alias="maxTimeDuration")
    outlier_threshold: int = Field(alias="outlierThreshold")
    options: Optional[str] = None
    dry_run: int = Field(alias="dryRun")
    nodes: int
    memory_per_task: int = Field(alias="memoryPerTask")
    memory_per_node: int = Field(alias="memoryPerNode")
    tasks_per_node: int = Field(alias="tasksPerNode")
    repetitions: int
    multi_file: int = Field(alias="multiFile")
    inter_test_delay: int = Field(alias="interTestDelay")
    fsync: int
    fsync_per_write: int = Field(alias="fsyncperwrite")
    use_existing_test_file: int = Field(alias="useExistingTestFile")
    unique_dir: int = Field(alias="uniqueDir")
    single_xfer_attempt: int = Field(alias="singleXferAttempt")
    read_file: int = Field(alias="readFile")
    write_file: int = Field(alias="writeFile")
    file_per_proc: int = Field(alias="filePerProc")
    reorder_tasks: int = Field(alias="reorderTasks")
    reorder_tasks_random: int = Field(alias="reorderTasksRandom")
    reorder_tasks_random_seed: int = Field(alias="reorderTasksRandomSeed")
    random_offset: int = Field(alias="randomOffset")
    check_write: int = Field(alias="checkWrite")
    check_read: int = Field(alias="checkRead")
    data_packet_type: int = Field(alias="dataPacketType")
    keep_file: int = Field(alias="keepFile")
    keep_file_with_error: int = Field(alias="keepFileWithError")
    warning_as_errors: int = Field(alias="warningAsErrors")
    verbose: int
    set_time_stamp_signature_incompressible_seed: int = Field(alias="setTimeStampSignature/incompressibleSeed")
    collective: int
    segment_count: int = Field(alias="segmentCount")
    transfer_size: int = Field(alias="transferSize")
    block_size: int = Field(alias="blockSize")

    @field_validator("options", mode="before")
    @classmethod
    def parse_options(cls, v):
        if isinstance(v, str) and v == "(null)":
            return None
        return v

    class Config:
        validate_by_name = True
        validate_by_alias = True


class IOROptions(BaseModel):
    api: str
    api_version: str = Field(alias="apiVersion")
    test_filename: str = Field(alias="test filename")
    access: str
    type: str
    segments: int
    ordering_in_a_file: str = Field(alias="ordering in a file")
    ordering_inter_file: str = Field(alias="ordering inter file")
    task_offset: Optional[int] = Field(default=None, alias="task offset")
    reorder_random_seed: Optional[int] = Field(default=None, alias="reorder random seed")
    nodes: int
    tasks: int
    clients_per_node: int = Field(alias="clients per node")
    memory_per_task: Optional[str] = Field(default=None, alias="memoryPerTask") # optional
    memory_per_node: Optional[str] = Field(default=None, alias="memoryPerNode") # optional
    memory_buffer: str = Field(alias="memoryBuffer")
    data_access: str = Field(alias="dataAccess")
    gpudirect: str = Field(alias="GPUDirect")
    repetitions: int
    xfersize: int
    blocksize: int
    aggregate_filesize: int = Field(alias="aggregate filesize")
    dry_run: Optional[int] = Field(default=None, alias="dryRun") # optional
    verbose: Optional[int] = Field(default=None, alias="verbose") # optional
    stonewalling_time: Optional[int] = Field(default=None, alias="stonewallingTime") # optional
    stonewall_wear_out: Optional[int] = Field(default=None, alias="stoneWallingWearOut") # optional

    @field_validator("xfersize", "blocksize", "aggregate_filesize", mode="before")
    @classmethod
    def parse_size_fields(cls, v):
        if isinstance(v, str):
            return _parse_size_str(v)
        return v

    class Config:
        validate_by_name = True
        validate_by_alias = True


class IORResult(BaseModel):
    access: AccessType
    bw_bytes: float = Field(alias="bwMiB") # converted
    block_bytes: int = Field(alias="blockKiB") # converted
    xfer_bytes: int = Field(alias="xferKiB") # converted
    iops: float
    latency: float
    open_time: float = Field(alias="openTime")
    wr_rd_time: float = Field(alias="wrRdTime")
    close_time: float = Field(alias="closeTime")
    total_time: float = Field(alias="totalTime")

    @field_validator("bw_bytes", mode="before")
    @classmethod
    def conv_mib(cls, v, info):
        aliases = {
            "bw_bytes": "bwMiB"
        }
        alias = aliases.get(info.field_name)
        if alias and alias in info.data:
            return v * (2 ** 20)
        return v

    # These fields should be integers, since the transfer/block sizes must be.
    @field_validator("block_bytes", "xfer_bytes", mode="before")
    @classmethod
    def conv_kib(cls, v, info):
        aliases = {
            "block_bytes": "blockKiB",
            "xfer_bytes": "xferKiB"
        }
        alias = aliases.get(info.field_name)
        if alias and alias in info.data:
            return round(v * (2 ** 10))
        return v

    class Config:
        validate_by_name = True
        validate_by_alias = True



class IORTest(BaseModel):
    test_id: int = Field(alias="TestID")
    start_time: datetime = Field(alias="StartTime")
    parameters: IORParameters = Field(alias="Parameters")
    options: IOROptions = Field(alias="Options")
    results: List[IORResult] = Field(alias="Results")

    @field_validator("start_time", mode="before")
    @classmethod
    def parse_time(cls, v):
        if isinstance(v, str):
            return _parse_time(v)
        return v

    class Config:
        validate_by_name = True
        validate_by_alias = True


class IORSummary(BaseModel):
    """IOR summary statistics for a test"""
    operation: AccessType
    api: str = Field(alias="API")
    test_id: int = Field(alias="TestID")
    reference_number: int = Field(alias="ReferenceNumber")
    segment_count: int = Field(alias="segmentCount")
    block_size: int = Field(alias="blockSize")
    transfer_size: int = Field(alias="transferSize")
    num_tasks: int = Field(alias="numTasks")
    tasks_per_node: int = Field(alias="tasksPerNode")
    repetitions: int
    file_per_proc: int = Field(alias="filePerProc")
    reorder_tasks: int = Field(alias="reorderTasks")
    task_per_node_offset: int = Field(alias="taskPerNodeOffset")
    reorder_tasks_random: int = Field(alias="reorderTasksRandom")
    reorder_tasks_random_seed: int = Field(alias="reorderTasksRandomSeed")
    bw_max_bytes: float = Field(alias="bwMaxMIB") # converted
    bw_min_bytes: float = Field(alias="bwMinMIB") # converted
    bw_mean_bytes: float = Field(alias="bwMeanMIB") # converted
    bw_std_bytes: float = Field(alias="bwStdMIB") # converted
    ops_max: float = Field(alias="OPsMax")
    ops_min: float = Field(alias="OPsMin")
    ops_mean: float = Field(alias="OPsMean")
    ops_sd: float = Field(alias="OPsSD")
    mean_time: float = Field(alias="MeanTime")
    stonewall_time: Optional[float] = Field(default=None, alias="StoneWallTime")
    stonewall_bw_mean_bytes: Optional[float] = Field(default=None, alias="StoneWallbwMeanMIB") # converted
    xsize_bytes: int = Field(alias="xsizeMiB") # converted

    @field_validator(
        "bw_max_bytes", "bw_min_bytes", "bw_mean_bytes", "bw_std_bytes",
        "stonewall_bw_mean_bytes", 
        mode="before"
    )
    @classmethod
    def conv_mib(cls, v, info):
        # Conversion is only necessary if we are importing the raw data
        # from IOR; if the field name is used directly, it means that
        # it was imported into this model, then exported, and is being
        # re-imported.
        if v is None:
            return None
        aliases = {
            "bw_max_bytes": "bwMaxMIB",
            "bw_min_bytes": "bwMinMIB",
            "bw_mean_bytes": "bwMeanMIB",
            "bw_std_bytes": "bwStdMIB",
            "stonewall_bw_mean_bytes": "StoneWallbwMeanMIB"
        }
        alias = aliases.get(info.field_name)
        if alias and alias in info.data:
            return v * (2 ** 20)
        return v 
    
    # Aggregate file size also an integer
    @field_validator("xsize_bytes", mode="before")
    @classmethod
    def conv_mib_rounded(cls, v, info):
        aliases = {
            "xsize_bytes": "xsizeMiB"
        }
        alias = aliases.get(info.field_name)
        if alias and alias in info.data:
            return round(v * (2 ** 20))
        return v

    class Config:
        validate_by_name = True
        validate_by_alias = True


class IOROutput(BaseModel):
    """Complete IOR output structure"""
    version: str = Field(alias="Version")
    began: datetime = Field(alias="Began")
    command_line: str = Field(alias="Command line")
    machine: str = Field(alias="Machine")
    tests: List[IORTest]
    summary: List[IORSummary]
    finished: datetime = Field(alias="Finished")

    @field_validator("began", "finished", mode="before")
    @classmethod
    def parse_time(cls, v):
        if isinstance(v, str):
            return _parse_time(v)
        return v

    class Config:
        validate_by_name = True
        validate_by_alias = True