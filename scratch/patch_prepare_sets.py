# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

FILE_PATH = "projects/Mixing_Nuoc_Tuong_Maggi_2026/prepare_tia_import_sets.py"

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Normalize newlines
content = content.replace('\r\n', '\n')

# --- PATCH 1: Client parameter loading, block calling, and mapping logic ---
target_client = """    # Step 0 Params
    main.add_network("Modbus TCP Client - Step 0 Mode", [
        ("CMP_EQ", "MB_TCP_iStep", "0"),
        ("MOVE", "1", "MB_TCP_Mode")
    ])
    main.add_network("Modbus TCP Client - Step 0 DataAddr", [
        ("CMP_EQ", "MB_TCP_iStep", "0"),
        ("MOVE", "40001", "MB_TCP_DataAddr")
    ])
    main.add_network("Modbus TCP Client - Step 0 DataLen", [
        ("CMP_EQ", "MB_TCP_iStep", "0"),
        ("MOVE", "3", "MB_TCP_DataLen")
    ])

    # Step 1 Params
    main.add_network("Modbus TCP Client - Step 1 Mode", [
        ("CMP_EQ", "MB_TCP_iStep", "1"),
        ("MOVE", "0", "MB_TCP_Mode")
    ])
    main.add_network("Modbus TCP Client - Step 1 DataAddr", [
        ("CMP_EQ", "MB_TCP_iStep", "1"),
        ("MOVE", "40001", "MB_TCP_DataAddr")
    ])
    main.add_network("Modbus TCP Client - Step 1 DataLen", [
        ("CMP_EQ", "MB_TCP_iStep", "1"),
        ("MOVE", "14", "MB_TCP_DataLen")
    ])

    # Trigger request when MB_CLIENT is not busy
    main.add_network("Modbus TCP Client - Trigger Request", [
        ("NC", "MB_TCP_BUSY"),
        ("Coil", "MB_TCP_REQ")
    ])

    # Call MB_CLIENT
    main.add_network("Modbus TCP Client - Call MB_CLIENT", [
        ("GENERIC", "MB_CLIENT", {
            "REQ": "MB_TCP_REQ",
            "DISCONNECT": "FALSE",
            "MB_MODE": "MB_TCP_Mode",
            "MB_DATA_ADDR": "MB_TCP_DataAddr",
            "MB_DATA_LEN": "MB_TCP_DataLen",
            "MB_DATA_PTR": "DB_PLC1_MB_Buffer_DB",
            "CONNECT_ID": "1",
            "IP_OCTET_1": "192",
            "IP_OCTET_2": "168",
            "IP_OCTET_3": "0",
            "IP_OCTET_4": "2",
            "IP_PORT": "502"
        }, {
            "DONE": "MB_TCP_DONE",
            "BUSY": "MB_TCP_BUSY",
            "ERROR": "MB_TCP_ERROR",
            "STATUS": "MB_TCP_STATUS"
        }, {"Version": "3.1", "card1200": "1", "card1500": "0"}, "MB_CLIENT_DB")
    ])

    # Copy Recv From Buffer DB when Done in Step 1
    main.add_network("Modbus TCP Client - Copy Recv AckSeq", [
        ("CMP_EQ", "MB_TCP_iStep", "1"),
        ("NO", "MB_TCP_DONE"),
        ("MOVE", "DB_PLC1_MB_Buffer_DB.Recv_AckSeq", "DB_PLC1_Recv_From_PLC2_DB.AckSeq")
    ])
    main.add_network("Modbus TCP Client - Copy Recv Done_Branch2", [
        ("CMP_EQ", "MB_TCP_iStep", "1"),
        ("NO", "MB_TCP_DONE"),
        ("NO", "DB_PLC1_MB_Buffer_DB.Recv_Done_Branch2"),
        ("Coil", "DB_PLC1_Recv_From_PLC2_DB.Done_Branch2")
    ])
    main.add_network("Modbus TCP Client - Copy Recv Done_Recipe", [
        ("CMP_EQ", "MB_TCP_iStep", "1"),
        ("NO", "MB_TCP_DONE"),
        ("NO", "DB_PLC1_MB_Buffer_DB.Recv_Done_Recipe"),
        ("Coil", "DB_PLC1_Recv_From_PLC2_DB.Done_Recipe")
    ])
    main.add_network("Modbus TCP Client - Copy Recv Alarm", [
        ("CMP_EQ", "MB_TCP_iStep", "1"),
        ("NO", "MB_TCP_DONE"),
        ("NO", "DB_PLC1_MB_Buffer_DB.Recv_Alarm"),
        ("Coil", "DB_PLC1_Recv_From_PLC2_DB.Alarm")
    ])
    main.add_network("Modbus TCP Client - Copy Recv State", [
        ("CMP_EQ", "MB_TCP_iStep", "1"),
        ("NO", "MB_TCP_DONE"),
        ("MOVE", "DB_PLC1_MB_Buffer_DB.Recv_State", "DB_PLC1_Recv_From_PLC2_DB.State")
    ])
    main.add_network("Modbus TCP Client - Copy Recv PID_Bon4_SP", [
        ("CMP_EQ", "MB_TCP_iStep", "1"),
        ("NO", "MB_TCP_DONE"),
        ("MOVE", "DB_PLC1_MB_Buffer_DB.Recv_PID_Bon4_SP", "DB_PLC1_Recv_From_PLC2_DB.PID_Bon4_SP")
    ])
    main.add_network("Modbus TCP Client - Copy Recv PID_Bon4_PV", [
        ("CMP_EQ", "MB_TCP_iStep", "1"),
        ("NO", "MB_TCP_DONE"),
        ("MOVE", "DB_PLC1_MB_Buffer_DB.Recv_PID_Bon4_PV", "DB_PLC1_Recv_From_PLC2_DB.PID_Bon4_PV")
    ])
    main.add_network("Modbus TCP Client - Copy Recv PID_Bon4_CV", [
        ("CMP_EQ", "MB_TCP_iStep", "1"),
        ("NO", "MB_TCP_DONE"),
        ("MOVE", "DB_PLC1_MB_Buffer_DB.Recv_PID_Bon4_CV", "DB_PLC1_Recv_From_PLC2_DB.PID_Bon4_CV")
    ])
    main.add_network("Modbus TCP Client - Copy Recv Done_Discharge2", [
        ("CMP_EQ", "MB_TCP_iStep", "1"),
        ("NO", "MB_TCP_DONE"),
        ("NO", "DB_PLC1_MB_Buffer_DB.Recv_Done_Discharge2"),
        ("Coil", "DB_PLC1_Recv_From_PLC2_DB.Done_Discharge2")
    ])
    main.add_network("Modbus TCP Client - Copy Recv Heartbeat", [
        ("CMP_EQ", "MB_TCP_iStep", "1"),
        ("NO", "MB_TCP_DONE"),
        ("MOVE", "DB_PLC1_MB_Buffer_DB.Recv_Heartbeat", "DB_PLC1_Recv_From_PLC2_DB.Heartbeat")
    ])"""

replacement_client = """    # Map Send variables to Modbus Array (Data[0..2])
    main.add_network("Modbus TCP Client - Map Send CmdSeq to Array", [
        ("MOVE", "DB_PLC1_MB_Buffer_DB.Send_CmdSeq", "DB_PLC1_MB_Buffer_DB.Data[0]")
    ])
    main.add_network("Modbus TCP Client - Map Send Cmd_Start to Array", [
        ("NO", "DB_PLC1_MB_Buffer_DB.Send_Cmd_Start"),
        ("Coil", "DB_PLC1_MB_Buffer_DB.Data[1].%X0")
    ])
    main.add_network("Modbus TCP Client - Map Send Cmd_Stop to Array", [
        ("NO", "DB_PLC1_MB_Buffer_DB.Send_Cmd_Stop"),
        ("Coil", "DB_PLC1_MB_Buffer_DB.Data[1].%X1")
    ])
    main.add_network("Modbus TCP Client - Map Send Cmd_Reset to Array", [
        ("NO", "DB_PLC1_MB_Buffer_DB.Send_Cmd_Reset"),
        ("Coil", "DB_PLC1_MB_Buffer_DB.Data[1].%X2")
    ])
    main.add_network("Modbus TCP Client - Map Send Cmd_EStop to Array", [
        ("NO", "DB_PLC1_MB_Buffer_DB.Send_Cmd_EStop"),
        ("Coil", "DB_PLC1_MB_Buffer_DB.Data[1].%X3")
    ])
    main.add_network("Modbus TCP Client - Map Send Cmd_Pump_Branch2_To_SubTanks to Array", [
        ("NO", "DB_PLC1_MB_Buffer_DB.Send_Cmd_Pump_Branch2_To_SubTanks"),
        ("Coil", "DB_PLC1_MB_Buffer_DB.Data[1].%X4")
    ])
    main.add_network("Modbus TCP Client - Map Send Cmd_Load_Recipe to Array", [
        ("NO", "DB_PLC1_MB_Buffer_DB.Send_Cmd_Load_Recipe"),
        ("Coil", "DB_PLC1_MB_Buffer_DB.Data[1].%X5")
    ])
    main.add_network("Modbus TCP Client - Map Send Heartbeat to Array", [
        ("MOVE", "DB_PLC1_MB_Buffer_DB.Send_Heartbeat", "DB_PLC1_MB_Buffer_DB.Data[2]")
    ])

    # Step 0 Params
    main.add_network("Modbus TCP Client - Step 0 Mode", [
        ("CMP_EQ", "MB_TCP_iStep", "0"),
        ("MOVE", "1", "MB_TCP_Mode")
    ])
    main.add_network("Modbus TCP Client - Step 0 DataAddr", [
        ("CMP_EQ", "MB_TCP_iStep", "0"),
        ("MOVE", "40001", "MB_TCP_DataAddr")
    ])
    main.add_network("Modbus TCP Client - Step 0 DataLen", [
        ("CMP_EQ", "MB_TCP_iStep", "0"),
        ("MOVE", "3", "MB_TCP_DataLen")
    ])

    # Step 1 Params
    main.add_network("Modbus TCP Client - Step 1 Mode", [
        ("CMP_EQ", "MB_TCP_iStep", "1"),
        ("MOVE", "0", "MB_TCP_Mode")
    ])
    main.add_network("Modbus TCP Client - Step 1 DataAddr", [
        ("CMP_EQ", "MB_TCP_iStep", "1"),
        ("MOVE", "40001", "MB_TCP_DataAddr")
    ])
    main.add_network("Modbus TCP Client - Step 1 DataLen", [
        ("CMP_EQ", "MB_TCP_iStep", "1"),
        ("MOVE", "13", "MB_TCP_DataLen")
    ])

    # Trigger request when MB_CLIENT is not busy
    main.add_network("Modbus TCP Client - Trigger Request", [
        ("NC", "MB_TCP_BUSY"),
        ("Coil", "MB_TCP_REQ")
    ])

    # Call MB_CLIENT
    main.add_network("Modbus TCP Client - Call MB_CLIENT", [
        ("GENERIC", "MB_CLIENT", {
            "REQ": "MB_TCP_REQ",
            "DISCONNECT": "FALSE",
            "MB_MODE": "MB_TCP_Mode",
            "MB_DATA_ADDR": "MB_TCP_DataAddr",
            "MB_DATA_LEN": "MB_TCP_DataLen",
            "MB_DATA_PTR": "DB_PLC1_MB_Buffer_DB.Data",
            "CONNECT_ID": "1",
            "IP_OCTET_1": "192",
            "IP_OCTET_2": "168",
            "IP_OCTET_3": "0",
            "IP_OCTET_4": "2",
            "IP_PORT": "502"
        }, {
            "DONE": "MB_TCP_DONE",
            "BUSY": "MB_TCP_BUSY",
            "ERROR": "MB_TCP_ERROR",
            "STATUS": "MB_TCP_STATUS"
        }, {"Version": "3.1", "card1200": "1", "card1500": "0"}, "MB_CLIENT_DB")
    ])

    # Copy Recv From Buffer DB when Done in Step 1
    main.add_network("Modbus TCP Client - Copy Recv AckSeq", [
        ("CMP_EQ", "MB_TCP_iStep", "1"),
        ("NO", "MB_TCP_DONE"),
        ("MOVE", "DB_PLC1_MB_Buffer_DB.Data[3]", "DB_PLC1_Recv_From_PLC2_DB.AckSeq")
    ])
    main.add_network("Modbus TCP Client - Copy Recv Done_Branch2", [
        ("CMP_EQ", "MB_TCP_iStep", "1"),
        ("NO", "MB_TCP_DONE"),
        ("NO", "DB_PLC1_MB_Buffer_DB.Data[4].%X0"),
        ("Coil", "DB_PLC1_Recv_From_PLC2_DB.Done_Branch2")
    ])
    main.add_network("Modbus TCP Client - Copy Recv Done_Recipe", [
        ("CMP_EQ", "MB_TCP_iStep", "1"),
        ("NO", "MB_TCP_DONE"),
        ("NO", "DB_PLC1_MB_Buffer_DB.Data[4].%X1"),
        ("Coil", "DB_PLC1_Recv_From_PLC2_DB.Done_Recipe")
    ])
    main.add_network("Modbus TCP Client - Copy Recv Alarm", [
        ("CMP_EQ", "MB_TCP_iStep", "1"),
        ("NO", "MB_TCP_DONE"),
        ("NO", "DB_PLC1_MB_Buffer_DB.Data[4].%X2"),
        ("Coil", "DB_PLC1_Recv_From_PLC2_DB.Alarm")
    ])
    main.add_network("Modbus TCP Client - Copy Recv State", [
        ("CMP_EQ", "MB_TCP_iStep", "1"),
        ("NO", "MB_TCP_DONE"),
        ("MOVE", "DB_PLC1_MB_Buffer_DB.Data[5]", "DB_PLC1_Recv_From_PLC2_DB.State")
    ])
    main.add_network("Modbus TCP Client - Copy Recv PID_Bon4_SP", [
        ("CMP_EQ", "MB_TCP_iStep", "1"),
        ("NO", "MB_TCP_DONE"),
        ("MOVE", "DB_PLC1_MB_Buffer_DB.Data[6]", "AI_MB_Temp_W0"),
        ("MOVE", "DB_PLC1_MB_Buffer_DB.Data[7]", "AI_MB_Temp_W1"),
        ("MOVE", "AI_MB_Temp_Real1", "DB_PLC1_Recv_From_PLC2_DB.PID_Bon4_SP")
    ])
    main.add_network("Modbus TCP Client - Copy Recv PID_Bon4_PV", [
        ("CMP_EQ", "MB_TCP_iStep", "1"),
        ("NO", "MB_TCP_DONE"),
        ("MOVE", "DB_PLC1_MB_Buffer_DB.Data[8]", "AI_MB_Temp_W2"),
        ("MOVE", "DB_PLC1_MB_Buffer_DB.Data[9]", "AI_MB_Temp_W3"),
        ("MOVE", "AI_MB_Temp_Real2", "DB_PLC1_Recv_From_PLC2_DB.PID_Bon4_PV")
    ])
    main.add_network("Modbus TCP Client - Copy Recv PID_Bon4_CV", [
        ("CMP_EQ", "MB_TCP_iStep", "1"),
        ("NO", "MB_TCP_DONE"),
        ("MOVE", "DB_PLC1_MB_Buffer_DB.Data[10]", "AI_MB_Temp_W4"),
        ("MOVE", "DB_PLC1_MB_Buffer_DB.Data[11]", "AI_MB_Temp_W5"),
        ("MOVE", "AI_MB_Temp_Real3", "DB_PLC1_Recv_From_PLC2_DB.PID_Bon4_CV")
    ])
    main.add_network("Modbus TCP Client - Copy Recv Done_Discharge2", [
        ("CMP_EQ", "MB_TCP_iStep", "1"),
        ("NO", "MB_TCP_DONE"),
        ("NO", "DB_PLC1_MB_Buffer_DB.Data[4].%X3"),
        ("Coil", "DB_PLC1_Recv_From_PLC2_DB.Done_Discharge2")
    ])
    main.add_network("Modbus TCP Client - Copy Recv Heartbeat", [
        ("CMP_EQ", "MB_TCP_iStep", "1"),
        ("NO", "MB_TCP_DONE"),
        ("MOVE", "DB_PLC1_MB_Buffer_DB.Data[12]", "DB_PLC1_Recv_From_PLC2_DB.Heartbeat")
    ])"""

# --- PATCH 2: Server call update and logic map nhận ---
target_server = """    # 1. Call MB_SERVER block
    main.add_network("Modbus TCP Server - Call MB_SERVER", [
        ("GENERIC", "MB_SERVER", {
            "DISCONNECT": "FALSE",
            "CONNECT_ID": "1",
            "IP_PORT": "502",
            "MB_HOLD_REG": "DB_Modbus_Holding_Register_DB"
        }, {
            "NDR": "MB_TCP_Server_NDR",
            "DR": "MB_TCP_Server_DR",
            "ERROR": "MB_TCP_Server_Error",
            "STATUS": "MB_TCP_Server_Status"
        }, {"Version": "3.1", "card1200": "1", "card1500": "0"}, "MB_SERVER_DB")
    ])"""

replacement_server = """    # 1. Call MB_SERVER block
    main.add_network("Modbus TCP Server - Call MB_SERVER", [
        ("GENERIC", "MB_SERVER", {
            "DISCONNECT": "FALSE",
            "CONNECT_ID": "1",
            "IP_PORT": "502",
            "MB_HOLD_REG": "DB_Modbus_Holding_Register_DB.Data"
        }, {
            "NDR": "MB_TCP_Server_NDR",
            "DR": "MB_TCP_Server_DR",
            "ERROR": "MB_TCP_Server_Error",
            "STATUS": "MB_TCP_Server_Status"
        }, {"Version": "3.1", "card1200": "1", "card1500": "0"}, "MB_SERVER_DB")
    ])

    # 2. Map Modbus Array to Server Local Commands (解包 - Unpack Data[0..2])
    main.add_network("Modbus TCP Server - Map Modbus Array to CmdSeq", [
        ("MOVE", "DB_Modbus_Holding_Register_DB.Data[0]", "DB_Modbus_Holding_Register_DB.CmdSeq")
    ])
    main.add_network("Modbus TCP Server - Map Modbus Array to Cmd_Start", [
        ("NO", "DB_Modbus_Holding_Register_DB.Data[1].%X0"),
        ("Coil", "DB_Modbus_Holding_Register_DB.Cmd_Start")
    ])
    main.add_network("Modbus TCP Server - Map Modbus Array to Cmd_Stop", [
        ("NO", "DB_Modbus_Holding_Register_DB.Data[1].%X1"),
        ("Coil", "DB_Modbus_Holding_Register_DB.Cmd_Stop")
    ])
    main.add_network("Modbus TCP Server - Map Modbus Array to Cmd_Reset", [
        ("NO", "DB_Modbus_Holding_Register_DB.Data[1].%X2"),
        ("Coil", "DB_Modbus_Holding_Register_DB.Cmd_Reset")
    ])
    main.add_network("Modbus TCP Server - Map Modbus Array to Cmd_EStop", [
        ("NO", "DB_Modbus_Holding_Register_DB.Data[1].%X3"),
        ("Coil", "DB_Modbus_Holding_Register_DB.Cmd_EStop")
    ])
    main.add_network("Modbus TCP Server - Map Modbus Array to Cmd_Pump_Branch2_To_SubTanks", [
        ("NO", "DB_Modbus_Holding_Register_DB.Data[1].%X4"),
        ("Coil", "DB_Modbus_Holding_Register_DB.Cmd_Pump_Branch2_To_SubTanks")
    ])
    main.add_network("Modbus TCP Server - Map Modbus Array to Cmd_Load_Recipe", [
        ("NO", "DB_Modbus_Holding_Register_DB.Data[1].%X5"),
        ("Coil", "DB_Modbus_Holding_Register_DB.Cmd_Load_Recipe")
    ])
    main.add_network("Modbus TCP Server - Map Modbus Array to Heartbeat_Client", [
        ("MOVE", "DB_Modbus_Holding_Register_DB.Data[2]", "DB_Modbus_Holding_Register_DB.Heartbeat_Client")
    ])"""

# --- PATCH 3: Server logic map gửi ---
target_feedback = """    # Heartbeat Monitor PLC1 -> PLC2
    main.add_network("Modbus TCP Server - Monitor Heartbeat Change", [
        ("CMP_NE", "DB_Modbus_Holding_Register_DB.Heartbeat_Client", "PLC1_Heartbeat_Last"),
        ("Coil", "PLC1_Heartbeat_Changed")
    ])
    main.add_network("Modbus TCP Server - Heartbeat Timeout TON", [
        ("NC", "PLC1_Heartbeat_Changed"),
        ("TON", "Timers_PLC2.Timer_Heartbeat_PLC2", "T#5S", "PLC2_Heartbeat_Timeout")
    ])
    main.add_network("Modbus TCP Server - Save Last PLC1 Heartbeat", [
        ("MOVE", "DB_Modbus_Holding_Register_DB.Heartbeat_Client", "PLC1_Heartbeat_Last")
    ])"""

replacement_feedback = """    # Heartbeat Monitor PLC1 -> PLC2
    main.add_network("Modbus TCP Server - Monitor Heartbeat Change", [
        ("CMP_NE", "DB_Modbus_Holding_Register_DB.Heartbeat_Client", "PLC1_Heartbeat_Last"),
        ("Coil", "PLC1_Heartbeat_Changed")
    ])
    main.add_network("Modbus TCP Server - Heartbeat Timeout TON", [
        ("NC", "PLC1_Heartbeat_Changed"),
        ("TON", "Timers_PLC2.Timer_Heartbeat_PLC2", "T#5S", "PLC2_Heartbeat_Timeout")
    ])
    main.add_network("Modbus TCP Server - Save Last PLC1 Heartbeat", [
        ("MOVE", "DB_Modbus_Holding_Register_DB.Heartbeat_Client", "PLC1_Heartbeat_Last")
    ])

    # Modbus TCP Server - Map Local Variables to Modbus Array (打包 - Pack Data[3..12])
    main.add_network("Modbus TCP Server - Map AckSeq to Modbus Array", [
        ("MOVE", "DB_Modbus_Holding_Register_DB.AckSeq", "DB_Modbus_Holding_Register_DB.Data[3]")
    ])
    main.add_network("Modbus TCP Server - Map Status Bits to Modbus Array", [
        ("NO", "DB_Modbus_Holding_Register_DB.Done_Branch2"),
        ("Coil", "DB_Modbus_Holding_Register_DB.Data[4].%X0")
    ])
    main.add_network("Modbus TCP Server - Map Status Done_Recipe to Modbus Array", [
        ("NO", "DB_Modbus_Holding_Register_DB.Done_Recipe"),
        ("Coil", "DB_Modbus_Holding_Register_DB.Data[4].%X1")
    ])
    main.add_network("Modbus TCP Server - Map Status Alarm to Modbus Array", [
        ("NO", "DB_Modbus_Holding_Register_DB.Alarm"),
        ("Coil", "DB_Modbus_Holding_Register_DB.Data[4].%X2")
    ])
    main.add_network("Modbus TCP Server - Map Status Done_Discharge2 to Modbus Array", [
        ("NO", "DB_Modbus_Holding_Register_DB.Done_Discharge2"),
        ("Coil", "DB_Modbus_Holding_Register_DB.Data[4].%X3")
    ])
    main.add_network("Modbus TCP Server - Map State to Modbus Array", [
        ("MOVE", "DB_Modbus_Holding_Register_DB.State", "DB_Modbus_Holding_Register_DB.Data[5]")
    ])
    main.add_network("Modbus TCP Server - Map PID_Bon4_SP to Modbus Array", [
        ("MOVE", "DB_Modbus_Holding_Register_DB.PID_Bon4_SP", "AI_MB_Temp_Real1"),
        ("MOVE", "AI_MB_Temp_W0", "DB_Modbus_Holding_Register_DB.Data[6]"),
        ("MOVE", "AI_MB_Temp_W1", "DB_Modbus_Holding_Register_DB.Data[7]")
    ])
    main.add_network("Modbus TCP Server - Map PID_Bon4_PV to Modbus Array", [
        ("MOVE", "DB_Modbus_Holding_Register_DB.PID_Bon4_PV", "AI_MB_Temp_Real2"),
        ("MOVE", "AI_MB_Temp_W2", "DB_Modbus_Holding_Register_DB.Data[8]"),
        ("MOVE", "AI_MB_Temp_W3", "DB_Modbus_Holding_Register_DB.Data[9]")
    ])
    main.add_network("Modbus TCP Server - Map PID_Bon4_CV to Modbus Array", [
        ("MOVE", "DB_Modbus_Holding_Register_DB.PID_Bon4_CV", "AI_MB_Temp_Real3"),
        ("MOVE", "AI_MB_Temp_W4", "DB_Modbus_Holding_Register_DB.Data[10]"),
        ("MOVE", "AI_MB_Temp_W5", "DB_Modbus_Holding_Register_DB.Data[11]")
    ])
    main.add_network("Modbus TCP Server - Map Heartbeat_Server to Modbus Array", [
        ("MOVE", "DB_Modbus_Holding_Register_DB.Heartbeat_Server", "DB_Modbus_Holding_Register_DB.Data[12]")
    ])"""

# Perform replacement
if target_client in content:
    content = content.replace(target_client, replacement_client)
    print("PATCH 1 (Client): Success")
else:
    print("PATCH 1 (Client): Target string not found!")

if target_server in content:
    content = content.replace(target_server, replacement_server)
    print("PATCH 2 (Server): Success")
else:
    print("PATCH 2 (Server): Target string not found!")

if target_feedback in content:
    content = content.replace(target_feedback, replacement_feedback)
    print("PATCH 3 (Feedback): Success")
else:
    print("PATCH 3 (Feedback): Target string not found!")

with open(FILE_PATH, 'w', encoding='utf-8') as f:
    f.write(content)
print("File prepare_tia_import_sets.py updated.")
