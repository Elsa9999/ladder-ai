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
    main.add_network("PLC1 - gọi logic VFD Bồn 2 Hybrid", [("CALL_FC", "FC_VFD_Bon2_Hybrid")])
    main.add_network("PLC1 - cập nhật mirror HMI", [("CALL_FC", "FC_HMI_Mirror_PLC1")])
    
    # 2. Modbus RTU Sequencer (iStep 0..3)
    main.add_network("VFD Bon 2 Modbus - Reset MBCL_Trigger chu ky truoc", [
        ("ResetCoil", "VFD_Bon2_MBCL_Trigger")
    ])
    main.add_network("VFD Bon 2 Modbus - Trigger MB_COMM_LOAD khi delay contactor xong", [
        ("NO", "FirstScan"),
        ("SetCoil", "VFD_Bon2_MBCL_Trigger")
    ])
    main.add_network("VFD Bon 2 Modbus - Khoi tao RS-485", [
        ("GENERIC", "MB_COMM_LOAD", {
            "REQ": "VFD_Bon2_MBCL_Trigger",
            "PORT": "269",
            "BAUD": "9600",
            "PARITY": "2",
            "FLOW_CTRL": "OPEN",
            "RTS_ON_DLY": "OPEN",
            "RTS_OFF_DLY": "OPEN",
            "RESP_TO": "OPEN",
            "MB_DB": "MB_MASTER_DB"
        }, {
            "DONE": "VFD_Bon2_MBCL_Done",
            "ERROR": "VFD_Bon2_MBCL_Error",
            "STATUS": "VFD_Bon2_MBCL_Status"
        }, {"Version": "2.1"}, "MB_COMM_LOAD_DB")
    ])
    main.add_network("VFD Bon 2 Modbus - SET CommReady khi MBCL Done", [
        ("NO", "VFD_Bon2_MBCL_Done"),
        ("SetCoil", "VFD_Bon2_Comm_Ready"),
        ("SetCoil", "VFD_Bon2_Comm_Active")
    ])
    main.add_network("VFD Bon 2 Modbus - Reset Ready va Active khi loi MBCL", [
        ("NO", "VFD_Bon2_MBCL_Error"),
        ("ResetCoil", "VFD_Bon2_Comm_Ready"),
        ("ResetCoil", "VFD_Bon2_Comm_Active")
    ])
    main.add_network("VFD Bon 2 Modbus - Reset Ready va Active khi mat Comm_Active", [
        ("NC", "VFD_Bon2_Comm_Active"),
        ("ResetCoil", "VFD_Bon2_Comm_Ready")
    ])
    main.add_network("VFD Bon 2 Modbus - Step 0 MODE", [
        ("CMP_EQ", "VFD_Bon2_iStep", "0"),
        ("MOVE", "1", "VFD_Bon2_MB_Mode")
    ])
    main.add_network("VFD Bon 2 Modbus - Step 0 DATA_ADDR", [
        ("CMP_EQ", "VFD_Bon2_iStep", "0"),
        ("MOVE", "48502", "VFD_Bon2_MB_DataAddr")
    ])
    main.add_network("VFD Bon 2 Modbus - Step 0 DATA_LEN", [
        ("CMP_EQ", "VFD_Bon2_iStep", "0"),
        ("MOVE", "1", "VFD_Bon2_MB_DataLen")
    ])
    main.add_network("VFD Bon 2 Modbus - Step 0 Write Buffer", [
        ("CMP_EQ", "VFD_Bon2_iStep", "0"),
        ("MOVE", "VFD_Bon2_MB_ControlWord", "VFD_Bon2_MB_DataBuffer")
    ])
    main.add_network("VFD Bon 2 Modbus - Step 1 MODE", [
        ("CMP_EQ", "VFD_Bon2_iStep", "1"),
        ("MOVE", "1", "VFD_Bon2_MB_Mode")
    ])
    main.add_network("VFD Bon 2 Modbus - Step 1 DATA_ADDR", [
        ("CMP_EQ", "VFD_Bon2_iStep", "1"),
        ("MOVE", "48503", "VFD_Bon2_MB_DataAddr")
    ])
    main.add_network("VFD Bon 2 Modbus - Step 1 DATA_LEN", [
        ("CMP_EQ", "VFD_Bon2_iStep", "1"),
        ("MOVE", "1", "VFD_Bon2_MB_DataLen")
    ])
    main.add_network("VFD Bon 2 Modbus - Step 1 Write Buffer", [
        ("CMP_EQ", "VFD_Bon2_iStep", "1"),
        ("MOVE", "VFD_Bon2_MB_FreqSetpoint", "VFD_Bon2_MB_DataBuffer")
    ])
    main.add_network("VFD Bon 2 Modbus - Step 2 MODE", [
        ("CMP_EQ", "VFD_Bon2_iStep", "2"),
        ("MOVE", "0", "VFD_Bon2_MB_Mode")
    ])
    main.add_network("VFD Bon 2 Modbus - Step 2 DATA_ADDR", [
        ("CMP_EQ", "VFD_Bon2_iStep", "2"),
        ("MOVE", "38501", "VFD_Bon2_MB_DataAddr")
    ])
    main.add_network("VFD Bon 2 Modbus - Step 2 DATA_LEN", [
        ("CMP_EQ", "VFD_Bon2_iStep", "2"),
        ("MOVE", "1", "VFD_Bon2_MB_DataLen")
    ])
    main.add_network("VFD Bon 2 Modbus - Step 3 MODE", [
        ("CMP_EQ", "VFD_Bon2_iStep", "3"),
        ("MOVE", "0", "VFD_Bon2_MB_Mode")
    ])
    main.add_network("VFD Bon 2 Modbus - Step 3 DATA_ADDR", [
        ("CMP_EQ", "VFD_Bon2_iStep", "3"),
        ("MOVE", "38502", "VFD_Bon2_MB_DataAddr")
    ])
    main.add_network("VFD Bon 2 Modbus - Step 3 DATA_LEN", [
        ("CMP_EQ", "VFD_Bon2_iStep", "3"),
        ("MOVE", "1", "VFD_Bon2_MB_DataLen")
    ])
    main.add_network("VFD Bon 2 Modbus - Set REQ khi co trigger", [
        ("NC", "VFD_Bon2_MB_Busy"),
        ("SetCoil", "VFD_Bon2_MB_Req")
    ])
    main.add_network("VFD Bon 2 Modbus - Reset REQ khi Busy", [
        ("NO", "VFD_Bon2_MB_Busy"),
        ("ResetCoil", "VFD_Bon2_MB_Req")
    ])
    main.add_network("VFD Bon 2 Modbus - Master Single Call", [
        ("NO", "VFD_Bon2_Comm_Active"),
        ("NO", "VFD_Bon2_Comm_Ready"),
        ("GENERIC", "MB_MASTER", {
            "REQ": "VFD_Bon2_MB_Req",
            "MB_ADDR": "1",
            "MODE": "VFD_Bon2_MB_Mode",
            "DATA_ADDR": "VFD_Bon2_MB_DataAddr",
            "DATA_LEN": "VFD_Bon2_MB_DataLen",
            "DATA_PTR": "VFD_Bon2_MB_DataBuffer"
        }, {
            "DONE": "VFD_Bon2_MB_Done",
            "BUSY": "VFD_Bon2_MB_Busy",
            "ERROR": "VFD_Bon2_MB_Error",
            "STATUS": "VFD_Bon2_MB_Status"
        }, {"Version": "2.2"}, "MB_MASTER_DB")
    ])
    main.add_network("VFD Bon 2 Modbus - Read Step 2 Buffer Copy", [
        ("CMP_EQ", "VFD_Bon2_iStep", "2"),
        ("NO", "VFD_Bon2_MB_Done"),
        ("MOVE", "VFD_Bon2_MB_DataBuffer", "VFD_Bon2_MB_StatusWord")
    ])
    main.add_network("VFD Bon 2 Modbus - Read Step 3 Buffer Copy", [
        ("CMP_EQ", "VFD_Bon2_iStep", "3"),
        ("NO", "VFD_Bon2_MB_Done"),
        ("MOVE", "VFD_Bon2_MB_DataBuffer", "VFD_Bon2_MB_FreqActual")
    ])
    main.add_network("VFD Bon 2 Modbus - Tang iStep khi Done", [
        ("NO", "VFD_Bon2_MB_Done"),
        ("MATH_ADD", "VFD_Bon2_iStep", "1", "VFD_Bon2_iStep")
    ])
    main.add_network("VFD Bon 2 Modbus - Reset iStep ve 0 khi vuot nguong", [
        ("CMP_GE", "VFD_Bon2_iStep", "4"),
        ("MOVE", "0", "VFD_Bon2_iStep")
    ])

    # 3. Giao tiếp Modbus TCP PLC1 - PLC2
    # Khởi tạo Connection Parameter
    main.add_network("Modbus TCP Client - Khoi tao Connection Param", [
        ("NO", "FirstScan"),
        ("MOVE", "64", "DB_MB_TCP_Client_Conn_DB.MB_TCP.InterfaceId"),
        ("MOVE", "5", "DB_MB_TCP_Client_Conn_DB.MB_TCP.ID"),
        ("MOVE", "11", "DB_MB_TCP_Client_Conn_DB.MB_TCP.ConnectionType"),
        ("MOVE", "TRUE", "DB_MB_TCP_Client_Conn_DB.MB_TCP.ActiveEstablished"),
        ("MOVE", "192", "DB_MB_TCP_Client_Conn_DB.MB_TCP.RemoteAddress.ADDR[1]"),
        ("MOVE", "168", "DB_MB_TCP_Client_Conn_DB.MB_TCP.RemoteAddress.ADDR[2]"),
        ("MOVE", "0", "DB_MB_TCP_Client_Conn_DB.MB_TCP.RemoteAddress.ADDR[3]"),
        ("MOVE", "2", "DB_MB_TCP_Client_Conn_DB.MB_TCP.RemoteAddress.ADDR[4]"),
        ("MOVE", "502", "DB_MB_TCP_Client_Conn_DB.MB_TCP.RemotePort"),
        ("MOVE", "0", "DB_MB_TCP_Client_Conn_DB.MB_TCP.LocalPort")
    ])

    # Reset any command edge
    main.add_network("Handshake Client - Reset Any Cmd Edge Flag", [
        ("ResetCoil", "MB_TCP_Any_Cmd_Edge")
    ])

    # Edge detection and old state updates
    main.add_network("Handshake Client - Start Edge", [
        ("NO", "Nut_Khoi_Dong_Eff"),
        ("NC", "Nut_Khoi_Dong_Eff_Old"),
        ("Coil", "Nut_Khoi_Dong_Eff_Edge")
    ])
    main.add_network("Handshake Client - Start Old Update", [
        ("NO", "Nut_Khoi_Dong_Eff"),
        ("Coil", "Nut_Khoi_Dong_Eff_Old")
    ])
    main.add_network("Handshake Client - Set Any Edge (Start)", [
        ("NO", "Nut_Khoi_Dong_Eff_Edge"),
        ("SetCoil", "MB_TCP_Any_Cmd_Edge")
    ])

    main.add_network("Handshake Client - Stop Edge", [
        ("NO", "Nut_Dung_Eff"),
        ("NC", "Nut_Dung_Eff_Old"),
        ("Coil", "Nut_Dung_Eff_Edge")
    ])
    main.add_network("Handshake Client - Stop Old Update", [
        ("NO", "Nut_Dung_Eff"),
        ("Coil", "Nut_Dung_Eff_Old")
    ])
    main.add_network("Handshake Client - Set Any Edge (Stop)", [
        ("NO", "Nut_Dung_Eff_Edge"),
        ("SetCoil", "MB_TCP_Any_Cmd_Edge")
    ])

    main.add_network("Handshake Client - Reset Edge", [
        ("NO", "Nut_Reset_Eff"),
        ("NC", "Nut_Reset_Eff_Old"),
        ("Coil", "Nut_Reset_Eff_Edge")
    ])
    main.add_network("Handshake Client - Reset Old Update", [
        ("NO", "Nut_Reset_Eff"),
        ("Coil", "Nut_Reset_Eff_Old")
    ])
    main.add_network("Handshake Client - Set Any Edge (Reset)", [
        ("NO", "Nut_Reset_Eff_Edge"),
        ("SetCoil", "MB_TCP_Any_Cmd_Edge")
    ])

    main.add_network("Handshake Client - EStop Edge", [
        ("NO", "Nut_EStop_Eff"),
        ("NC", "Nut_EStop_Eff_Old"),
        ("Coil", "Nut_EStop_Eff_Edge")
    ])
    main.add_network("Handshake Client - EStop Old Update", [
        ("NO", "Nut_EStop_Eff"),
        ("Coil", "Nut_EStop_Eff_Old")
    ])
    main.add_network("Handshake Client - Set Any Edge (EStop)", [
        ("NO", "Nut_EStop_Eff_Edge"),
        ("SetCoil", "MB_TCP_Any_Cmd_Edge")
    ])

    main.add_network("Handshake Client - Transfer Edge", [
        ("NO", "Pump3265_Chuyen_Nhanh2_Cmd"),
        ("NC", "Pump3265_Chuyen_Nhanh2_Cmd_Old"),
        ("Coil", "Pump3265_Chuyen_Nhanh2_Cmd_Edge")
    ])
    main.add_network("Handshake Client - Transfer Old Update", [
        ("NO", "Pump3265_Chuyen_Nhanh2_Cmd"),
        ("Coil", "Pump3265_Chuyen_Nhanh2_Cmd_Old")
    ])
    main.add_network("Handshake Client - Set Any Edge (Transfer)", [
        ("NO", "Pump3265_Chuyen_Nhanh2_Cmd_Edge"),
        ("SetCoil", "MB_TCP_Any_Cmd_Edge")
    ])

    main.add_network("Handshake Client - Load Recipe Edge", [
        ("NO", "PLC1_Load_Default_Cmd"),
        ("NC", "PLC1_Load_Default_Cmd_Old"),
        ("Coil", "PLC1_Load_Default_Cmd_Edge")
    ])
    main.add_network("Handshake Client - Load Recipe Old Update", [
        ("NO", "PLC1_Load_Default_Cmd"),
        ("Coil", "PLC1_Load_Default_Cmd_Old")
    ])
    main.add_network("Handshake Client - Set Any Edge (Load Recipe)", [
        ("NO", "PLC1_Load_Default_Cmd_Edge"),
        ("SetCoil", "MB_TCP_Any_Cmd_Edge")
    ])

    # Latch command bits when edge detected
    main.add_network("Handshake Client - Latch Start", [
        ("NO", "Nut_Khoi_Dong_Eff_Edge"),
        ("SetCoil", "DB_PLC1_Send_To_PLC2_DB.Cmd_Start")
    ])
    main.add_network("Handshake Client - Latch Stop", [
        ("NO", "Nut_Dung_Eff_Edge"),
        ("SetCoil", "DB_PLC1_Send_To_PLC2_DB.Cmd_Stop")
    ])
    main.add_network("Handshake Client - Latch Reset", [
        ("NO", "Nut_Reset_Eff_Edge"),
        ("SetCoil", "DB_PLC1_Send_To_PLC2_DB.Cmd_Reset")
    ])
    main.add_network("Handshake Client - Latch EStop", [
        ("NO", "Nut_EStop_Eff_Edge"),
        ("SetCoil", "DB_PLC1_Send_To_PLC2_DB.Cmd_EStop")
    ])
    main.add_network("Handshake Client - Latch Transfer", [
        ("NO", "Pump3265_Chuyen_Nhanh2_Cmd_Edge"),
        ("SetCoil", "DB_PLC1_Send_To_PLC2_DB.Cmd_Pump_Branch2_To_SubTanks")
    ])
    main.add_network("Handshake Client - Latch Load Recipe", [
        ("NO", "PLC1_Load_Default_Cmd_Edge"),
        ("SetCoil", "DB_PLC1_Send_To_PLC2_DB.Cmd_Load_Recipe")
    ])

    # Increment CmdSeq on any edge
    main.add_network("Handshake Client - Increment CmdSeq", [
        ("NO", "MB_TCP_Any_Cmd_Edge"),
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

    # === PACK dữ liệu vào Word Buffer trước khi gửi đi (Step 0) ===
    # Register map Write (Data[0..2] → Modbus addr 40001..40003 trên PLC2):
    # Data[0] = CmdSeq (Int cast to Word)
    # Data[1] = Cmd flags word (bit0=Start, bit1=Stop, bit2=Reset, bit3=EStop, bit4=Transfer, bit5=LoadRecipe)
    # Data[2] = Heartbeat_Client
    main.add_network("Modbus TCP Client - Pack CmdSeq vào Data[0]", [
        ("MOVE", "DB_PLC1_Send_To_PLC2_DB.CmdSeq", "DB_PLC1_MB_Word_Buffer_DB.Data[0]")
    ])
    main.add_network("Modbus TCP Client - Pack Cmd flags vào Data[1]", [
        ("MOVE", "0", "AI_Temp_Pack_Word"),
        ("MOVE", "DB_PLC1_Send_To_PLC2_DB.Cmd_Start", "AI_Temp_Pack_Word.%X0"),
        ("MOVE", "DB_PLC1_Send_To_PLC2_DB.Cmd_Stop", "AI_Temp_Pack_Word.%X1"),
        ("MOVE", "DB_PLC1_Send_To_PLC2_DB.Cmd_Reset", "AI_Temp_Pack_Word.%X2"),
        ("MOVE", "DB_PLC1_Send_To_PLC2_DB.Cmd_EStop", "AI_Temp_Pack_Word.%X3"),
        ("MOVE", "DB_PLC1_Send_To_PLC2_DB.Cmd_Pump_Branch2_To_SubTanks", "AI_Temp_Pack_Word.%X4"),
        ("MOVE", "DB_PLC1_Send_To_PLC2_DB.Cmd_Load_Recipe", "AI_Temp_Pack_Word.%X5"),
        ("MOVE", "AI_Temp_Pack_Word", "DB_PLC1_MB_Word_Buffer_DB.Data[1]")
    ])
    main.add_network("Modbus TCP Client - Pack Heartbeat vào Data[2]", [
        ("MOVE", "DB_PLC1_Send_To_PLC2_DB.Heartbeat", "DB_PLC1_MB_Word_Buffer_DB.Data[2]")
    ])

    # Sequencer step logic
    main.add_network("Modbus TCP Client - Request Write (Step 0)", [
        ("CMP_EQ", "MB_TCP_iStep", "0"),
        ("Coil", "MB_TCP_REQ")
    ])
    main.add_network("Modbus TCP Client - Request Read (Step 1)", [
        ("CMP_EQ", "MB_TCP_iStep", "1"),
        ("Coil", "MB_TCP_REQ")
    ])

    # Call MB_CLIENT Write — MB_DATA_PTR trỏ vào Array of Word DB (fix lỗi 80B6)
    main.add_network("Modbus TCP Client - Call MB_CLIENT Write (Step 0)", [
        ("GENERIC", "MB_CLIENT", {
            "REQ": "MB_TCP_REQ",
            "DISCONNECT": "FALSE",
            "MB_MODE": "1",
            "MB_DATA_ADDR": "40001",
            "MB_DATA_LEN": "3",
            "MB_DATA_PTR": "DB_PLC1_MB_Word_Buffer_DB.Data",
            "CONNECT_ID": "5",
            "IP_OCTET_1": "192",
            "IP_OCTET_2": "168",
            "IP_OCTET_3": "0",
            "IP_OCTET_4": "2",
            "IP_PORT": "502"
        }, {
            "DONE": "MB_TCP_DONE",
            "BUSY": "OPEN",
            "ERROR": "MB_TCP_ERROR",
            "STATUS": "MB_TCP_STATUS"
        }, {"Version": "3.1", "card1200": "1", "card1500": "0"}, "MB_CLIENT_Write_DB")
    ])

    # Call MB_CLIENT Read — MB_DATA_PTR trỏ vào Array of Word DB (fix lỗi 80B6)
    # Register map Read (Data[3..9] ← Modbus addr 40004..40010 từ PLC2):
    # Data[3] = AckSeq, Data[4] = Status flags, Data[5] = State
    # Data[6] = SP×10 (Int), Data[7] = PV×10 (Int), Data[8] = CV×10 (Int)
    # Data[9] = Heartbeat_Server
    main.add_network("Modbus TCP Client - Call MB_CLIENT Read (Step 1)", [
        ("GENERIC", "MB_CLIENT", {
            "REQ": "MB_TCP_REQ",
            "DISCONNECT": "FALSE",
            "MB_MODE": "0",
            "MB_DATA_ADDR": "40004",
            "MB_DATA_LEN": "7",
            "MB_DATA_PTR": "DB_PLC1_MB_Word_Buffer_DB.Data[3]",
            "CONNECT_ID": "5",
            "IP_OCTET_1": "192",
            "IP_OCTET_2": "168",
            "IP_OCTET_3": "0",
            "IP_OCTET_4": "2",
            "IP_PORT": "502"
        }, {
            "DONE": "MB_TCP_DONE",
            "BUSY": "OPEN",
            "ERROR": "MB_TCP_ERROR",
            "STATUS": "MB_TCP_STATUS"
        }, {"Version": "3.1", "card1200": "1", "card1500": "0"}, "MB_CLIENT_Read_DB")
    ])

    # Step transitions
    main.add_network("Modbus TCP Client - Transition Step 0 to 1 (Done)", [
        ("CMP_EQ", "MB_TCP_iStep", "0"),
        ("NO", "MB_TCP_DONE"),
        ("MOVE", "1", "MB_TCP_iStep")
    ])
    main.add_network("Modbus TCP Client - Transition Step 0 to 1 (Error)", [
        ("CMP_EQ", "MB_TCP_iStep", "0"),
        ("NO", "MB_TCP_ERROR"),
        ("MOVE", "1", "MB_TCP_iStep")
    ])
    main.add_network("Modbus TCP Client - Transition Step 1 to 0 (Done)", [
        ("CMP_EQ", "MB_TCP_iStep", "1"),
        ("NO", "MB_TCP_DONE"),
        ("MOVE", "0", "MB_TCP_iStep")
    ])
    main.add_network("Modbus TCP Client - Transition Step 1 to 0 (Error)", [
        ("CMP_EQ", "MB_TCP_iStep", "1"),
        ("NO", "MB_TCP_ERROR"),
        ("MOVE", "0", "MB_TCP_iStep")
    ])
    main.add_network("Modbus TCP Client - iStep Safety Reset", [
        ("CMP_GE", "MB_TCP_iStep", "2"),
        ("MOVE", "0", "MB_TCP_iStep")
    ])

    # Heartbeat
    main.add_network("Modbus TCP Client - Increment Heartbeat", [
        ("NO", "Clock_1Hz"),
        ("MATH_ADD", "DB_PLC1_Send_To_PLC2_DB.Heartbeat", "1", "DB_PLC1_Send_To_PLC2_DB.Heartbeat")
    ])

    # === UNPACK dữ liệu nhận từ PLC2 sau khi Read Done (Data[3..9]) ===
    main.add_network("Modbus TCP Client - Unpack AckSeq từ Data[3]", [
        ("NO", "MB_TCP_DONE"),
        ("MOVE", "DB_PLC1_MB_Word_Buffer_DB.Data[3]", "DB_PLC1_Recv_From_PLC2_DB.AckSeq")
    ])
    main.add_network("Modbus TCP Client - Unpack Status flags từ Data[4]", [
        ("NO", "MB_TCP_DONE"),
        ("MOVE", "DB_PLC1_MB_Word_Buffer_DB.Data[4]", "AI_Temp_Unpack_Word"),
        ("MOVE", "AI_Temp_Unpack_Word.%X0", "DB_PLC1_Recv_From_PLC2_DB.Done_Branch2"),
        ("MOVE", "AI_Temp_Unpack_Word.%X1", "DB_PLC1_Recv_From_PLC2_DB.Done_Recipe"),
        ("MOVE", "AI_Temp_Unpack_Word.%X2", "DB_PLC1_Recv_From_PLC2_DB.Alarm"),
        ("MOVE", "AI_Temp_Unpack_Word.%X3", "DB_PLC1_Recv_From_PLC2_DB.Done_Discharge2")
    ])
    main.add_network("Modbus TCP Client - Unpack State từ Data[5]", [
        ("NO", "MB_TCP_DONE"),
        ("MOVE", "DB_PLC1_MB_Word_Buffer_DB.Data[5]", "DB_PLC1_Recv_From_PLC2_DB.State")
    ])
    # SP/PV/CV được truyền dưới dạng Int x10 để tránh phức tạp Real→2Word conversion
    main.add_network("Modbus TCP Client - Unpack SP_x10 từ Data[6] sang Real", [
        ("NO", "MB_TCP_DONE"),
        ("MOVE", "DB_PLC1_MB_Word_Buffer_DB.Data[6]", "PID_Bon4_SP_Recv_Int"),
        ("CONV_Convert", "PID_Bon4_SP_Recv_Int", "PID_Bon4_SP_Recv", "Int", "Real"),
        ("MATH_MUL_Real", "PID_Bon4_SP_Recv", "0.1", "PID_Bon4_SP_Recv")
    ])
    main.add_network("Modbus TCP Client - Unpack PV_x10 từ Data[7] sang Real", [
        ("NO", "MB_TCP_DONE"),
        ("MOVE", "DB_PLC1_MB_Word_Buffer_DB.Data[7]", "PID_Bon4_PV_Recv_Int"),
        ("CONV_Convert", "PID_Bon4_PV_Recv_Int", "PID_Bon4_PV_Recv", "Int", "Real"),
        ("MATH_MUL_Real", "PID_Bon4_PV_Recv", "0.1", "PID_Bon4_PV_Recv")
    ])
    main.add_network("Modbus TCP Client - Unpack CV_x10 từ Data[8] sang Real", [
        ("NO", "MB_TCP_DONE"),
        ("MOVE", "DB_PLC1_MB_Word_Buffer_DB.Data[8]", "PID_Bon4_CV_Recv_Int"),
        ("CONV_Convert", "PID_Bon4_CV_Recv_Int", "PID_Bon4_CV_Recv", "Int", "Real"),
        ("MATH_MUL_Real", "PID_Bon4_CV_Recv", "0.1", "PID_Bon4_CV_Recv")
    ])
    main.add_network("Modbus TCP Client - Unpack Heartbeat_Server từ Data[9]", [
        ("NO", "MB_TCP_DONE"),
        ("MOVE", "DB_PLC1_MB_Word_Buffer_DB.Data[9]", "DB_PLC1_Recv_From_PLC2_DB.Heartbeat")
    ])

    # Map Received Status to Local tags
    main.add_network("Modbus TCP Client - Map Received PLC2 Status sang tags cục bộ", [
        ("MOVE", "DB_PLC1_Recv_From_PLC2_DB.Done_Branch2", "PLC2_Me_Nhanh2_Hoan_Thanh_Nhan"),
        ("MOVE", "DB_PLC1_Recv_From_PLC2_DB.Done_Recipe", "PLC1_Load_Default_Done_Nhan"),
        ("MOVE", "DB_PLC1_Recv_From_PLC2_DB.Alarm", "PLC2_Loi_Tong_Recv"),
        ("MOVE", "DB_PLC1_Recv_From_PLC2_DB.State", "PLC2_State_Recv"),
        ("MOVE", "PID_Bon4_SP_Recv", "PID_Bon4_SP_Recv"),
        ("MOVE", "PID_Bon4_PV_Recv", "PID_Bon4_PV_Recv"),
        ("MOVE", "PID_Bon4_CV_Recv", "PID_Bon4_CV_Recv")
    ])
    
    return main.generate_xml()


def build_main_for_plc2() -> str:
    main = TIALadderBuilder(fb_name="Main", block_id="1", block_type="OB")
    
    # 1. Modbus TCP Connection parameters initialization for PLC2 (Server)
    main.add_network("Modbus TCP Server - Khoi tao Connection Param", [
        ("NO", "FirstScan"),
        ("MOVE", "64", "DB_MB_TCP_Server_Conn_DB.MB_TCP_SERVER.InterfaceId"),
        ("MOVE", "5", "DB_MB_TCP_Server_Conn_DB.MB_TCP_SERVER.ID"),
        ("MOVE", "11", "DB_MB_TCP_Server_Conn_DB.MB_TCP_SERVER.ConnectionType"),
        ("MOVE", "FALSE", "DB_MB_TCP_Server_Conn_DB.MB_TCP_SERVER.ActiveEstablished"),
        ("MOVE", "192", "DB_MB_TCP_Server_Conn_DB.MB_TCP_SERVER.RemoteAddress.ADDR[1]"),
        ("MOVE", "168", "DB_MB_TCP_Server_Conn_DB.MB_TCP_SERVER.RemoteAddress.ADDR[2]"),
        ("MOVE", "0", "DB_MB_TCP_Server_Conn_DB.MB_TCP_SERVER.RemoteAddress.ADDR[3]"),
        ("MOVE", "1", "DB_MB_TCP_Server_Conn_DB.MB_TCP_SERVER.RemoteAddress.ADDR[4]"),
        ("MOVE", "0", "DB_MB_TCP_Server_Conn_DB.MB_TCP_SERVER.RemotePort"),
        ("MOVE", "502", "DB_MB_TCP_Server_Conn_DB.MB_TCP_SERVER.LocalPort")
    ])
    
    # 2. Call MB_SERVER block — MB_HOLD_REG trỏ vào Array of Word DB (fix lỗi 80B6)
    # Register map Holding Register (0-indexed, Modbus addr 40001+ = Data[0]+):
    # Data[0]=CmdSeq, Data[1]=CmdFlags, Data[2]=Heartbeat_Client (PLC1→PLC2 write zone)
    # Data[3]=AckSeq, Data[4]=StatusFlags, Data[5]=State,
    # Data[6]=SP×10, Data[7]=PV×10, Data[8]=CV×10, Data[9]=Heartbeat_Server (PLC2 status zone)
    main.add_network("Modbus TCP Server - Call MB_SERVER", [
        ("GENERIC", "MB_SERVER", {
            "DISCONNECT": "FALSE",
            "CONNECT_ID": "5",
            "IP_PORT": "502",
            "MB_HOLD_REG": "DB_PLC2_MB_Holding_Word_DB.Data"
        }, {
            "NDR": "MB_TCP_Server_NDR",
            "DR": "MB_TCP_Server_DR",
            "ERROR": "MB_TCP_Server_Error",
            "STATUS": "MB_TCP_Server_Status"
        }, {"Version": "3.1", "card1200": "1", "card1500": "0"}, "MB_SERVER_DB")
    ])

    # === UNPACK command từ PLC1 (Data[0..2]) ngay sau MB_SERVER ===
    main.add_network("Modbus TCP Server - Unpack CmdSeq từ Data[0]", [
        ("MOVE", "DB_PLC2_MB_Holding_Word_DB.Data[0]", "DB_Modbus_Holding_Register_DB.CmdSeq")
    ])
    main.add_network("Modbus TCP Server - Unpack Cmd flags từ Data[1]", [
        ("MOVE", "DB_PLC2_MB_Holding_Word_DB.Data[1]", "AI_Temp_Unpack_Word"),
        ("MOVE", "AI_Temp_Unpack_Word.%X0", "DB_Modbus_Holding_Register_DB.Cmd_Start"),
        ("MOVE", "AI_Temp_Unpack_Word.%X1", "DB_Modbus_Holding_Register_DB.Cmd_Stop"),
        ("MOVE", "AI_Temp_Unpack_Word.%X2", "DB_Modbus_Holding_Register_DB.Cmd_Reset"),
        ("MOVE", "AI_Temp_Unpack_Word.%X3", "DB_Modbus_Holding_Register_DB.Cmd_EStop"),
        ("MOVE", "AI_Temp_Unpack_Word.%X4", "DB_Modbus_Holding_Register_DB.Cmd_Pump_Branch2_To_SubTanks"),
        ("MOVE", "AI_Temp_Unpack_Word.%X5", "DB_Modbus_Holding_Register_DB.Cmd_Load_Recipe")
    ])
    main.add_network("Modbus TCP Server - Unpack Heartbeat_Client từ Data[2]", [
        ("MOVE", "DB_PLC2_MB_Holding_Word_DB.Data[2]", "DB_Modbus_Holding_Register_DB.Heartbeat_Client")
    ])
    
    # 3. Detect CmdSeq change
    main.add_network("Handshake Server - Detect new CmdSeq", [
        ("CMP_NE", "DB_Modbus_Holding_Register_DB.CmdSeq", "PLC2_Last_CmdSeq"),
        ("Coil", "PLC2_CmdSeq_New")
    ])
    
    # 4. Map DB commands to local receive tags (pulse 1 scan)
    main.add_network("Handshake Server - Start command pulse", [
        ("NO", "PLC2_CmdSeq_New"),
        ("NO", "DB_Modbus_Holding_Register_DB.Cmd_Start"),
        ("Coil", "Nut_Khoi_Dong_Nhan")
    ])
    main.add_network("Handshake Server - Stop command pulse", [
        ("NO", "PLC2_CmdSeq_New"),
        ("NO", "DB_Modbus_Holding_Register_DB.Cmd_Stop"),
        ("Coil", "Nut_Dung_Nhan")
    ])
    main.add_network("Handshake Server - Reset command pulse", [
        ("NO", "PLC2_CmdSeq_New"),
        ("NO", "DB_Modbus_Holding_Register_DB.Cmd_Reset"),
        ("Coil", "Nut_Reset_Nhan")
    ])
    main.add_network("Handshake Server - EStop command pulse", [
        ("NO", "PLC2_CmdSeq_New"),
        ("NO", "DB_Modbus_Holding_Register_DB.Cmd_EStop"),
        ("Coil", "Nut_EStop_Nhan")
    ])
    main.add_network("Handshake Server - Transfer command pulse", [
        ("NO", "PLC2_CmdSeq_New"),
        ("NO", "DB_Modbus_Holding_Register_DB.Cmd_Pump_Branch2_To_SubTanks"),
        ("Coil", "Pump3265_Chuyen_Nhanh2_Cmd_Nhan")
    ])
    main.add_network("Handshake Server - Load Recipe command pulse", [
        ("NO", "PLC2_CmdSeq_New"),
        ("NO", "DB_Modbus_Holding_Register_DB.Cmd_Load_Recipe"),
        ("Coil", "PLC2_Load_Default_Cmd_Nhan")
    ])
    
    # 5. Gọi logic điều khiển cơ sở của PLC2
    main.add_network("PLC2 - Gọi logic khởi tạo recipe mặc định PLC2", [("CALL_FC", "FC_Init_Default_Recipe_PLC2")])
    main.add_network("PLC2 - gọi logic Bồn 3 và Bồn 4", [("CALL_FC", "FC_PLC2_Mixing")])
    main.add_network("PLC2 - cập nhật mirror HMI", [("CALL_FC", "FC_HMI_Mirror_PLC2")])
    
    # 6. Map dữ liệu từ PLC2 sang symbolic DB (legacy) và đồng thời PACK vào Word buffer DB
    main.add_network("Modbus TCP Server - Map Analog Status", [
        ("MOVE", "PLC2_Me_Nhanh2_Hoan_Thanh", "DB_Modbus_Holding_Register_DB.Done_Branch2"),
        ("MOVE", "PLC2_Load_Default_Done", "DB_Modbus_Holding_Register_DB.Done_Recipe"),
        ("MOVE", "PLC2_Loi_Tong", "DB_Modbus_Holding_Register_DB.Alarm"),
        ("MOVE", "PLC2_State", "DB_Modbus_Holding_Register_DB.State"),
        ("MOVE", "PID_Bon4_SP", "DB_Modbus_Holding_Register_DB.PID_Bon4_SP"),
        ("MOVE", "TT3219_Bon4_Sim", "DB_Modbus_Holding_Register_DB.PID_Bon4_PV"),
        ("MOVE", "CV3216_Hoi_Bon4", "DB_Modbus_Holding_Register_DB.PID_Bon4_CV")
    ])

    # === PACK dữ liệu trạng thái PLC2 vào Word buffer DB (Data[3..9]) để MB_SERVER gửi đi ===
    main.add_network("Modbus TCP Server - Pack AckSeq vào Data[3]", [
        ("MOVE", "DB_Modbus_Holding_Register_DB.AckSeq", "DB_PLC2_MB_Holding_Word_DB.Data[3]")
    ])
    main.add_network("Modbus TCP Server - Pack Status flags vào Data[4]", [
        ("MOVE", "0", "AI_Temp_Pack_Word"),
        ("MOVE", "DB_Modbus_Holding_Register_DB.Done_Branch2", "AI_Temp_Pack_Word.%X0"),
        ("MOVE", "DB_Modbus_Holding_Register_DB.Done_Recipe", "AI_Temp_Pack_Word.%X1"),
        ("MOVE", "DB_Modbus_Holding_Register_DB.Alarm", "AI_Temp_Pack_Word.%X2"),
        ("MOVE", "DB_Modbus_Holding_Register_DB.Done_Discharge2", "AI_Temp_Pack_Word.%X3"),
        ("MOVE", "AI_Temp_Pack_Word", "DB_PLC2_MB_Holding_Word_DB.Data[4]")
    ])
    main.add_network("Modbus TCP Server - Pack State vào Data[5]", [
        ("MOVE", "DB_Modbus_Holding_Register_DB.State", "DB_PLC2_MB_Holding_Word_DB.Data[5]")
    ])
    # SP/PV/CV truyền dưới dạng Int x10: Real × 10.0 → Round → Int → Word
    main.add_network("Modbus TCP Server - Pack SP×10 vào Data[6]", [
        ("MATH_MUL_Real", "PID_Bon4_SP", "10.0", "PID_Bon4_SP_x10_Real"),
        ("CONV_Round", "PID_Bon4_SP_x10_Real", "PID_Bon4_SP_x10_Int", "Real", "Int"),
        ("MOVE", "PID_Bon4_SP_x10_Int", "DB_PLC2_MB_Holding_Word_DB.Data[6]")
    ])
    main.add_network("Modbus TCP Server - Pack PV×10 vào Data[7]", [
        ("MATH_MUL_Real", "TT3219_Bon4_Eff", "10.0", "PID_Bon4_PV_x10_Real"),
        ("CONV_Round", "PID_Bon4_PV_x10_Real", "PID_Bon4_PV_x10_Int", "Real", "Int"),
        ("MOVE", "PID_Bon4_PV_x10_Int", "DB_PLC2_MB_Holding_Word_DB.Data[7]")
    ])
    main.add_network("Modbus TCP Server - Pack CV×10 vào Data[8]", [
        ("MATH_MUL_Real", "CV3216_Hoi_Bon4", "10.0", "PID_Bon4_CV_x10_Real"),
        ("CONV_Round", "PID_Bon4_CV_x10_Real", "PID_Bon4_CV_x10_Int", "Real", "Int"),
        ("MOVE", "PID_Bon4_CV_x10_Int", "DB_PLC2_MB_Holding_Word_DB.Data[8]")
    ])

    # Heartbeat PLC2
    main.add_network("Modbus TCP Server - Increment Heartbeat", [
        ("NO", "Clock_1Hz"),
        ("MATH_ADD", "DB_Modbus_Holding_Register_DB.Heartbeat_Server", "1", "DB_Modbus_Holding_Register_DB.Heartbeat_Server")
    ])
    main.add_network("Modbus TCP Server - Pack Heartbeat_Server vào Data[9]", [
        ("MOVE", "DB_Modbus_Holding_Register_DB.Heartbeat_Server", "DB_PLC2_MB_Holding_Word_DB.Data[9]")
    ])

    # 7. Update AckSeq and Last_CmdSeq at the end of scan
    main.add_network("Handshake Server - Update AckSeq and Last_CmdSeq", [
        ("MOVE", "DB_Modbus_Holding_Register_DB.CmdSeq", "DB_Modbus_Holding_Register_DB.AckSeq"),
        ("MOVE", "DB_Modbus_Holding_Register_DB.CmdSeq", "PLC2_Last_CmdSeq")
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
        "FC_HMI_Animation_PLC1.xml",
        "FC_Manual_Control_PLC1.xml",
        "FC_VFD_Bon2_Hybrid.xml",
        "OB30_PID_PLC1_Bon2.xml",
        "Hmi.TextList.TL_Mixing_Step.xml",
        "Hmi.TextList.TL_Canh_Bao_Mixing.xml",
        "Hmi.TextList.TL_Phan_Quyen.xml",
        "Timers_PLC1.xml",
        "DB_PLC1_Send_To_PLC2_DB.xml",
        "DB_PLC1_Recv_From_PLC2_DB.xml",
        "DB_PLC1_MB_Buffer_DB.xml",
        "DB_MB_TCP_Client_Conn_DB.xml",   # TCON_IP_v4 connection DB (fix 80B6)
        "DB_PLC1_MB_Word_Buffer_DB.xml",  # Array of Word buffer cho MB_CLIENT (fix 80B6)
    ])
    shutil.copy2(OUTPUT_DIR / "PLC_Tags_PLC1.xml", plc1 / "PLC_Tags.xml")
    write_text(plc1 / "Main.xml", build_main_for_plc1())

    # Generate custom MB_CLIENT instance DBs
    template_path = PROJECT_DIR / "post_import_export" / "PLC_1" / "Blocks" / "MB_CLIENT_DB.xml"
    if template_path.exists():
        template_content = template_path.read_text(encoding="utf-8")
        write_db_content = template_content.replace("<Name>MB_CLIENT_DB</Name>", "<Name>MB_CLIENT_Write_DB</Name>").replace("<Number>52</Number>", "<Number>54</Number>")
        read_db_content = template_content.replace("<Name>MB_CLIENT_DB</Name>", "<Name>MB_CLIENT_Read_DB</Name>").replace("<Number>52</Number>", "<Number>55</Number>")
        (plc1 / "MB_CLIENT_Write_DB.xml").write_text(write_db_content, encoding="utf-8")
        (plc1 / "MB_CLIENT_Read_DB.xml").write_text(read_db_content, encoding="utf-8")
        print("Generated MB_CLIENT_Write_DB.xml and MB_CLIENT_Read_DB.xml from template.")
    else:
        print(f"WARNING: Template not found at {template_path}, cannot generate MB_CLIENT DBs.")

    copy_from_output(plc2, [
        "FC_Init_Default_Recipe_PLC2.xml",
        "FC_PLC2_Mixing.xml",
        "FC_HMI_Mirror_PLC2.xml",
        "FC_HMI_Animation_PLC2.xml",
        "FC_Manual_Control_PLC2.xml",
        "OB31_PID_PLC2_Bon4.xml",
        "Timers_PLC2.xml",
        "DB_MB_TCP_Server_Conn_DB.xml",    # TCON_IP_v4 connection DB (fix 80B6)
        "DB_Modbus_Holding_Register_DB.xml",
        "DB_PLC2_MB_Holding_Word_DB.xml",  # Array of Word buffer cho MB_SERVER (fix 80B6)
    ])
    shutil.copy2(OUTPUT_DIR / "PLC_Tags_PLC2.xml", plc2 / "PLC_Tags.xml")
    write_text(plc2 / "Main.xml", build_main_for_plc2())

    print(f"Prepared TIA import sets under {IMPORT_DIR}")


if __name__ == "__main__":
    main()
