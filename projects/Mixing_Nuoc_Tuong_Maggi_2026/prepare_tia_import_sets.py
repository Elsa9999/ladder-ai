# -*- coding: utf-8 -*-
"""
Tạo các thư mục import riêng cho từng CPU đang có trong TIA Portal.

Importer generic chọn CPU theo tên thư mục chứa "PLC_1" hoặc "PLC_2",
vì vậy không import trực tiếp output phẳng.
"""
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Ladder"))

from Agent_LAD_Library import TIALadderBuilder  # noqa: E402

PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "output"
IMPORT_DIR = PROJECT_DIR / "tia_import"


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_main_for_plc1() -> str:
    main = TIALadderBuilder(fb_name="Main", block_id="1", block_type="OB")
    
    # 1. Gọi logic điều khiển cơ sở
    main.add_network("PLC1 - Gọi logic khởi tạo recipe mặc định PLC1", [("CALL_FC", "FC_Init_Default_Recipe_PLC1")])
    main.add_network("PLC1 - gọi logic Bồn 1 và Bồn 2", [("CALL_FC", "FC_PLC1_Mixing")])
    main.add_network("PLC1 - gọi logic bồn chứa và lọc thành phẩm", [("CALL_FC", "FC_Bon_Chua_Loc")])
    main.add_network("PLC1 - cập nhật mirror HMI", [("CALL_FC", "FC_HMI_Mirror_PLC1")])
    
    # 2. Modbus RTU Sequencer (iStep 0..3)
    main.add_network("VFD Bon 2 Modbus - Request Step 0 (Ghi Control Word)", [
        ("CMP_EQ", "AI_VFD_Bon2_iStep", "0"),
        ("Coil", "AI_VFD_Bon2_Step0_Req")
    ])
    main.add_network("VFD Bon 2 Modbus - Request Step 1 (Ghi Freq Setpoint)", [
        ("CMP_EQ", "AI_VFD_Bon2_iStep", "1"),
        ("Coil", "AI_VFD_Bon2_Step1_Req")
    ])
    main.add_network("VFD Bon 2 Modbus - Request Step 2 (Đọc Status Word)", [
        ("CMP_EQ", "AI_VFD_Bon2_iStep", "2"),
        ("Coil", "AI_VFD_Bon2_Step2_Req")
    ])
    main.add_network("VFD Bon 2 Modbus - Request Step 3 (Đọc Actual Speed)", [
        ("CMP_EQ", "AI_VFD_Bon2_iStep", "3"),
        ("Coil", "AI_VFD_Bon2_Step3_Req")
    ])
    main.add_network("VFD Bon 2 Modbus - Reset iStep Trigger", [
        ("CMP_GE", "AI_VFD_Bon2_iStep", "4"),
        ("Coil", "AI_VFD_Bon2_iStep_Reset")
    ])
    main.add_network("VFD Bon 2 Modbus - Tang iStep", [
        ("NO", "AI_VFD_Bon2_MB_Done"),
        ("CTU", "AI_Timers_PLC1.AI_VFD_Bon2_MB_Counter", {"R": "AI_VFD_Bon2_iStep_Reset", "PV": "3"}, {"CV": "AI_VFD_Bon2_iStep"}, "Int")
    ])
    
    # Call Modbus Blocks
    main.add_network("VFD Bon 2 Modbus - Khoi tao RS-485", [
        ("GENERIC", "MB_COMM_LOAD", {
            "REQ": "AI_FirstScan",
            "PORT": "269",
            "BAUD": "9600",
            "PARITY": "2",
            "MB_DB": "MB_MASTER_DB"
        }, {
            "DONE": "AI_VFD_Bon2_MBCL_Done",
            "ERROR": "AI_VFD_Bon2_MBCL_Error",
            "STATUS": "AI_VFD_Bon2_MBCL_Status"
        }, {"Version": "2.1"}, "MB_COMM_LOAD_DB")
    ])
    
    main.add_network("VFD Bon 2 Modbus - Master Step 0 (Ghi Control Word)", [
        ("GENERIC", "MB_MASTER", {
            "REQ": "AI_VFD_Bon2_Step0_Req",
            "MB_ADDR": "1",
            "MODE": "1",
            "DATA_ADDR": "48502",
            "DATA_LEN": "1",
            "DATA_PTR": "AI_VFD_Bon2_MB_ControlWord"
        }, {
            "DONE": "AI_VFD_Bon2_MB_Done",
            "BUSY": "AI_VFD_Bon2_MB_Busy",
            "ERROR": "AI_VFD_Bon2_MB_Error",
            "STATUS": "AI_VFD_Bon2_MB_Status"
        }, {"Version": "2.2"}, "MB_MASTER_DB")
    ])
    
    main.add_network("VFD Bon 2 Modbus - Master Step 1 (Ghi Freq Setpoint)", [
        ("GENERIC", "MB_MASTER", {
            "REQ": "AI_VFD_Bon2_Step1_Req",
            "MB_ADDR": "1",
            "MODE": "1",
            "DATA_ADDR": "48503",
            "DATA_LEN": "1",
            "DATA_PTR": "AI_VFD_Bon2_MB_FreqSetpoint"
        }, {
            "DONE": "AI_VFD_Bon2_MB_Done",
            "BUSY": "AI_VFD_Bon2_MB_Busy",
            "ERROR": "AI_VFD_Bon2_MB_Error",
            "STATUS": "AI_VFD_Bon2_MB_Status"
        }, {"Version": "2.2"}, "MB_MASTER_DB")
    ])
    
    main.add_network("VFD Bon 2 Modbus - Master Step 2 (Doc Status Word)", [
        ("GENERIC", "MB_MASTER", {
            "REQ": "AI_VFD_Bon2_Step2_Req",
            "MB_ADDR": "1",
            "MODE": "0",
            "DATA_ADDR": "43202",
            "DATA_LEN": "1",
            "DATA_PTR": "AI_VFD_Bon2_MB_StatusWord"
        }, {
            "DONE": "AI_VFD_Bon2_MB_Done",
            "BUSY": "AI_VFD_Bon2_MB_Busy",
            "ERROR": "AI_VFD_Bon2_MB_Error",
            "STATUS": "AI_VFD_Bon2_MB_Status"
        }, {"Version": "2.2"}, "MB_MASTER_DB")
    ])
    
    main.add_network("VFD Bon 2 Modbus - Master Step 3 (Doc Actual Speed)", [
        ("GENERIC", "MB_MASTER", {
            "REQ": "AI_VFD_Bon2_Step3_Req",
            "MB_ADDR": "1",
            "MODE": "0",
            "DATA_ADDR": "43203",
            "DATA_LEN": "1",
            "DATA_PTR": "AI_VFD_Bon2_MB_ActualSpeed"
        }, {
            "DONE": "AI_VFD_Bon2_MB_Done",
            "BUSY": "AI_VFD_Bon2_MB_Busy",
            "ERROR": "AI_VFD_Bon2_MB_Error",
            "STATUS": "AI_VFD_Bon2_MB_Status"
        }, {"Version": "2.2"}, "MB_MASTER_DB")
    ])
    
    # 3. Giao tiếp Modbus TCP PLC1 - PLC2
    # Khởi tạo Connection Parameter
    main.add_network("Modbus TCP Client - Khoi tao Connection Param", [
        ("NO", "AI_FirstScan"),
        ("MOVE", "64", "DB_MB_TCP_Client_Conn_DB.MB_TCP.InterfaceId"),
        ("MOVE", "5", "DB_MB_TCP_Client_Conn_DB.MB_TCP.ID"),
        ("MOVE", "11", "DB_MB_TCP_Client_Conn_DB.MB_TCP.ConnectionType"),
        ("MOVE", "TRUE", "DB_MB_TCP_Client_Conn_DB.MB_TCP.ActiveEstablished"),
        ("MOVE", "2", "DB_MB_TCP_Client_Conn_DB.MB_TCP.AddressFamily"),
        ("MOVE", "192", "DB_MB_TCP_Client_Conn_DB.MB_TCP.RemoteAddress[1]"),
        ("MOVE", "168", "DB_MB_TCP_Client_Conn_DB.MB_TCP.RemoteAddress[2]"),
        ("MOVE", "0", "DB_MB_TCP_Client_Conn_DB.MB_TCP.RemoteAddress[3]"),
        ("MOVE", "2", "DB_MB_TCP_Client_Conn_DB.MB_TCP.RemoteAddress[4]"),
        ("MOVE", "502", "DB_MB_TCP_Client_Conn_DB.MB_TCP.RemotePort"),
        ("MOVE", "0", "DB_MB_TCP_Client_Conn_DB.MB_TCP.LocalPort")
    ])

    # Reset any command edge
    main.add_network("Handshake Client - Reset Any Cmd Edge Flag", [
        ("ResetCoil", "AI_MB_TCP_Any_Cmd_Edge")
    ])

    # Edge detection and old state updates
    main.add_network("Handshake Client - Start Edge", [
        ("NO", "AI_Nut_Khoi_Dong_Eff"),
        ("NC", "AI_Nut_Khoi_Dong_Eff_Old"),
        ("Coil", "AI_Nut_Khoi_Dong_Eff_Edge")
    ])
    main.add_network("Handshake Client - Start Old Update", [
        ("NO", "AI_Nut_Khoi_Dong_Eff"),
        ("Coil", "AI_Nut_Khoi_Dong_Eff_Old")
    ])
    main.add_network("Handshake Client - Set Any Edge (Start)", [
        ("NO", "AI_Nut_Khoi_Dong_Eff_Edge"),
        ("SetCoil", "AI_MB_TCP_Any_Cmd_Edge")
    ])

    main.add_network("Handshake Client - Stop Edge", [
        ("NO", "AI_Nut_Dung_Eff"),
        ("NC", "AI_Nut_Dung_Eff_Old"),
        ("Coil", "AI_Nut_Dung_Eff_Edge")
    ])
    main.add_network("Handshake Client - Stop Old Update", [
        ("NO", "AI_Nut_Dung_Eff"),
        ("Coil", "AI_Nut_Dung_Eff_Old")
    ])
    main.add_network("Handshake Client - Set Any Edge (Stop)", [
        ("NO", "AI_Nut_Dung_Eff_Edge"),
        ("SetCoil", "AI_MB_TCP_Any_Cmd_Edge")
    ])

    main.add_network("Handshake Client - Reset Edge", [
        ("NO", "AI_Nut_Reset_Eff"),
        ("NC", "AI_Nut_Reset_Eff_Old"),
        ("Coil", "AI_Nut_Reset_Eff_Edge")
    ])
    main.add_network("Handshake Client - Reset Old Update", [
        ("NO", "AI_Nut_Reset_Eff"),
        ("Coil", "AI_Nut_Reset_Eff_Old")
    ])
    main.add_network("Handshake Client - Set Any Edge (Reset)", [
        ("NO", "AI_Nut_Reset_Eff_Edge"),
        ("SetCoil", "AI_MB_TCP_Any_Cmd_Edge")
    ])

    main.add_network("Handshake Client - EStop Edge", [
        ("NO", "AI_Nut_EStop_Eff"),
        ("NC", "AI_Nut_EStop_Eff_Old"),
        ("Coil", "AI_Nut_EStop_Eff_Edge")
    ])
    main.add_network("Handshake Client - EStop Old Update", [
        ("NO", "AI_Nut_EStop_Eff"),
        ("Coil", "AI_Nut_EStop_Eff_Old")
    ])
    main.add_network("Handshake Client - Set Any Edge (EStop)", [
        ("NO", "AI_Nut_EStop_Eff_Edge"),
        ("SetCoil", "AI_MB_TCP_Any_Cmd_Edge")
    ])

    main.add_network("Handshake Client - Transfer Edge", [
        ("NO", "AI_Pump3265_Chuyen_Nhanh2_Cmd"),
        ("NC", "AI_Pump3265_Chuyen_Nhanh2_Cmd_Old"),
        ("Coil", "AI_Pump3265_Chuyen_Nhanh2_Cmd_Edge")
    ])
    main.add_network("Handshake Client - Transfer Old Update", [
        ("NO", "AI_Pump3265_Chuyen_Nhanh2_Cmd"),
        ("Coil", "AI_Pump3265_Chuyen_Nhanh2_Cmd_Old")
    ])
    main.add_network("Handshake Client - Set Any Edge (Transfer)", [
        ("NO", "AI_Pump3265_Chuyen_Nhanh2_Cmd_Edge"),
        ("SetCoil", "AI_MB_TCP_Any_Cmd_Edge")
    ])

    main.add_network("Handshake Client - Load Recipe Edge", [
        ("NO", "AI_PLC1_Load_Default_Cmd"),
        ("NC", "AI_PLC1_Load_Default_Cmd_Old"),
        ("Coil", "AI_PLC1_Load_Default_Cmd_Edge")
    ])
    main.add_network("Handshake Client - Load Recipe Old Update", [
        ("NO", "AI_PLC1_Load_Default_Cmd"),
        ("Coil", "AI_PLC1_Load_Default_Cmd_Old")
    ])
    main.add_network("Handshake Client - Set Any Edge (Load Recipe)", [
        ("NO", "AI_PLC1_Load_Default_Cmd_Edge"),
        ("SetCoil", "AI_MB_TCP_Any_Cmd_Edge")
    ])

    # Latch command bits when edge detected
    main.add_network("Handshake Client - Latch Start", [
        ("NO", "AI_Nut_Khoi_Dong_Eff_Edge"),
        ("SetCoil", "DB_PLC1_Send_To_PLC2_DB.Cmd_Start")
    ])
    main.add_network("Handshake Client - Latch Stop", [
        ("NO", "AI_Nut_Dung_Eff_Edge"),
        ("SetCoil", "DB_PLC1_Send_To_PLC2_DB.Cmd_Stop")
    ])
    main.add_network("Handshake Client - Latch Reset", [
        ("NO", "AI_Nut_Reset_Eff_Edge"),
        ("SetCoil", "DB_PLC1_Send_To_PLC2_DB.Cmd_Reset")
    ])
    main.add_network("Handshake Client - Latch EStop", [
        ("NO", "AI_Nut_EStop_Eff_Edge"),
        ("SetCoil", "DB_PLC1_Send_To_PLC2_DB.Cmd_EStop")
    ])
    main.add_network("Handshake Client - Latch Transfer", [
        ("NO", "AI_Pump3265_Chuyen_Nhanh2_Cmd_Edge"),
        ("SetCoil", "DB_PLC1_Send_To_PLC2_DB.Cmd_Pump_Branch2_To_SubTanks")
    ])
    main.add_network("Handshake Client - Latch Load Recipe", [
        ("NO", "AI_PLC1_Load_Default_Cmd_Edge"),
        ("SetCoil", "DB_PLC1_Send_To_PLC2_DB.Cmd_Load_Recipe")
    ])

    # Increment CmdSeq on any edge
    main.add_network("Handshake Client - Increment CmdSeq", [
        ("NO", "AI_MB_TCP_Any_Cmd_Edge"),
        ("MATH_ADD", "DB_PLC1_Send_To_PLC2_DB.CmdSeq", "1", "DB_PLC1_Send_To_PLC2_DB.CmdSeq")
    ])

    # Clear latched commands on AckSeq == CmdSeq
    main.add_network("Handshake Client - Clear Latched Cmds on Ack", [
        ("CMP_EQ", "DB_PLC1_Recv_From_PLC2_DB.AckSeq", "DB_PLC1_Send_To_PLC2_DB.CmdSeq"),
        ("ResetCoil", "DB_PLC1_Send_To_PLC2_DB.Cmd_Start")
    ])
    main.add_network("Handshake Client - Clear Latched Stop on Ack", [
        ("CMP_EQ", "DB_PLC1_Recv_From_PLC2_DB.AckSeq", "DB_PLC1_Send_To_PLC2_DB.CmdSeq"),
        ("ResetCoil", "DB_PLC1_Send_To_PLC2_DB.Cmd_Stop")
    ])
    main.add_network("Handshake Client - Clear Latched Reset on Ack", [
        ("CMP_EQ", "DB_PLC1_Recv_From_PLC2_DB.AckSeq", "DB_PLC1_Send_To_PLC2_DB.CmdSeq"),
        ("ResetCoil", "DB_PLC1_Send_To_PLC2_DB.Cmd_Reset")
    ])
    main.add_network("Handshake Client - Clear Latched EStop on Ack", [
        ("CMP_EQ", "DB_PLC1_Recv_From_PLC2_DB.AckSeq", "DB_PLC1_Send_To_PLC2_DB.CmdSeq"),
        ("ResetCoil", "DB_PLC1_Send_To_PLC2_DB.Cmd_EStop")
    ])
    main.add_network("Handshake Client - Clear Latched Transfer on Ack", [
        ("CMP_EQ", "DB_PLC1_Recv_From_PLC2_DB.AckSeq", "DB_PLC1_Send_To_PLC2_DB.CmdSeq"),
        ("ResetCoil", "DB_PLC1_Send_To_PLC2_DB.Cmd_Pump_Branch2_To_SubTanks")
    ])
    main.add_network("Handshake Client - Clear Latched Load Recipe on Ack", [
        ("CMP_EQ", "DB_PLC1_Recv_From_PLC2_DB.AckSeq", "DB_PLC1_Send_To_PLC2_DB.CmdSeq"),
        ("ResetCoil", "DB_PLC1_Send_To_PLC2_DB.Cmd_Load_Recipe")
    ])

    # Sequencer step logic
    main.add_network("Modbus TCP Client - Request Write (Step 0)", [
        ("CMP_EQ", "AI_MB_TCP_iStep", "0"),
        ("Coil", "AI_MB_TCP_Write_Req")
    ])
    main.add_network("Modbus TCP Client - Request Read (Step 1)", [
        ("CMP_EQ", "AI_MB_TCP_iStep", "1"),
        ("Coil", "AI_MB_TCP_Read_Req")
    ])

    # Call MB_CLIENT Write
    main.add_network("Modbus TCP Client - Call MB_CLIENT Write (Step 0)", [
        ("GENERIC", "MB_CLIENT", {
            "REQ": "AI_MB_TCP_Write_Req",
            "DISCONNECT": "FALSE",
            "MB_MODE": "1",
            "MB_DATA_ADDR": "40001",
            "MB_DATA_LEN": "3",
            "MB_DATA_PTR": "DB_PLC1_Send_To_PLC2_DB",
            "CONNECT": "DB_MB_TCP_Client_Conn_DB.MB_TCP"
        }, {
            "DONE": "AI_MB_TCP_Write_Done",
            "ERROR": "AI_MB_TCP_Write_Error",
            "STATUS": "AI_MB_TCP_Write_Status"
        }, {"Version": "4.0"}, "MB_CLIENT_DB")
    ])

    # Call MB_CLIENT Read
    main.add_network("Modbus TCP Client - Call MB_CLIENT Read (Step 1)", [
        ("GENERIC", "MB_CLIENT", {
            "REQ": "AI_MB_TCP_Read_Req",
            "DISCONNECT": "FALSE",
            "MB_MODE": "0",
            "MB_DATA_ADDR": "40004",
            "MB_DATA_LEN": "10",
            "MB_DATA_PTR": "DB_PLC1_Recv_From_PLC2_DB",
            "CONNECT": "DB_MB_TCP_Client_Conn_DB.MB_TCP"
        }, {
            "DONE": "AI_MB_TCP_Read_Done",
            "ERROR": "AI_MB_TCP_Read_Error",
            "STATUS": "AI_MB_TCP_Read_Status"
        }, {"Version": "4.0"}, "MB_CLIENT_DB")
    ])

    # Step transitions
    main.add_network("Modbus TCP Client - Transition Step 0 to 1 (Done)", [
        ("CMP_EQ", "AI_MB_TCP_iStep", "0"),
        ("NO", "AI_MB_TCP_Write_Done"),
        ("MOVE", "1", "AI_MB_TCP_iStep")
    ])
    main.add_network("Modbus TCP Client - Transition Step 0 to 1 (Error)", [
        ("CMP_EQ", "AI_MB_TCP_iStep", "0"),
        ("NO", "AI_MB_TCP_Write_Error"),
        ("MOVE", "1", "AI_MB_TCP_iStep")
    ])
    main.add_network("Modbus TCP Client - Transition Step 1 to 0 (Done)", [
        ("CMP_EQ", "AI_MB_TCP_iStep", "1"),
        ("NO", "AI_MB_TCP_Read_Done"),
        ("MOVE", "0", "AI_MB_TCP_iStep")
    ])
    main.add_network("Modbus TCP Client - Transition Step 1 to 0 (Error)", [
        ("CMP_EQ", "AI_MB_TCP_iStep", "1"),
        ("NO", "AI_MB_TCP_Read_Error"),
        ("MOVE", "0", "AI_MB_TCP_iStep")
    ])
    main.add_network("Modbus TCP Client - iStep Safety Reset", [
        ("CMP_GE", "AI_MB_TCP_iStep", "2"),
        ("MOVE", "0", "AI_MB_TCP_iStep")
    ])

    # Heartbeat
    main.add_network("Modbus TCP Client - Increment Heartbeat", [
        ("NO", "AI_Clock_1Hz"),
        ("MATH_ADD", "DB_PLC1_Send_To_PLC2_DB.Heartbeat", "1", "DB_PLC1_Send_To_PLC2_DB.Heartbeat")
    ])

    # Map Received Status to Local tags
    main.add_network("Modbus TCP Client - Map Received PLC2 Status", [
        ("MOVE", "DB_PLC1_Recv_From_PLC2_DB.Done_Branch2", "AI_PLC2_Me_Nhanh2_Hoan_Thanh_Nhan"),
        ("MOVE", "DB_PLC1_Recv_From_PLC2_DB.Done_Recipe", "AI_PLC1_Load_Default_Done_Nhan"),
        ("MOVE", "DB_PLC1_Recv_From_PLC2_DB.Alarm", "AI_PLC2_Loi_Tong_Recv"),
        ("MOVE", "DB_PLC1_Recv_From_PLC2_DB.State", "AI_PLC2_State_Recv"),
        ("MOVE", "DB_PLC1_Recv_From_PLC2_DB.PID_Bon4_SP", "AI_PID_Bon4_SP_Recv"),
        ("MOVE", "DB_PLC1_Recv_From_PLC2_DB.PID_Bon4_PV", "AI_PID_Bon4_PV_Recv"),
        ("MOVE", "DB_PLC1_Recv_From_PLC2_DB.PID_Bon4_CV", "AI_PID_Bon4_CV_Recv")
    ])
    
    return main.generate_xml()


def build_main_for_plc2() -> str:
    main = TIALadderBuilder(fb_name="Main", block_id="1", block_type="OB")
    
    # 1. Modbus TCP Connection parameters initialization for PLC2 (Server)
    main.add_network("Modbus TCP Server - Khoi tao Connection Param", [
        ("NO", "AI_FirstScan"),
        ("MOVE", "64", "DB_MB_TCP_Server_Conn_DB.MB_TCP_SERVER.InterfaceId"),
        ("MOVE", "5", "DB_MB_TCP_Server_Conn_DB.MB_TCP_SERVER.ID"),
        ("MOVE", "11", "DB_MB_TCP_Server_Conn_DB.MB_TCP_SERVER.ConnectionType"),
        ("MOVE", "FALSE", "DB_MB_TCP_Server_Conn_DB.MB_TCP_SERVER.ActiveEstablished"),
        ("MOVE", "2", "DB_MB_TCP_Server_Conn_DB.MB_TCP_SERVER.AddressFamily"),
        ("MOVE", "192", "DB_MB_TCP_Server_Conn_DB.MB_TCP_SERVER.RemoteAddress[1]"),
        ("MOVE", "168", "DB_MB_TCP_Server_Conn_DB.MB_TCP_SERVER.RemoteAddress[2]"),
        ("MOVE", "0", "DB_MB_TCP_Server_Conn_DB.MB_TCP_SERVER.RemoteAddress[3]"),
        ("MOVE", "1", "DB_MB_TCP_Server_Conn_DB.MB_TCP_SERVER.RemoteAddress[4]"),
        ("MOVE", "0", "DB_MB_TCP_Server_Conn_DB.MB_TCP_SERVER.RemotePort"),
        ("MOVE", "502", "DB_MB_TCP_Server_Conn_DB.MB_TCP_SERVER.LocalPort")
    ])
    
    # 2. Call MB_SERVER block
    main.add_network("Modbus TCP Server - Call MB_SERVER", [
        ("GENERIC", "MB_SERVER", {
            "DISCONNECT": "FALSE",
            "MB_HOLD_REG": "DB_Modbus_Holding_Register_DB",
            "CONNECT": "DB_MB_TCP_Server_Conn_DB.MB_TCP_SERVER"
        }, {
            "ERROR": "AI_MB_TCP_Server_Error",
            "STATUS": "AI_MB_TCP_Server_Status"
        }, {"Version": "4.0"}, "MB_SERVER_DB")
    ])
    
    # 3. Detect CmdSeq change
    main.add_network("Handshake Server - Detect new CmdSeq", [
        ("CMP_NE", "DB_Modbus_Holding_Register_DB.CmdSeq", "AI_PLC2_Last_CmdSeq"),
        ("Coil", "AI_PLC2_CmdSeq_New")
    ])
    
    # 4. Map DB commands to local receive tags (pulse 1 scan)
    main.add_network("Handshake Server - Start command pulse", [
        ("NO", "AI_PLC2_CmdSeq_New"),
        ("NO", "DB_Modbus_Holding_Register_DB.Cmd_Start"),
        ("Coil", "AI_Nut_Khoi_Dong_Nhan")
    ])
    main.add_network("Handshake Server - Stop command pulse", [
        ("NO", "AI_PLC2_CmdSeq_New"),
        ("NO", "DB_Modbus_Holding_Register_DB.Cmd_Stop"),
        ("Coil", "AI_Nut_Dung_Nhan")
    ])
    main.add_network("Handshake Server - Reset command pulse", [
        ("NO", "AI_PLC2_CmdSeq_New"),
        ("NO", "DB_Modbus_Holding_Register_DB.Cmd_Reset"),
        ("Coil", "AI_Nut_Reset_Nhan")
    ])
    main.add_network("Handshake Server - EStop command pulse", [
        ("NO", "AI_PLC2_CmdSeq_New"),
        ("NO", "DB_Modbus_Holding_Register_DB.Cmd_EStop"),
        ("Coil", "AI_Nut_EStop_Nhan")
    ])
    main.add_network("Handshake Server - Transfer command pulse", [
        ("NO", "AI_PLC2_CmdSeq_New"),
        ("NO", "DB_Modbus_Holding_Register_DB.Cmd_Pump_Branch2_To_SubTanks"),
        ("Coil", "AI_Pump3265_Chuyen_Nhanh2_Cmd_Nhan")
    ])
    main.add_network("Handshake Server - Load Recipe command pulse", [
        ("NO", "AI_PLC2_CmdSeq_New"),
        ("NO", "DB_Modbus_Holding_Register_DB.Cmd_Load_Recipe"),
        ("Coil", "AI_PLC2_Load_Default_Cmd_Nhan")
    ])
    
    # 5. Gọi logic điều khiển cơ sở của PLC2
    main.add_network("PLC2 - Gọi logic khởi tạo recipe mặc định PLC2", [("CALL_FC", "FC_Init_Default_Recipe_PLC2")])
    main.add_network("PLC2 - gọi logic Bồn 3 và Bồn 4", [("CALL_FC", "FC_PLC2_Mixing")])
    main.add_network("PLC2 - cập nhật mirror HMI", [("CALL_FC", "FC_HMI_Mirror_PLC2")])
    
    # 6. Map dữ liệu từ PLC2 sang DB holding register trước khi gửi sang PLC1
    main.add_network("Modbus TCP Server - Map Status to Holding Register", [
        ("MOVE", "AI_PLC2_Me_Nhanh2_Hoan_Thanh", "DB_Modbus_Holding_Register_DB.Done_Branch2"),
        ("MOVE", "AI_PLC2_Load_Default_Done", "DB_Modbus_Holding_Register_DB.Done_Recipe"),
        ("MOVE", "AI_PLC2_Loi_Tong", "DB_Modbus_Holding_Register_DB.Alarm"),
        ("MOVE", "AI_PLC2_State", "DB_Modbus_Holding_Register_DB.State"),
        ("MOVE", "AI_PID_Bon4_SP", "DB_Modbus_Holding_Register_DB.PID_Bon4_SP"),
        ("MOVE", "AI_TT3219_Bon4_Eff", "DB_Modbus_Holding_Register_DB.PID_Bon4_PV"),
        ("MOVE", "AI_CV3216_Hoi_Bon4", "DB_Modbus_Holding_Register_DB.PID_Bon4_CV")
    ])
    
    # Heartbeat PLC2
    main.add_network("Modbus TCP Server - Increment Heartbeat", [
        ("NO", "AI_Clock_1Hz"),
        ("MATH_ADD", "DB_Modbus_Holding_Register_DB.Heartbeat_Server", "1", "DB_Modbus_Holding_Register_DB.Heartbeat_Server")
    ])
    
    # 7. Update AckSeq and Last_CmdSeq at the end of scan
    main.add_network("Handshake Server - Update AckSeq and Last_CmdSeq", [
        ("MOVE", "DB_Modbus_Holding_Register_DB.CmdSeq", "DB_Modbus_Holding_Register_DB.AckSeq"),
        ("MOVE", "DB_Modbus_Holding_Register_DB.CmdSeq", "AI_PLC2_Last_CmdSeq")
    ])
    
    return main.generate_xml()


def copy_from_output(target_dir: Path, filenames: list[str]) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    for filename in filenames:
        shutil.copy2(OUTPUT_DIR / filename, target_dir / filename)


def main() -> None:
    if IMPORT_DIR.exists():
        shutil.rmtree(IMPORT_DIR)

    plc1 = IMPORT_DIR / "PLC_1_Mixing_Import"
    plc2 = IMPORT_DIR / "PLC_2_Mixing_Import"

    copy_from_output(plc1, [
        "FC_Init_Default_Recipe_PLC1.xml",
        "FC_PLC1_Mixing.xml",
        "FC_Bon_Chua_Loc.xml",
        "FC_HMI_Mirror_PLC1.xml",
        "OB30_PID_PLC1_Bon2.xml",
        "Hmi.TextList.TL_Mixing_Step.xml",
        "Hmi.TextList.TL_Canh_Bao_Mixing.xml",
        "Hmi.TextList.TL_Phan_Quyen.xml",
        "AI_Timers_PLC1.xml",
        "DB_PLC1_Send_To_PLC2_DB.xml",
        "DB_PLC1_Recv_From_PLC2_DB.xml",
        "DB_MB_TCP_Client_Conn_DB.xml",
    ])
    shutil.copy2(OUTPUT_DIR / "AI_Tags_PLC1.xml", plc1 / "AI_Tags.xml")
    write_text(plc1 / "Main.xml", build_main_for_plc1())

    copy_from_output(plc2, [
        "FC_Init_Default_Recipe_PLC2.xml",
        "FC_PLC2_Mixing.xml",
        "FC_HMI_Mirror_PLC2.xml",
        "OB31_PID_PLC2_Bon4.xml",
        "AI_Timers_PLC2.xml",
        "DB_MB_TCP_Server_Conn_DB.xml",
        "DB_Modbus_Holding_Register_DB.xml",
    ])
    shutil.copy2(OUTPUT_DIR / "AI_Tags_PLC2.xml", plc2 / "AI_Tags.xml")
    write_text(plc2 / "Main.xml", build_main_for_plc2())

    print(f"Prepared TIA import sets under {IMPORT_DIR}")


if __name__ == "__main__":
    main()
