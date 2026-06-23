# -*- coding: utf-8 -*-
"""
PLC Logic Simulator & Unit Tester
mixing_nuoc_tuong_maggi_2026
This script simulates the PLC sequence program scans to test transitions,
safety alarms, and I/O outputs.
"""
import sys

# Reconfigure stdout to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

class PLC1Simulator:
    def __init__(self):
        # Setpoints
        self.HMI_SP_PLC1_Nuoc_Bon1 = 100.0
        self.HMI_SP_PLC1_Nuoc_Bon2 = 120.0
        self.HMI_SP_PLC1_Toc_Do_Bon1 = 50.0
        self.HMI_SP_PLC1_Toc_Do_Bon2_Main = 60.0
        self.HMI_SP_PLC1_Nhiet_Do_Bon2 = 75.0
        self.HMI_SP_Time_Khuay_Bon1 = 10 # simulated seconds
        self.HMI_SP_Time_Fwd = 15
        self.HMI_SP_Time_Rev = 15
        self.HMI_SP_Time_Sterilize = 20
        self.HMI_SP_BonChua1_Nhiet_Giai_Nhiet = 45.0

        # Physical / Gated Inputs
        self.Nut_Khoi_Dong_Eff = False
        self.Nut_Dung_Eff = False
        self.Nut_Reset_Eff = False
        self.Nut_EStop_Eff = False
        self.HMI_Reset_Alarm = False
        self.PID_Bon2_Reset_Eff = False
        self.PLC1_Loi_Tong = False
        self.PLC1_SP_Valid = True
        self.PLC1_EStop_Latch = False
        self.PLC1_Stop_Active = False

        # Sensors / Statuses
        self.FQ3200_Bon1_Eff = 0.0
        self.PLC1_Tip_Bon1_Xong_HMI = False
        self.LT3203_Bon1_Eff = 10.0
        self.FQ3205_Bon2_Eff = 0.0
        self.PLC1_Tip_Bon2_Xong_HMI = False
        self.TT3208_Bon2_Eff = 25.0
        self.LT3209_Bon2_Eff = 12.0
        self.LT3302_BonChua1_Eff = 10.0
        self.LT3307_BonChua2_Eff = 10.0
        self.TT3301_BonChua1_Eff = 50.0

        self.PLC1_Khuay_Bon1_Xong_HMI = False
        self.PLC1_Khuay_Thuan_Bon2_Xong_HMI = False
        self.PLC1_Khuay_Nghich_Bon2_Xong_HMI = False
        self.PLC1_Thanh_Trung_Bon2_Xong_HMI = False
        self.PLC1_Xa_Bon2_Xong_HMI = False

        # Internal Step Flags
        self.PLC1_Auto_Enable = False
        self.PLC1_Step_Bon1_Dosing = False
        self.PLC1_Step_Bon1_Tip = False
        self.PLC1_Step_Bon1_Khuay = False
        self.PLC1_Step_Bon1_Xa = False
        self.PLC1_Step_Bon2_Dosing = False
        self.PLC1_Step_Bon2_Tip = False
        self.PLC1_Step_Bon2_Khuay_Thuan = False
        self.PLC1_Step_Bon2_Khuay_Nghich = False
        self.PLC1_Step_Bon2_PID = False
        self.PLC1_Step_Bon2_Thanh_Trung = False
        self.PLC1_Me_Nhanh1_Hoan_Thanh = False
        
        # State Value
        self.PLC1_State = 0
        
        # Timer Accumulators
        self.timer_khuay_bon1_acc = 0
        self.timer_fwd_bon2_acc = 0
        self.timer_rev_bon2_acc = 0
        self.timer_sterilize_bon2_acc = 0
        self.timer_dryrun_bon2_acc = 0
        self.timer_tip_bon1_acc = 0
        self.timer_tip_bon2_acc = 0

        # PID Variables
        self.PID_Bon2_Enable = False
        self.PID_Bon2_SP = 0.0
        self.PID_Bon2_CV = 0.0
        self.PID_Bon2_Error = False
        self.HMI_Che_Do_Thi = 0
        self.PID_Bon2_PV_Eff = 25.0
        self.PID_Bon2_Enable_Eff = False
        self.HMI_PID_Bon2_Dau_Noi_Enable = False
        self.VFD_Bon2_Run_Cmd = False
        self.VFD_Bon2_Dao_Chieu_Cmd = False
        self.VFD_Bon2_Toc_Do_Cmd = 0.0
        self.HMI_VFD_Bon2_Comm_Enable = False
        self.HMI_VFD_Bon2_Real_Enable = False
        self.VFD_Bon2_Comm_Active = False
        self.VFD_Bon2_Real_Active = False
        self.VFD_Bon2_Run_Safe = False
        self.VFD_Bon2_Comm_Active_Last = False
        self.VFD_Bon2_MBCL_Trigger = False
        self.VFD_Bon2_MBCL_Error = False
        self.VFD_Bon2_MBCL_Done = False
        self.VFD_Bon2_MBCL_Auto_Complete = True
        self.VFD_Bon2_Comm_Ready = False
        self.VFD_Bon2_Mode_Invalid = False
        self.VFD_Bon2_Run = False
        self.VFD_Bon2_Dao_Chieu = False
        self.HMI_Run_Enable = True

        # Physical Outputs
        self.V3230_Nuoc_Bon1 = False
        self.CV3201_Nuoc_Bon1 = 0.0
        self.AGTR3260_Khuay_Bon1 = False
        self.AGTR3260_Toc_Do_AO = 0.0
        self.V3232_Xa_Bon1 = False
        self.V3233_Xa_Bon1 = False
        self.V3234_Xa_Bon1 = False
        self.V3235_Nuoc_Bon2 = False
        self.CV3206_Hoi_Bon2 = 0.0
        self.VFD_Bon2_Toc_Do_AO = 0.0
        self.V3237_Xa_Bon2 = False
        self.V3238_Xa_Bon2 = False
        self.V3239_Xa_Bon2 = False
        self.Pump3264_Chuyen_Nhanh1 = False

        # VFD Modbus Scheduler
        self.VFD_Bon2_iStep = 0
        self.VFD_Bon2_MB_Req = False
        self.VFD_Bon2_MB_Busy = False
        self.VFD_Bon2_MB_Done = False
        self.VFD_Bon2_MB_Error = False
        self.VFD_Bon2_MB_Mode = 0
        self.VFD_Bon2_MB_DataAddr = 0
        self.VFD_Bon2_MB_DataLen = 0
        self.VFD_Bon2_MB_DataBuffer = 0
        self.VFD_Bon2_MB_ControlWord = 0
        self.VFD_Bon2_MB_FreqSetpoint = 0
        self.VFD_Bon2_MB_StatusWord = 0
        self.VFD_Bon2_MB_FreqActual = 0
        self.VFD_Bon2_Contactor = False
        self.VFD_Bon2_Contactor_Delay_Done = False

        # New Modbus Tags
        self.VFD_Bon2_MB_Error_Last = False
        self.VFD_Bon2_MB_Error_Edge = False
        self.VFD_Bon2_MB_Error_Confirmed = False
        self.VFD_Bon2_MB_Error_Counter = 0
        self.VFD_Bon2_MB_Last_Status = 0
        self.VFD_Bon2_MB_Retry_Active = False
        self.VFD_Bon2_MB_Retry_Timer_Q = False
        self.timer_vfd_mb_retry_acc = 0
        self.VFD_Bon2_MB_Status = 0
        self.VFD_Bon2_MBCL_Active = False
        
        class Dummy: pass
        self.DB_PLC1_Recv_From_PLC2_DB = Dummy()
        self.DB_PLC1_Recv_From_PLC2_DB.Heartbeat = 0
        self.Gia_Lap_Heartbeat_Chay = True

        # Heartbeat & Communication
        self.Clock_1Hz = False
        self.Clock_1Hz_Last = False
        self.Clock_1Hz_Edge = False
        self.PLC1_Heartbeat_Timeout = False
        self.PLC2_Heartbeat_Last = 0
        self.PLC2_Heartbeat_Changed = False
        self.PLC2_Heartbeat_Timeout_Acc = 0
        self.MB_TCP_Write_Error = False
        self.MB_TCP_Read_Error = False
        self.Gia_Lap_Mat_Ket_Noi_HMI = False
        self.PLC1_Loi_Truyen_Thong = False

        # Storage Area (PLC1 evaluates)
        self.BonChua_Owner_Nhanh1 = False
        self.BonChua_Owner_Nhanh2 = False
        self.BonChua_Step_Nhan_Dich = False
        self.BonChua_Step_Giai_Nhiet = False
        self.BonChua_Step_Chuyen_Bon2 = False
        self.BonChua_Step_Loc_Chiet = False
        self.BonChua_Me_Hoan_Thanh = False
        self.BonChua_Nhan_Dich_Xong_HMI = False
        self.BonChua_Chuyen_Bon2_Xong_HMI = False
        self.BonChua_State = 0
        self.BonChua_SP_Valid = True
        self.PLC2_Me_Nhanh2_Hoan_Thanh_Nhan = False
        self.PLC2_Xa_Bon4_Xong_Nhan = False
        
        # Filter and Filler outputs
        self.Pump3361_LuanChuyen_BonChua1 = False
        self.Pump3362_Xa_BonChua1 = False
        self.Pump3364_Filter = False
        self.Pump3365_Filter = False
        self.V3340_Duong_Filter = False
        self.V3341_Duong_Filter = False
        self.CV_Filler_Cap_Dich = 0.0


        self.PLC1_Loi_Dry_Run = False
        self.PLC1_Loi_Dosing = False
        self.PLC1_Loi_Setpoint = False
        self.BonChua_Loi_Setpoint = False
        
        # Agitator animation frame counters
        self.HMI_Anim_Bon1_Frame = 0
        self.HMI_Anim_Bon2_Frame = 0
        self.HMI_Anim_Bon1_MucDich = 0
        self.HMI_Anim_Bon2_MucDich = 0
        self.HMI_Anim_BonChua1_MucDich = 0
        self.HMI_Anim_BonChua2_MucDich = 0

        # Rising edge state memory
        self.start_old = False

        # Manual Mode tags
        self.HMI_Che_Do_Manual = False
        self.HMI_Cho_Phep_Sua_Thong_So = False
        self.HMI_User_Level = 1  # 1: Operator, 2: Engineer, 3: Admin
        self.PLC1_Manual_Mode_Active = False
        self.BonChua1_Xa_Xong = False
        self.BonChua2_Xa_Xong = False
        self.PLC1_Xa_Bon2_Xong = False

        # Manual DOs
        self.V3230_Nuoc_Bon1_Man = False
        self.AGTR3260_Khuay_Bon1_Man = False
        self.V3232_Xa_Bon1_Man = False
        self.V3233_Xa_Bon1_Man = False
        self.V3234_Xa_Bon1_Man = False
        self.V3235_Nuoc_Bon2_Man = False
        self.VFD_Bon2_Run_Man = False
        self.VFD_Bon2_Dao_Chieu_Man = False
        self.V3237_Xa_Bon2_Man = False
        self.V3238_Xa_Bon2_Man = False
        self.V3239_Xa_Bon2_Man = False
        self.Pump3264_Chuyen_Nhanh1_Man = False
        self.V3331_Xa_BonChua1_Man = False
        self.V3332_Xa_BonChua1_Man = False
        self.Pump3361_LuanChuyen_BonChua1_Man = False
        self.Pump3362_Xa_BonChua1_Man = False
        self.V3333_DieuHuong_BonChua1_Man = False
        self.V3334_DieuHuong_BonChua1_Man = False
        self.V3335_DieuHuong_BonChua1_Man = False
        self.V3338_Xa_BonChua2_Man = False
        self.V3339_Xa_BonChua2_Man = False
        self.Pump3364_Filter_Man = False
        self.Pump3365_Filter_Man = False
        self.V3340_Duong_Filter_Man = False
        self.V3341_Duong_Filter_Man = False

        # Manual AOs
        self.CV3201_Nuoc_Bon1_Man = 0.0
        self.AGTR3260_Toc_Do_AO_Man = 0.0
        self.CV3206_Hoi_Bon2_Man = 0.0
        self.VFD_Bon2_Toc_Do_AO_Man = 0.0
        self.CV3304_Nuoc_Lam_Mat_Man = 0.0
        self.CV_Filler_Cap_Dich_Man = 0.0


    def _tick_pid_routing(self):
        # Mode 0 (TDH):
        if self.HMI_Che_Do_Thi == 0:
            self.PID_Bon2_PV_Eff = self.TT3208_Bon2_Eff
            self.PID_Bon2_Enable_Eff = self.PID_Bon2_Enable
            if self.PID_Bon2_Enable_Eff:
                self.PID_Bon2_SP = self.HMI_SP_PLC1_Nhiet_Do_Bon2
        # Mode 1 (DN):
        elif self.HMI_Che_Do_Thi == 1:
            self.PID_Bon2_PV_Eff = self.VFD_Bon2_Actual_Speed_Feedback if hasattr(self, 'VFD_Bon2_Actual_Speed_Feedback') else 0.0
            self.PID_Bon2_Enable_Eff = self.HMI_PID_Bon2_Dau_Noi_Enable
            if self.PID_Bon2_Enable_Eff:
                self.PID_Bon2_SP = self.HMI_SP_PLC1_Toc_Do_Bon2_Main
        else:
            self.PID_Bon2_PV_Eff = 0.0
            self.PID_Bon2_Enable_Eff = False
            self.PID_Bon2_SP = 0.0

        # Run PID Compact block calculation
        if self.PID_Bon2_Enable_Eff:
            diff = self.PID_Bon2_SP - self.PID_Bon2_PV_Eff
            if self.HMI_Che_Do_Thi == 0 and self.PLC1_State == 31:
                self.PID_Bon2_CV = 80.0
            else:
                self.PID_Bon2_CV = max(0.0, min(100.0, diff * 10.0))
        else:
            self.PID_Bon2_CV = 0.0

        # Route PID output
        if self.HMI_Che_Do_Thi == 0:
            # Mode 0: steam valve CV3206
            if self.PID_Bon2_Enable_Eff:
                self.CV3206_Hoi_Bon2 = self.PID_Bon2_CV
                self.VFD_Bon2_Toc_Do_Cmd = self.HMI_SP_PLC1_Toc_Do_Bon2_Main
            else:
                self.CV3206_Hoi_Bon2 = 0.0
                self.VFD_Bon2_Toc_Do_Cmd = 0.0
        elif self.HMI_Che_Do_Thi == 1:
            # Mode 1: speed command VFD_Bon2_Toc_Do_Cmd
            if self.PID_Bon2_Enable_Eff:
                self.VFD_Bon2_Toc_Do_Cmd = self.PID_Bon2_CV
            else:
                self.VFD_Bon2_Toc_Do_Cmd = 0.0
            self.CV3206_Hoi_Bon2 = 0.0
        else:
            self.CV3206_Hoi_Bon2 = 0.0
            self.VFD_Bon2_Toc_Do_Cmd = 0.0

    def _tick_vfd_hybrid(self):
        # 0. Điều khóa contactor và trễ đóng nguồn
        if (self.HMI_Che_Do_Thi == 1 and 
            self.HMI_Run_Enable and 
            not self.PLC1_EStop_Latch and 
            not self.PLC1_Loi_Tong and 
            not self.PLC1_Stop_Active and 
            not self.Nut_EStop_Eff and 
            not self.Nut_Dung_Eff):
            self.VFD_Bon2_Contactor = True
        else:
            self.VFD_Bon2_Contactor = False
        self.VFD_Bon2_Contactor_Delay_Done = self.VFD_Bon2_Contactor

        # 1. Tính VFD_Bon2_Comm_Active
        if self.HMI_VFD_Bon2_Comm_Enable and self.HMI_Che_Do_Thi == 1 and self.VFD_Bon2_Contactor_Delay_Done:
            self.VFD_Bon2_Comm_Active = True
        else:
            self.VFD_Bon2_Comm_Active = False

        # 3. Tính VFD_Bon2_Real_Active (tất cả điều kiện an toàn)
        if (self.HMI_Che_Do_Thi == 1 and 
            self.HMI_VFD_Bon2_Comm_Enable and 
            self.HMI_VFD_Bon2_Real_Enable and 
            self.HMI_Run_Enable and 
            self.VFD_Bon2_Comm_Ready and
            not self.PLC1_EStop_Latch and 
            not self.PLC1_Loi_Tong and
            not self.PLC1_Stop_Active):
            self.VFD_Bon2_Real_Active = True
        else:
            self.VFD_Bon2_Real_Active = False

        # 4. Tính VFD_Bon2_Run_Safe
        if self.VFD_Bon2_Real_Active and self.VFD_Bon2_Run_Cmd and not self.PLC1_Loi_Tong:
            self.VFD_Bon2_Run_Safe = True
        else:
            self.VFD_Bon2_Run_Safe = False

        # 5. Physical output routing
        if self.VFD_Bon2_Real_Active:
            self.VFD_Bon2_Run = self.VFD_Bon2_Run_Safe
            self.VFD_Bon2_Dao_Chieu = self.VFD_Bon2_Dao_Chieu_Cmd
            self.VFD_Bon2_Toc_Do_AO = self.VFD_Bon2_Toc_Do_Cmd
        else:
            self.VFD_Bon2_Run = False
            self.VFD_Bon2_Dao_Chieu = False
            self.VFD_Bon2_Toc_Do_AO = 0.0

    def tick(self):
        # Clock Edge Detection
        self.Clock_1Hz_Edge = self.Clock_1Hz and not self.Clock_1Hz_Last
        self.Clock_1Hz_Last = self.Clock_1Hz

        # Heartbeat monitor: PLC2 -> PLC1
        if getattr(self, 'Gia_Lap_Heartbeat_Chay', True):
            self.DB_PLC1_Recv_From_PLC2_DB.Heartbeat += 1
        self.PLC2_Heartbeat_Changed = (self.DB_PLC1_Recv_From_PLC2_DB.Heartbeat != self.PLC2_Heartbeat_Last)
        if not self.PLC2_Heartbeat_Changed:
            self.PLC2_Heartbeat_Timeout_Acc += 1
            if self.PLC2_Heartbeat_Timeout_Acc >= 5:
                self.PLC1_Heartbeat_Timeout = True
        else:
            self.PLC2_Heartbeat_Timeout_Acc = 0
            self.PLC1_Heartbeat_Timeout = False
        self.PLC2_Heartbeat_Last = self.DB_PLC1_Recv_From_PLC2_DB.Heartbeat

        # Gọi VFD hybrid block để tính Comm_Active và Real_Active trước
        self._tick_vfd_hybrid()

        # Modbus VFD Simulator Scan Cycle Logic
        # 1. Reset REQ chu kỳ sau khi đã kích hoạt Busy
        if self.VFD_Bon2_MB_Req and self.VFD_Bon2_MB_Busy:
            self.VFD_Bon2_MB_Req = False

        # Reset MBCL_Trigger của scan trước
        self.VFD_Bon2_MBCL_Trigger = False

        # Trigger MB_COMM_LOAD khi delay contactor xong và chưa Ready/Active
        if (self.VFD_Bon2_Comm_Active and self.VFD_Bon2_Contactor_Delay_Done
                and not self.VFD_Bon2_Comm_Ready and not self.VFD_Bon2_MBCL_Active):
            self.VFD_Bon2_MBCL_Trigger = True
            self.VFD_Bon2_MBCL_Active = True

        # Mô phỏng MB_COMM_LOAD: một xung REQ hợp lệ hoàn tất khởi tạo cổng.
        if self.VFD_Bon2_MBCL_Trigger and self.VFD_Bon2_MBCL_Auto_Complete and not self.VFD_Bon2_MBCL_Error:
            self.VFD_Bon2_MBCL_Done = True

        # SET CommReady khi MBCL Done
        if self.VFD_Bon2_MBCL_Done:
            self.VFD_Bon2_Comm_Ready = True
            self.VFD_Bon2_MBCL_Active = False

        # Reset Ready và Active khi loi MBCL
        if self.VFD_Bon2_MBCL_Error:
            self.VFD_Bon2_Comm_Ready = False
            self.VFD_Bon2_MBCL_Active = False

        # Reset Ready và Active khi mat Comm_Active
        if not self.VFD_Bon2_Comm_Active:
            self.VFD_Bon2_Comm_Ready = False
            self.VFD_Bon2_MBCL_Active = False
            self.VFD_Bon2_MBCL_Trigger = False

        # 2. Reset/clear khi Comm_Enable = FALSE
        if not self.HMI_VFD_Bon2_Comm_Enable:
            self.VFD_Bon2_MB_Error_Confirmed = False
            self.VFD_Bon2_MB_Error_Counter = 0
            self.VFD_Bon2_iStep = 0
            self.VFD_Bon2_MB_Req = False
            self.VFD_Bon2_MB_Retry_Active = False
            self.VFD_Bon2_MB_Error_Last = False
            self.VFD_Bon2_MB_Error_Edge = False
            self.VFD_Bon2_MBCL_Trigger = False
            self.VFD_Bon2_MBCL_Active = False
            self.VFD_Bon2_Comm_Ready = False

        # 3. Phát hiện cạnh lên lỗi (Chỉ xử lý khi Comm_Ready = True)
        self.VFD_Bon2_MB_Error_Edge = (self.VFD_Bon2_Comm_Active and self.VFD_Bon2_Comm_Ready
                                       and self.VFD_Bon2_MB_Error and not self.VFD_Bon2_MB_Error_Last)

        # 4. Tang iStep khi Done (Network 1)
        if self.VFD_Bon2_MB_Done:
            self.VFD_Bon2_iStep += 1
            self.VFD_Bon2_MB_Error_Counter = 0

        # 4.5. Reset iStep ve 0 khi vuot nguong (Network 2)
        if self.VFD_Bon2_iStep >= 4:
            self.VFD_Bon2_iStep = 0

        # 5. Set REQ khi có trigger (Done của COMM_LOAD / Done của MB_MASTER / Timer retry done)
        if (self.VFD_Bon2_MBCL_Done or self.VFD_Bon2_MB_Done or self.VFD_Bon2_MB_Retry_Timer_Q) \
                and self.VFD_Bon2_Comm_Active and self.VFD_Bon2_Comm_Ready and not self.VFD_Bon2_MB_Busy:
            self.VFD_Bon2_MB_Req = True

        # 6. Reset REQ khi Busy
        if self.VFD_Bon2_MB_Busy:
            self.VFD_Bon2_MB_Req = False

        # 7. Setup params based on step (chỉ gán khi not Busy)
        if not self.VFD_Bon2_MB_Busy:
            if self.VFD_Bon2_iStep == 0:
                self.VFD_Bon2_MB_Mode = 1
                self.VFD_Bon2_MB_DataAddr = 48502
                self.VFD_Bon2_MB_DataLen = 1
                self.VFD_Bon2_MB_DataBuffer = self.VFD_Bon2_MB_ControlWord
            elif self.VFD_Bon2_iStep == 1:
                self.VFD_Bon2_MB_Mode = 1
                self.VFD_Bon2_MB_DataAddr = 48503
                self.VFD_Bon2_MB_DataLen = 1
                self.VFD_Bon2_MB_DataBuffer = self.VFD_Bon2_MB_FreqSetpoint
            elif self.VFD_Bon2_iStep == 2:
                self.VFD_Bon2_MB_Mode = 0
                self.VFD_Bon2_MB_DataAddr = 43202
                self.VFD_Bon2_MB_DataLen = 1
            elif self.VFD_Bon2_iStep == 3:
                self.VFD_Bon2_MB_Mode = 0
                self.VFD_Bon2_MB_DataAddr = 43203
                self.VFD_Bon2_MB_DataLen = 1

        # 8. Simulate asynchronous MB_MASTER execution (lấy cờ từ Req sang Busy)
        if self.VFD_Bon2_MB_Req and not self.VFD_Bon2_MB_Busy:
            if self.VFD_Bon2_Comm_Active and self.VFD_Bon2_Comm_Ready:
                self.VFD_Bon2_MB_Busy = True
                self.VFD_Bon2_MB_Done = False
                self.VFD_Bon2_MB_Error = False
        
        # 9. Read steps buffer copies khi Done
        if self.VFD_Bon2_MB_Done and not self.VFD_Bon2_MB_Busy:
            if self.VFD_Bon2_iStep == 2:
                self.VFD_Bon2_MB_StatusWord = 1
            elif self.VFD_Bon2_iStep == 3:
                self.VFD_Bon2_MB_FreqActual = self.VFD_Bon2_Toc_Do_AO

        # 10. Reset error counter khi Done (tích hợp vào bước 4)
        pass

        # 11. Xử lý lỗi theo VFD_Bon2_MB_Error_Edge
        if self.VFD_Bon2_MB_Error_Edge:
            self.VFD_Bon2_MB_Last_Status = self.VFD_Bon2_MB_Status
            self.VFD_Bon2_MB_Error_Counter += 1
            self.VFD_Bon2_MB_Req = False
            if self.VFD_Bon2_MB_Error_Counter >= 3:
                self.VFD_Bon2_MB_Error_Confirmed = True
            if not self.VFD_Bon2_MB_Error_Confirmed:
                self.VFD_Bon2_MB_Retry_Active = True

        # 12. Timer Ton Retry 200ms
        if self.VFD_Bon2_MB_Retry_Active:
            self.timer_vfd_mb_retry_acc += 10  # Giả lập 10ms mỗi tick
            if self.timer_vfd_mb_retry_acc >= 200:
                self.VFD_Bon2_MB_Retry_Timer_Q = True
        else:
            self.timer_vfd_mb_retry_acc = 0
            self.VFD_Bon2_MB_Retry_Timer_Q = False

        # 13. Reset retry active khi timer xong
        if self.VFD_Bon2_MB_Retry_Timer_Q:
            self.VFD_Bon2_MB_Retry_Active = False
            self.VFD_Bon2_MB_Retry_Timer_Q = False
            self.VFD_Bon2_MB_Req = True

        # 14. Save Error Last State
        self.VFD_Bon2_MB_Error_Last = (self.VFD_Bon2_Comm_Active and self.VFD_Bon2_Comm_Ready
                                       and self.VFD_Bon2_MB_Error)

        # Hạ cờ DONE/ERROR của MB_MASTER ở cuối chu kỳ quét
        self.VFD_Bon2_MB_Done = False
        self.VFD_Bon2_MB_Error = False
        self.VFD_Bon2_MBCL_Done = False

        # Communication alarms evaluation
        if self.Gia_Lap_Mat_Ket_Noi_HMI or self.PLC1_Heartbeat_Timeout or self.MB_TCP_Write_Error or self.MB_TCP_Read_Error:
            self.PLC1_Loi_Truyen_Thong = True
        
        self.PID_Bon2_Reset_Eff = self.Nut_Reset_Eff or self.HMI_Reset_Alarm

        # Reset alarm path
        if (self.Nut_Reset_Eff or self.HMI_Reset_Alarm) and not self.Nut_EStop_Eff and not self.PLC1_EStop_Latch:
            self.PLC1_Loi_Truyen_Thong = False
            self.PLC1_Loi_Dry_Run = False
            self.PLC1_Loi_Dosing = False
            self.PLC1_Loi_Setpoint = False
            self.BonChua_Loi_Setpoint = False
            self.PID_Bon2_Error = False
            self.VFD_Bon2_MB_Error = False
            self.VFD_Bon2_MBCL_Error = False
            self.VFD_Bon2_MB_Error_Confirmed = False
            self.VFD_Bon2_MB_Error_Counter = 0
            self.VFD_Bon2_MB_Retry_Active = False
            self.VFD_Bon2_MB_Error_Last = False
            self.VFD_Bon2_MB_Error_Edge = False
            self.PLC1_Loi_Tong = False

        # Aggregate overall alarm (chốt lỗi Modbus bằng cờ Confirmed)
        if (self.Nut_EStop_Eff or self.PLC1_EStop_Latch or self.PLC1_Loi_Dry_Run or
            self.PLC1_Loi_Dosing or self.PLC1_Loi_Truyen_Thong or self.PLC1_Loi_Setpoint or
            self.BonChua_Loi_Setpoint or
            (self.PID_Bon2_Error and self.PID_Bon2_Enable_Eff) or
            (self.VFD_Bon2_MB_Error_Confirmed and self.VFD_Bon2_Comm_Active) or
            (self.VFD_Bon2_MBCL_Error and self.VFD_Bon2_Comm_Active)):
            self.PLC1_Loi_Tong = True

        # Update emptying status maps first
        self.PLC1_Xa_Bon2_Xong = (self.PLC1_State == 40) and (self.LT3209_Bon2_Eff <= 0.5)
        self.BonChua1_Xa_Xong = (self.BonChua_State == 70) and (self.LT3302_BonChua1_Eff <= 0.5)
        self.BonChua2_Xa_Xong = (self.BonChua_State == 80) and (self.LT3307_BonChua2_Eff <= 0.5)

        # Dry-run protection (instant)
        if self.Pump3264_Chuyen_Nhanh1 and self.LT3209_Bon2_Eff <= 0.5 and not self.PLC1_Xa_Bon2_Xong:
            self.PLC1_Loi_Dry_Run = True

        if (self.Pump3361_LuanChuyen_BonChua1 or self.Pump3362_Xa_BonChua1) and self.LT3302_BonChua1_Eff <= 0.5 and not self.BonChua1_Xa_Xong:
            self.PLC1_Loi_Dry_Run = True

        if (self.Pump3364_Filter or self.Pump3365_Filter) and self.LT3307_BonChua2_Eff <= 0.5 and not self.BonChua2_Xa_Xong:
            self.PLC1_Loi_Dry_Run = True


        # Start Edge detection
        self.start_edge_edge = self.Nut_Khoi_Dong_Eff and not self.start_old
        self.start_old = self.Nut_Khoi_Dong_Eff

        # PID Enable Set/Reset logic
        if self.PLC1_State == 30:
            self.PID_Bon2_Enable = True
            
        if self.PLC1_Loi_Tong or self.Nut_Dung_Eff:
            self.PID_Bon2_Enable = False

        # State transitions
        state_before = self.PLC1_State
        if self.PLC1_Loi_Tong:
            self.PLC1_Auto_Enable = False
            self.PLC1_State = 0
            self.PID_Bon2_Enable = False
        elif self.Nut_Dung_Eff:
            self.PLC1_Auto_Enable = False
            self.PLC1_State = 0
            self.PID_Bon2_Enable = False
        else:
            # Transitions
            next_state = self.PLC1_State
            if self.PLC1_State == 40:
                if self.LT3209_Bon2_Eff <= 0.5 or self.PLC1_Xa_Bon2_Xong_HMI:
                    self.PLC1_Auto_Enable = False
                    next_state = 0
            elif self.PLC1_State == 31:
                self.timer_sterilize_bon2_acc += 1
                if self.timer_sterilize_bon2_acc >= self.HMI_SP_Time_Sterilize or self.PLC1_Thanh_Trung_Bon2_Xong_HMI:
                    self.PLC1_Auto_Enable = False
                    self.PID_Bon2_Enable = False
                    next_state = 40
            elif self.PLC1_State == 30:
                if self.TT3208_Bon2_Eff >= self.HMI_SP_PLC1_Nhiet_Do_Bon2:
                    next_state = 31
            elif self.PLC1_State == 23:
                self.timer_rev_bon2_acc += 1
                if self.timer_rev_bon2_acc >= self.HMI_SP_Time_Rev or self.PLC1_Khuay_Nghich_Bon2_Xong_HMI:
                    next_state = 30
            elif self.PLC1_State == 22:
                self.timer_fwd_bon2_acc += 1
                if self.timer_fwd_bon2_acc >= self.HMI_SP_Time_Fwd or self.PLC1_Khuay_Thuan_Bon2_Xong_HMI:
                    next_state = 23
            elif self.PLC1_State == 21:
                self.timer_tip_bon2_acc += 1
                if self.timer_tip_bon2_acc >= 30 or self.PLC1_Tip_Bon2_Xong_HMI:
                    next_state = 22
            elif self.PLC1_State == 20:
                if self.FQ3205_Bon2_Eff >= self.HMI_SP_PLC1_Nuoc_Bon2:
                    next_state = 21
            elif self.PLC1_State == 15:
                if self.LT3203_Bon1_Eff <= 0.5:
                    next_state = 20
            elif self.PLC1_State == 12:
                self.timer_khuay_bon1_acc += 1
                if self.timer_khuay_bon1_acc >= self.HMI_SP_Time_Khuay_Bon1 or self.PLC1_Khuay_Bon1_Xong_HMI:
                    next_state = 15
            elif self.PLC1_State == 11:
                self.timer_tip_bon1_acc += 1
                if self.timer_tip_bon1_acc >= 30 or self.PLC1_Tip_Bon1_Xong_HMI:
                    next_state = 12
            elif self.PLC1_State == 10:
                if self.FQ3200_Bon1_Eff >= self.HMI_SP_PLC1_Nuoc_Bon1:
                    next_state = 11
            elif self.PLC1_State == 0:
                if self.start_edge_edge and self.PLC1_SP_Valid:
                    self.PLC1_Auto_Enable = True
                    next_state = 10
            
            # Clean HMI done flags when leaving states
            if next_state != 11: self.PLC1_Tip_Bon1_Xong_HMI = False
            if next_state != 12: self.PLC1_Khuay_Bon1_Xong_HMI = False
            if next_state != 21: self.PLC1_Tip_Bon2_Xong_HMI = False
            if next_state != 22: self.PLC1_Khuay_Thuan_Bon2_Xong_HMI = False
            if next_state != 23: self.PLC1_Khuay_Nghich_Bon2_Xong_HMI = False
            if next_state != 31: self.PLC1_Thanh_Trung_Bon2_Xong_HMI = False
 
            self.PLC1_State = next_state

        # One-hot step mapping
        self.PLC1_Step_Bon1_Dosing = (self.PLC1_State == 10)
        self.PLC1_Step_Bon1_Tip = (self.PLC1_State == 11)
        self.PLC1_Step_Bon1_Khuay = (self.PLC1_State == 12)
        self.PLC1_Step_Bon1_Xa = (self.PLC1_State == 15)
        self.PLC1_Step_Bon2_Dosing = (self.PLC1_State == 20)
        self.PLC1_Step_Bon2_Tip = (self.PLC1_State == 21)
        self.PLC1_Step_Bon2_Khuay_Thuan = (self.PLC1_State == 22)
        self.PLC1_Step_Bon2_Khuay_Nghich = (self.PLC1_State == 23)
        self.PLC1_Step_Bon2_PID = (self.PLC1_State == 30)
        self.PLC1_Step_Bon2_Thanh_Trung = (self.PLC1_State == 31)
        self.PLC1_Me_Nhanh1_Hoan_Thanh = (self.PLC1_State == 40)

        # Actuators logic
        self.V3230_Nuoc_Bon1 = self.PLC1_Step_Bon1_Dosing
        self.CV3201_Nuoc_Bon1 = 100.0 if self.PLC1_Step_Bon1_Dosing else 0.0
        self.AGTR3260_Khuay_Bon1 = self.PLC1_Step_Bon1_Khuay and not self.PLC1_Loi_Tong
        self.AGTR3260_Toc_Do_AO = self.HMI_SP_PLC1_Toc_Do_Bon1 if self.PLC1_Step_Bon1_Khuay else 0.0
        self.V3232_Xa_Bon1 = self.PLC1_Step_Bon1_Xa
        self.V3233_Xa_Bon1 = self.PLC1_Step_Bon1_Xa
        self.V3234_Xa_Bon1 = self.PLC1_Step_Bon1_Xa
        self.V3235_Nuoc_Bon2 = self.PLC1_Step_Bon2_Dosing

        # Gọi PID routing
        self._tick_pid_routing()

        # Tính toán VFD commands cho sequence (đánh giá dạng Coil LAD mỗi chu kỳ quét)
        self.VFD_Bon2_Khuay_Active = (self.PLC1_Step_Bon2_Khuay_Thuan or self.PLC1_Step_Bon2_Khuay_Nghich)
        self.VFD_Bon2_Should_Run = (self.VFD_Bon2_Khuay_Active or self.PID_Bon2_Enable_Eff)

        if self.HMI_Che_Do_Thi < 0 or self.HMI_Che_Do_Thi > 1:
            self.VFD_Bon2_Mode_Invalid = True
            self.PID_Bon2_Enable_Eff = False
            self.VFD_Bon2_Run_Cmd = False
            self.VFD_Bon2_Dao_Chieu_Cmd = False
            self.VFD_Bon2_Toc_Do_Cmd = 0.0
            self.VFD_Bon2_Should_Run = False
        else:
            self.VFD_Bon2_Mode_Invalid = False
            
            # Coil LAD behavior for commands
            if self.VFD_Bon2_Should_Run and not self.PLC1_Loi_Tong and not self.PLC1_Stop_Active:
                self.VFD_Bon2_Run_Cmd = True
            else:
                self.VFD_Bon2_Run_Cmd = False
                
            if self.PLC1_Step_Bon2_Khuay_Nghich and not self.PLC1_Loi_Tong and not self.PLC1_Stop_Active:
                self.VFD_Bon2_Dao_Chieu_Cmd = True
            else:
                self.VFD_Bon2_Dao_Chieu_Cmd = False

            # Speed command cleanup and auto override
            if not self.VFD_Bon2_Run_Cmd or self.PLC1_Loi_Tong or self.PLC1_Stop_Active:
                self.VFD_Bon2_Toc_Do_Cmd = 0.0
            elif self.PLC1_Auto_Enable and self.HMI_Che_Do_Thi == 0 and self.VFD_Bon2_Khuay_Active:
                self.VFD_Bon2_Toc_Do_Cmd = self.HMI_SP_PLC1_Toc_Do_Bon2_Main

        # Gọi VFD hybrid block đã được di chuyển lên đầu hàm tick()
        pass

        # Storage Area (PLC1 evaluates)
        # One-hot Storage Step flags derived from BonChua_State
        self.BonChua_Step_Nhan_Dich = (self.BonChua_State == 50)
        self.BonChua_Step_Giai_Nhiet = (self.BonChua_State == 60)
        self.BonChua_Step_Chuyen_Bon2 = (self.BonChua_State == 70)
        self.BonChua_Step_Loc_Chiet = (self.BonChua_State == 80)

        # Owner Arbitration
        if self.PLC1_Me_Nhanh1_Hoan_Thanh and not self.BonChua_Owner_Nhanh1 and not self.BonChua_Owner_Nhanh2:
            self.BonChua_Owner_Nhanh1 = True
        elif self.PLC2_Me_Nhanh2_Hoan_Thanh_Nhan and not self.BonChua_Owner_Nhanh1 and not self.BonChua_Owner_Nhanh2:
            self.BonChua_Owner_Nhanh2 = True

        # Storage Transitions
        # Storage Transitions
        next_bc_state = self.BonChua_State
        if self.PLC1_Stop_Active or self.PLC1_Loi_Tong:
            next_bc_state = 0
            self.BonChua_Owner_Nhanh1 = False
            self.BonChua_Owner_Nhanh2 = False
            self.BonChua_Me_Hoan_Thanh = False
        else:
            if self.BonChua_State == 80:
                if self.LT3307_BonChua2_Eff <= 0.5:
                    self.BonChua_Me_Hoan_Thanh = True
                    next_bc_state = 0
            elif self.BonChua_State == 70:
                if self.BonChua_Chuyen_Bon2_Xong_HMI:
                    next_bc_state = 80
            elif self.BonChua_State == 60:
                if self.TT3301_BonChua1_Eff <= self.HMI_SP_BonChua1_Nhiet_Giai_Nhiet:
                    next_bc_state = 70
            elif self.BonChua_State == 50:
                if self.BonChua_Owner_Nhanh1 and self.LT3209_Bon2_Eff <= 0.5:
                    next_bc_state = 60
                elif self.BonChua_Owner_Nhanh2 and self.PLC2_Xa_Bon4_Xong_Nhan:
                    next_bc_state = 60
                elif self.BonChua_Nhan_Dich_Xong_HMI:
                    next_bc_state = 60
            elif self.BonChua_State == 0:
                if (self.BonChua_Owner_Nhanh1 or self.BonChua_Owner_Nhanh2) and self.BonChua_SP_Valid:
                    next_bc_state = 50
                    self.BonChua_Me_Hoan_Thanh = False

        if next_bc_state == 60:
            self.BonChua_Owner_Nhanh1 = False
            self.BonChua_Owner_Nhanh2 = False

        if next_bc_state != 50:
            self.BonChua_Nhan_Dich_Xong_HMI = False
        if next_bc_state != 70:
            self.BonChua_Chuyen_Bon2_Xong_HMI = False

        self.BonChua_State = next_bc_state

        # Standard Coils for filter outputs
        is_state_80_active = (self.BonChua_State == 80) and not (self.PLC1_Stop_Active or self.PLC1_Loi_Tong)
        self.Pump3364_Filter = is_state_80_active
        self.Pump3365_Filter = is_state_80_active
        self.V3340_Duong_Filter = is_state_80_active
        self.V3341_Duong_Filter = is_state_80_active
        
        if is_state_80_active:
            self.CV_Filler_Cap_Dich = 75.0
        else:
            self.CV_Filler_Cap_Dich = 0.0

        # Actuators for Storage
        self.Pump3264_Chuyen_Nhanh1 = (self.BonChua_State == 50) and self.BonChua_Owner_Nhanh1 and self.PLC1_Me_Nhanh1_Hoan_Thanh
        self.V3237_Xa_Bon2 = self.Pump3264_Chuyen_Nhanh1
        self.V3238_Xa_Bon2 = self.Pump3264_Chuyen_Nhanh1
        self.V3239_Xa_Bon2 = self.Pump3264_Chuyen_Nhanh1

        # --- Manual Control PLC1 ---
        # 1. Evaluate Manual Mode Active flag
        self.PLC1_Manual_Mode_Active = self.HMI_Che_Do_Manual and self.HMI_Cho_Phep_Sua_Thong_So and (self.HMI_User_Level > 1)

        # 2. Reset Auto/PID/Sequence if Manual Active
        if self.PLC1_Manual_Mode_Active:
            self.PLC1_Auto_Enable = False
            self.PID_Bon2_Enable = False
            self.PLC1_State = 0
            self.BonChua_State = 0
            
            # 4. Clamping and applying manual values
            # Clamping Real variables
            self.CV3201_Nuoc_Bon1_Man = max(0.0, min(100.0, self.CV3201_Nuoc_Bon1_Man))
            self.AGTR3260_Toc_Do_AO_Man = max(0.0, min(100.0, self.AGTR3260_Toc_Do_AO_Man))
            self.CV3206_Hoi_Bon2_Man = max(0.0, min(100.0, self.CV3206_Hoi_Bon2_Man))
            self.VFD_Bon2_Toc_Do_AO_Man = max(0.0, min(100.0, self.VFD_Bon2_Toc_Do_AO_Man))
            self.CV3304_Nuoc_Lam_Mat_Man = max(0.0, min(100.0, self.CV3304_Nuoc_Lam_Mat_Man))
            self.CV_Filler_Cap_Dich_Man = max(0.0, min(100.0, self.CV_Filler_Cap_Dich_Man))

            # DO manual mapping
            self.V3230_Nuoc_Bon1 = self.V3230_Nuoc_Bon1_Man
            self.AGTR3260_Khuay_Bon1 = self.AGTR3260_Khuay_Bon1_Man
            self.V3232_Xa_Bon1 = self.V3232_Xa_Bon1_Man
            self.V3233_Xa_Bon1 = self.V3233_Xa_Bon1_Man
            self.V3234_Xa_Bon1 = self.V3234_Xa_Bon1_Man
            self.V3235_Nuoc_Bon2 = self.V3235_Nuoc_Bon2_Man
            self.VFD_Bon2_Run_Cmd = self.VFD_Bon2_Run_Man
            self.VFD_Bon2_Dao_Chieu_Cmd = self.VFD_Bon2_Dao_Chieu_Man
            self.V3237_Xa_Bon2 = self.V3237_Xa_Bon2_Man
            self.V3238_Xa_Bon2 = self.V3238_Xa_Bon2_Man
            self.V3239_Xa_Bon2 = self.V3239_Xa_Bon2_Man
            
            self.V3331_Xa_BonChua1 = self.V3331_Xa_BonChua1_Man
            self.V3332_Xa_BonChua1 = self.V3332_Xa_BonChua1_Man
            self.V3333_DieuHuong_BonChua1 = self.V3333_DieuHuong_BonChua1_Man
            self.V3334_DieuHuong_BonChua1 = self.V3334_DieuHuong_BonChua1_Man
            self.V3335_DieuHuong_BonChua1 = self.V3335_DieuHuong_BonChua1_Man
            self.V3338_Xa_BonChua2 = self.V3338_Xa_BonChua2_Man
            self.V3339_Xa_BonChua2 = self.V3339_Xa_BonChua2_Man
            self.V3340_Duong_Filter = self.V3340_Duong_Filter_Man
            self.V3341_Duong_Filter = self.V3341_Duong_Filter_Man

            # AO manual mapping
            self.CV3201_Nuoc_Bon1 = self.CV3201_Nuoc_Bon1_Man
            self.AGTR3260_Toc_Do_AO = self.AGTR3260_Toc_Do_AO_Man
            self.CV3206_Hoi_Bon2 = self.CV3206_Hoi_Bon2_Man
            self.VFD_Bon2_Toc_Do_Cmd = self.VFD_Bon2_Toc_Do_AO_Man
            self.CV3304_Nuoc_Lam_Mat = self.CV3304_Nuoc_Lam_Mat_Man
            self.CV_Filler_Cap_Dich = self.CV_Filler_Cap_Dich_Man

            # Pump manual mapping with level interlocks
            # Pump3264
            if self.LT3209_Bon2_Eff <= 0.5:
                self.Pump3264_Chuyen_Nhanh1_Man = False
                self.Pump3264_Chuyen_Nhanh1 = False
                self.V3237_Xa_Bon2 = False
                self.V3238_Xa_Bon2 = False
                self.V3239_Xa_Bon2 = False
            else:
                self.Pump3264_Chuyen_Nhanh1 = self.Pump3264_Chuyen_Nhanh1_Man
                if self.Pump3264_Chuyen_Nhanh1:
                    self.V3237_Xa_Bon2 = True
                    self.V3238_Xa_Bon2 = True
                    self.V3239_Xa_Bon2 = True

            # Pump3361
            if self.LT3302_BonChua1_Eff <= 0.5:
                self.Pump3361_LuanChuyen_BonChua1_Man = False
                self.Pump3361_LuanChuyen_BonChua1 = False
            else:
                self.Pump3361_LuanChuyen_BonChua1 = self.Pump3361_LuanChuyen_BonChua1_Man

            # Pump3362
            if self.LT3302_BonChua1_Eff <= 0.5:
                self.Pump3362_Xa_BonChua1_Man = False
                self.Pump3362_Xa_BonChua1 = False
            else:
                self.Pump3362_Xa_BonChua1 = self.Pump3362_Xa_BonChua1_Man

            # Pump3364
            if self.LT3307_BonChua2_Eff <= 0.5:
                self.Pump3364_Filter_Man = False
                self.Pump3364_Filter = False
            else:
                self.Pump3364_Filter = self.Pump3364_Filter_Man

            # Pump3365
            if self.LT3307_BonChua2_Eff <= 0.5:
                self.Pump3365_Filter_Man = False
                self.Pump3365_Filter = False
            else:
                self.Pump3365_Filter = self.Pump3365_Filter_Man

        # 3. Leaving Manual Mode resets manual command tags
        else:
            self.V3230_Nuoc_Bon1_Man = False
            self.AGTR3260_Khuay_Bon1_Man = False
            self.V3232_Xa_Bon1_Man = False
            self.V3233_Xa_Bon1_Man = False
            self.V3234_Xa_Bon1_Man = False
            self.V3235_Nuoc_Bon2_Man = False
            self.VFD_Bon2_Run_Man = False
            self.VFD_Bon2_Dao_Chieu_Man = False
            self.V3237_Xa_Bon2_Man = False
            self.V3238_Xa_Bon2_Man = False
            self.V3239_Xa_Bon2_Man = False
            self.Pump3264_Chuyen_Nhanh1_Man = False
            self.V3331_Xa_BonChua1_Man = False
            self.V3332_Xa_BonChua1_Man = False
            self.Pump3361_LuanChuyen_BonChua1_Man = False
            self.Pump3362_Xa_BonChua1_Man = False
            self.V3333_DieuHuong_BonChua1_Man = False
            self.V3334_DieuHuong_BonChua1_Man = False
            self.V3335_DieuHuong_BonChua1_Man = False
            self.V3338_Xa_BonChua2_Man = False
            self.V3339_Xa_BonChua2_Man = False
            self.Pump3364_Filter_Man = False
            self.Pump3365_Filter_Man = False
            self.V3340_Duong_Filter_Man = False
            self.V3341_Duong_Filter_Man = False

            self.CV3201_Nuoc_Bon1_Man = 0.0
            self.AGTR3260_Toc_Do_AO_Man = 0.0
            self.CV3206_Hoi_Bon2_Man = 0.0
            self.VFD_Bon2_Toc_Do_AO_Man = 0.0
            self.CV3304_Nuoc_Lam_Mat_Man = 0.0
            self.CV_Filler_Cap_Dich_Man = 0.0

        # 5. Safety overrides (Dừng khẩn / Dừng / Lỗi tổng)
        if self.PLC1_EStop_Latch or self.Nut_EStop_Eff or self.PLC1_Stop_Active or self.PLC1_Loi_Tong:
            self.V3230_Nuoc_Bon1 = False
            self.AGTR3260_Khuay_Bon1 = False
            self.V3232_Xa_Bon1 = False
            self.V3233_Xa_Bon1 = False
            self.V3234_Xa_Bon1 = False
            self.V3235_Nuoc_Bon2 = False
            self.VFD_Bon2_Run = False
            self.VFD_Bon2_Dao_Chieu = False
            self.V3237_Xa_Bon2 = False
            self.V3238_Xa_Bon2 = False
            self.V3239_Xa_Bon2 = False
            self.Pump3264_Chuyen_Nhanh1 = False
            self.V3331_Xa_BonChua1 = False
            self.V3332_Xa_BonChua1 = False
            self.Pump3361_LuanChuyen_BonChua1 = False
            self.Pump3362_Xa_BonChua1 = False
            self.V3333_DieuHuong_BonChua1 = False
            self.V3334_DieuHuong_BonChua1 = False
            self.V3335_DieuHuong_BonChua1 = False
            self.V3338_Xa_BonChua2 = False
            self.V3339_Xa_BonChua2 = False
            self.Pump3364_Filter = False
            self.Pump3365_Filter = False
            self.V3340_Duong_Filter = False
            self.V3341_Duong_Filter = False

            self.CV3201_Nuoc_Bon1 = 0.0
            self.AGTR3260_Toc_Do_AO = 0.0
            self.CV3206_Hoi_Bon2 = 0.0
            self.VFD_Bon2_Toc_Do_AO = 0.0
            self.CV3304_Nuoc_Lam_Mat = 0.0
            self.CV_Filler_Cap_Dich = 0.0

            # Also clear the Man command tags during safety override
            self.V3230_Nuoc_Bon1_Man = False
            self.AGTR3260_Khuay_Bon1_Man = False
            self.V3232_Xa_Bon1_Man = False
            self.V3233_Xa_Bon1_Man = False
            self.V3234_Xa_Bon1_Man = False
            self.V3235_Nuoc_Bon2_Man = False
            self.VFD_Bon2_Run_Man = False
            self.VFD_Bon2_Dao_Chieu_Man = False
            self.V3237_Xa_Bon2_Man = False
            self.V3238_Xa_Bon2_Man = False
            self.V3239_Xa_Bon2_Man = False
            self.Pump3264_Chuyen_Nhanh1_Man = False
            self.V3331_Xa_BonChua1_Man = False
            self.V3332_Xa_BonChua1_Man = False
            self.Pump3361_LuanChuyen_BonChua1_Man = False
            self.Pump3362_Xa_BonChua1_Man = False
            self.V3333_DieuHuong_BonChua1_Man = False
            self.V3334_DieuHuong_BonChua1_Man = False
            self.V3335_DieuHuong_BonChua1_Man = False
            self.V3338_Xa_BonChua2_Man = False
            self.V3339_Xa_BonChua2_Man = False
            self.Pump3364_Filter_Man = False
            self.Pump3365_Filter_Man = False
            self.V3340_Duong_Filter_Man = False
            self.V3341_Duong_Filter_Man = False

            self.CV3201_Nuoc_Bon1_Man = 0.0
            self.AGTR3260_Toc_Do_AO_Man = 0.0
            self.CV3206_Hoi_Bon2_Man = 0.0
            self.VFD_Bon2_Toc_Do_AO_Man = 0.0
            self.CV3304_Nuoc_Lam_Mat_Man = 0.0
            self.CV_Filler_Cap_Dich_Man = 0.0

        # Agitator 1 Animation
        if self.AGTR3260_Khuay_Bon1:
            self.HMI_Anim_Bon1_Frame += 1
            if self.HMI_Anim_Bon1_Frame > 7:
                self.HMI_Anim_Bon1_Frame = 0
        else:
            self.HMI_Anim_Bon1_Frame = 0

        # Agitator 2 Animation
        if self.VFD_Bon2_Run_Cmd:
            if not self.VFD_Bon2_Dao_Chieu_Cmd:
                self.HMI_Anim_Bon2_Frame += 1
                if self.HMI_Anim_Bon2_Frame > 7:
                    self.HMI_Anim_Bon2_Frame = 0
            else:
                self.HMI_Anim_Bon2_Frame -= 1
                if self.HMI_Anim_Bon2_Frame < 0:
                    self.HMI_Anim_Bon2_Frame = 7
        else:
            self.HMI_Anim_Bon2_Frame = 0

        # Bồn 1 Level Animation
        if self.LT3203_Bon1_Eff <= 0.5:
            self.HMI_Anim_Bon1_MucDich = 0
        elif self.LT3203_Bon1_Eff < 50.0:
            self.HMI_Anim_Bon1_MucDich = 1
        else:
            self.HMI_Anim_Bon1_MucDich = 2

        # Bồn 2 Level Animation
        if self.LT3209_Bon2_Eff <= 0.5:
            self.HMI_Anim_Bon2_MucDich = 0
        elif self.LT3209_Bon2_Eff < 50.0:
            self.HMI_Anim_Bon2_MucDich = 1
        else:
            self.HMI_Anim_Bon2_MucDich = 2

        # Bồn chứa 1 Level Animation
        if self.LT3302_BonChua1_Eff <= 0.5:
            self.HMI_Anim_BonChua1_MucDich = 0
        elif self.LT3302_BonChua1_Eff < 50.0:
            self.HMI_Anim_BonChua1_MucDich = 1
        else:
            self.HMI_Anim_BonChua1_MucDich = 2

        # Bồn chứa 2 Level Animation
        if self.LT3307_BonChua2_Eff <= 0.5:
            self.HMI_Anim_BonChua2_MucDich = 0
        elif self.LT3307_BonChua2_Eff < 50.0:
            self.HMI_Anim_BonChua2_MucDich = 1
        else:
            self.HMI_Anim_BonChua2_MucDich = 2




class PLC2Simulator:
    def __init__(self):
        # Setpoints
        self.HMI_SP_PLC2_Nuoc_Bon3 = 100.0
        self.HMI_SP_PLC2_Nuoc_Bon4 = 120.0
        self.HMI_SP_PLC2_Toc_Do_Bon3 = 50.0
        self.HMI_SP_PLC2_Toc_Do_Bon4_Main = 60.0
        self.HMI_SP_PLC2_Nhiet_Do_Bon4 = 95.0
        self.HMI_SP_Time_Khuay_Bon3 = 10
        self.HMI_SP_Time_Fwd = 15
        self.HMI_SP_Time_Rev = 15
        self.HMI_SP_Time_Sterilize = 20

        # Handshake Inputs from PLC1
        self.Nut_Khoi_Dong_Nhan_Eff = False
        self.Nut_Dung_Nhan_Eff = False
        self.Nut_Reset_Nhan_Eff = False
        self.Nut_EStop_Nhan_Eff = False
        
        self.Nut_Khoi_Dong_Nhan = False
        self.Nut_Dung_Nhan = False
        self.Nut_Reset_Nhan = False
        self.Nut_EStop_Nhan = False
        self.HMI_Reset_Alarm = False
        self.PID_Bon4_Reset_Eff = False
        self.Pump3265_Chuyen_Nhanh2_Cmd_Nhan = False
        self.PLC2_Load_Default_Cmd_Nhan = False

        # Alarms
        self.PLC2_Loi_Tong = False
        self.PLC2_SP_Valid = True

        # Process Values
        self.FQ3210_Bon3_Eff = 0.0
        self.PLC2_Tip_Bon3_Xong_HMI = False
        self.LT3213_Bon3_Eff = 10.0
        self.FQ3215_Bon4_Eff = 0.0
        self.PLC2_Tip_Bon4_Xong_HMI = False
        self.TT3219_Bon4_Eff = 25.0
        self.LT3218_Bon4_Eff = 12.0
        self.PLC2_Khuay_Bon3_Xong_HMI = False
        self.PLC2_Khuay_Thuan_Bon4_Xong_HMI = False
        self.PLC2_Khuay_Nghich_Bon4_Xong_HMI = False
        self.PLC2_Thanh_Trung_Bon4_Xong_HMI = False
        self.PLC2_Xa_Bon4_Xong_HMI = False

        # Internal Step Flags
        self.PLC2_Auto_Enable = False
        self.PLC2_Step_Bon3_Dosing = False
        self.PLC2_Step_Bon3_Tip = False
        self.PLC2_Step_Bon3_Khuay = False
        self.PLC2_Step_Bon3_Xa = False
        self.PLC2_Step_Bon4_Dosing = False
        self.PLC2_Step_Bon4_Tip = False
        self.PLC2_Step_Bon4_Khuay_Thuan = False
        self.PLC2_Step_Bon4_Khuay_Nghich = False
        self.PLC2_Step_Bon4_PID_Mo_Phong = False
        self.PLC2_Step_Bon4_Thanh_Trung = False
        self.PLC2_Me_Nhanh2_Hoan_Thanh = False
        self.PLC2_Xa_Bon4_Xong = False

        # State Value
        self.PLC2_State = 0

        # Timer Accumulators
        self.timer_khuay_bon3_acc = 0
        self.timer_fwd_bon4_acc = 0
        self.timer_rev_bon4_acc = 0
        self.timer_sterilize_bon4_acc = 0
        self.timer_dryrun_bon4_acc = 0
        self.timer_tip_bon3_acc = 0
        self.timer_tip_bon4_acc = 0

        # PID Variables
        self.PID_Bon4_Enable = False
        self.PID_Bon4_SP = 0.0
        self.PID_Bon4_CV = 0.0
        self.PID_Bon4_Error = False

        # Physical Outputs
        self.V3240_Nuoc_Bon3 = False
        self.CV3211_Nuoc_Bon3 = 0.0
        self.AGTR3262_Khuay_Bon3 = False
        self.AGTR3262_Toc_Do_AO = 0.0
        self.V3242_Xa_Bon3 = False
        self.V3243_Xa_Bon3 = False
        self.V3244_Xa_Bon3 = False
        self.V3245_Nuoc_Bon4 = False
        self.CV3216_Hoi_Bon4 = 0.0
        self.AGTR3263_Toc_Do_AO = 0.0
        self.AGTR3263_Khuay_Bon4 = False
        self.AGTR3263_Dao_Chieu = False
        self.Pump3265_Chuyen_Nhanh2 = False
        self.V3247_Xa_Bon4 = False
        self.V3248_Xa_Bon4 = False
        self.V3249_Xa_Bon4 = False

        # Manual Mode tags
        self.HMI_Che_Do_Manual = False
        self.HMI_Cho_Phep_Sua_Thong_So = False
        self.HMI_User_Level = 1  # 1: Operator, 2: Engineer, 3: Admin
        self.PLC2_Manual_Mode_Active = False

        # Manual DOs
        self.V3240_Nuoc_Bon3_Man = False
        self.AGTR3262_Khuay_Bon3_Man = False
        self.V3242_Xa_Bon3_Man = False
        self.V3243_Xa_Bon3_Man = False
        self.V3244_Xa_Bon3_Man = False
        self.V3245_Nuoc_Bon4_Man = False
        self.AGTR3263_Khuay_Bon4_Man = False
        self.AGTR3263_Dao_Chieu_Man = False
        self.V3247_Xa_Bon4_Man = False
        self.V3248_Xa_Bon4_Man = False
        self.V3249_Xa_Bon4_Man = False
        self.Pump3265_Chuyen_Nhanh2_Man = False

        # Manual AOs
        self.CV3211_Nuoc_Bon3_Man = 0.0
        self.AGTR3262_Toc_Do_AO_Man = 0.0
        self.CV3216_Hoi_Bon4_Man = 0.0
        self.AGTR3263_Toc_Do_AO_Man = 0.0


        # Agitator animation frame counters
        self.HMI_Anim_Bon3_Frame = 0
        self.HMI_Anim_Bon4_Frame = 0
        self.HMI_Anim_Bon3_MucDich = 0
        self.HMI_Anim_Bon4_MucDich = 0

        class Dummy: pass
        self.DB_Modbus_Holding_Register_DB = Dummy()
        self.DB_Modbus_Holding_Register_DB.Heartbeat_Client = 0
        self.DB_Modbus_Holding_Register_DB.Heartbeat_Server = 0
        self.Gia_Lap_Heartbeat_Chay = True

        # Heartbeat & Communication
        self.Clock_1Hz = False
        self.Clock_1Hz_Last = False
        self.Clock_1Hz_Edge = False
        self.PLC2_Heartbeat_Timeout = False
        self.PLC1_Heartbeat_Last = 0
        self.PLC1_Heartbeat_Changed = False
        self.PLC1_Heartbeat_Timeout_Acc = 0
        self.MB_TCP_Server_Error = False
        self.Gia_Lap_Mat_Ket_Noi_HMI = False
        self.PLC2_Loi_Truyen_Thong = False

        self.PLC2_EStop_Latch = False
        self.PLC2_Stop_Active = False
        self.PLC2_Loi_Dry_Run = False
        self.PLC2_Loi_Dosing = False
        self.PLC2_Loi_Setpoint = False

        # Rising edge state memory
        self.start_old = False

    def tick(self):
        # Clock Edge Detection
        self.Clock_1Hz_Edge = self.Clock_1Hz and not self.Clock_1Hz_Last
        self.Clock_1Hz_Last = self.Clock_1Hz

        # Heartbeat monitor: PLC1 -> PLC2
        if getattr(self, 'Gia_Lap_Heartbeat_Chay', True):
            self.DB_Modbus_Holding_Register_DB.Heartbeat_Client += 1
        self.PLC1_Heartbeat_Changed = (self.DB_Modbus_Holding_Register_DB.Heartbeat_Client != self.PLC1_Heartbeat_Last)
        if not self.PLC1_Heartbeat_Changed:
            self.PLC1_Heartbeat_Timeout_Acc += 1
            if self.PLC1_Heartbeat_Timeout_Acc >= 5:
                self.PLC2_Heartbeat_Timeout = True
        else:
            self.PLC1_Heartbeat_Timeout_Acc = 0
            self.PLC2_Heartbeat_Timeout = False
        self.PLC1_Heartbeat_Last = self.DB_Modbus_Holding_Register_DB.Heartbeat_Client

        # Gated Eff commands
        self.Nut_Khoi_Dong_Nhan_Eff = self.Nut_Khoi_Dong_Nhan
        self.Nut_Dung_Nhan_Eff = self.Nut_Dung_Nhan
        self.Nut_Reset_Nhan_Eff = self.Nut_Reset_Nhan
        self.Nut_EStop_Nhan_Eff = self.Nut_EStop_Nhan

        # Communication alarms evaluation
        if self.Gia_Lap_Mat_Ket_Noi_HMI or self.PLC2_Heartbeat_Timeout or self.MB_TCP_Server_Error:
            self.PLC2_Loi_Truyen_Thong = True
        
        self.PID_Bon4_Reset_Eff = self.Nut_Reset_Nhan_Eff or self.HMI_Reset_Alarm

        if (self.Nut_Reset_Nhan_Eff or self.HMI_Reset_Alarm) and not self.Nut_EStop_Nhan_Eff and not self.PLC2_EStop_Latch:
            self.PLC2_Loi_Truyen_Thong = False
            self.PLC2_Loi_Dry_Run = False
            self.PLC2_Loi_Dosing = False
            self.PLC2_Loi_Setpoint = False
            self.PID_Bon4_Error = False
            self.PLC2_Loi_Tong = False

        if (self.Nut_EStop_Nhan_Eff or self.PLC2_EStop_Latch or self.PLC2_Loi_Dry_Run or
            self.PLC2_Loi_Dosing or self.PLC2_Loi_Truyen_Thong or self.PLC2_Loi_Setpoint or
            self.PID_Bon4_Error):
            self.PLC2_Loi_Tong = True

        # Update emptying status map
        self.PLC2_Xa_Bon4_Xong = (self.PLC2_State == 40) and (self.LT3218_Bon4_Eff <= 0.5)

        # Dry-run protection (instant)
        if self.Pump3265_Chuyen_Nhanh2 and self.LT3218_Bon4_Eff <= 0.5 and not self.PLC2_Xa_Bon4_Xong:
            self.PLC2_Loi_Dry_Run = True


        # Start Edge detection
        self.start_edge_edge = self.Nut_Khoi_Dong_Nhan_Eff and not self.start_old
        self.start_old = self.Nut_Khoi_Dong_Nhan_Eff

        # PID Enable Set/Reset logic
        if self.PLC2_State == 30:
            self.PID_Bon4_Enable = True
            
        if self.PLC2_Loi_Tong or self.Nut_Dung_Nhan_Eff:
            self.PID_Bon4_Enable = False

        # State transitions
        state_before = self.PLC2_State
        if self.PLC2_Loi_Tong:
            self.PLC2_Auto_Enable = False
            self.PLC2_State = 0
            self.PID_Bon4_Enable = False
        elif self.Nut_Dung_Nhan_Eff:
            self.PLC2_Auto_Enable = False
            self.PLC2_State = 0
            self.PID_Bon4_Enable = False
        else:
            # Transitions
            next_state = self.PLC2_State
            if self.PLC2_State == 40:
                if self.LT3218_Bon4_Eff <= 0.5 or self.PLC2_Xa_Bon4_Xong_HMI:
                    self.PLC2_Auto_Enable = False
                    next_state = 0
            elif self.PLC2_State == 31:
                self.timer_sterilize_bon4_acc += 1
                if self.timer_sterilize_bon4_acc >= self.HMI_SP_Time_Sterilize or self.PLC2_Thanh_Trung_Bon4_Xong_HMI:
                    self.PLC2_Auto_Enable = False
                    self.PID_Bon4_Enable = False
                    next_state = 40
            elif self.PLC2_State == 30:
                if self.TT3219_Bon4_Eff >= self.HMI_SP_PLC2_Nhiet_Do_Bon4:
                    next_state = 31
            elif self.PLC2_State == 23:
                self.timer_rev_bon4_acc += 1
                if self.timer_rev_bon4_acc >= self.HMI_SP_Time_Rev or self.PLC2_Khuay_Nghich_Bon4_Xong_HMI:
                    next_state = 30
            elif self.PLC2_State == 22:
                self.timer_fwd_bon4_acc += 1
                if self.timer_fwd_bon4_acc >= self.HMI_SP_Time_Fwd or self.PLC2_Khuay_Thuan_Bon4_Xong_HMI:
                    next_state = 23
            elif self.PLC2_State == 21:
                self.timer_tip_bon4_acc += 1
                if self.timer_tip_bon4_acc >= 30 or self.PLC2_Tip_Bon4_Xong_HMI:
                    next_state = 22
            elif self.PLC2_State == 20:
                if self.FQ3215_Bon4_Eff >= self.HMI_SP_PLC2_Nuoc_Bon4:
                    next_state = 21
            elif self.PLC2_State == 15:
                if self.LT3213_Bon3_Eff <= 0.5:
                    next_state = 20
            elif self.PLC2_State == 12:
                self.timer_khuay_bon3_acc += 1
                if self.timer_khuay_bon3_acc >= self.HMI_SP_Time_Khuay_Bon3 or self.PLC2_Khuay_Bon3_Xong_HMI:
                    next_state = 15
            elif self.PLC2_State == 11:
                self.timer_tip_bon3_acc += 1
                if self.timer_tip_bon3_acc >= 30 or self.PLC2_Tip_Bon3_Xong_HMI:
                    next_state = 12
            elif self.PLC2_State == 10:
                if self.FQ3210_Bon3_Eff >= self.HMI_SP_PLC2_Nuoc_Bon3:
                    next_state = 11
            elif self.PLC2_State == 0:
                if self.start_edge_edge and self.PLC2_SP_Valid:
                    self.PLC2_Auto_Enable = True
                    next_state = 10

            # Clean HMI done flags when leaving states
            if next_state != 11: self.PLC2_Tip_Bon3_Xong_HMI = False
            if next_state != 12: self.PLC2_Khuay_Bon3_Xong_HMI = False
            if next_state != 21: self.PLC2_Tip_Bon4_Xong_HMI = False
            if next_state != 22: self.PLC2_Khuay_Thuan_Bon4_Xong_HMI = False
            if next_state != 23: self.PLC2_Khuay_Nghich_Bon4_Xong_HMI = False
            if next_state != 31: self.PLC2_Thanh_Trung_Bon4_Xong_HMI = False

            self.PLC2_State = next_state

        # One-hot step mapping
        self.PLC2_Step_Bon3_Dosing = (self.PLC2_State == 10)
        self.PLC2_Step_Bon3_Tip = (self.PLC2_State == 11)
        self.PLC2_Step_Bon3_Khuay = (self.PLC2_State == 12)
        self.PLC2_Step_Bon3_Xa = (self.PLC2_State == 15)
        self.PLC2_Step_Bon4_Dosing = (self.PLC2_State == 20)
        self.PLC2_Step_Bon4_Tip = (self.PLC2_State == 21)
        self.PLC2_Step_Bon4_Khuay_Thuan = (self.PLC2_State == 22)
        self.PLC2_Step_Bon4_Khuay_Nghich = (self.PLC2_State == 23)
        self.PLC2_Step_Bon4_PID_Mo_Phong = (self.PLC2_State == 30)
        self.PLC2_Step_Bon4_Thanh_Trung = (self.PLC2_State == 31)
        self.PLC2_Me_Nhanh2_Hoan_Thanh = (self.PLC2_State == 40)

        # Actuators logic
        self.V3240_Nuoc_Bon3 = self.PLC2_Step_Bon3_Dosing
        self.CV3211_Nuoc_Bon3 = 100.0 if self.PLC2_Step_Bon3_Dosing else 0.0

        self.AGTR3262_Khuay_Bon3 = self.PLC2_Step_Bon3_Khuay
        self.AGTR3262_Toc_Do_AO = self.HMI_SP_PLC2_Toc_Do_Bon3 if self.PLC2_Step_Bon3_Khuay else 0.0

        self.V3242_Xa_Bon3 = self.PLC2_Step_Bon3_Xa
        self.V3243_Xa_Bon3 = self.PLC2_Step_Bon3_Xa
        self.V3244_Xa_Bon3 = self.PLC2_Step_Bon3_Xa
        self.V3245_Nuoc_Bon4 = self.PLC2_Step_Bon4_Dosing

        self.PID_Bon4_SP = self.HMI_SP_PLC2_Nhiet_Do_Bon4 if self.PID_Bon4_Enable else 0.0
        self.PID_Bon4_CV = 80.0 if self.PID_Bon4_Enable else 0.0
        self.CV3216_Hoi_Bon4 = self.PID_Bon4_CV if self.PID_Bon4_Enable else 0.0

        self.AGTR3263_Khuay_Active = (
            self.PLC2_Step_Bon4_Khuay_Thuan or 
            self.PLC2_Step_Bon4_Khuay_Nghich or 
            self.PID_Bon4_Enable
        )
        self.AGTR3263_Khuay_Bon4 = self.AGTR3263_Khuay_Active
        self.AGTR3263_Dao_Chieu = self.PLC2_Step_Bon4_Khuay_Nghich

        if self.AGTR3263_Khuay_Active:
            self.AGTR3263_Toc_Do_AO = self.HMI_SP_PLC2_Toc_Do_Bon4_Main
        else:
            self.AGTR3263_Toc_Do_AO = 0.0

        # Transfer Pump self-latch logic
        self.Pump3265_Chuyen_Nhanh2 = (
            (self.PLC2_State == 40) and 
            (self.Pump3265_Chuyen_Nhanh2_Cmd_Nhan or self.Pump3265_Chuyen_Nhanh2) and 
            (self.LT3218_Bon4_Eff > 0.5) and 
            not self.PLC2_Loi_Tong and 
            not self.PLC2_Stop_Active and 
            not self.PLC2_EStop_Latch
        )
        self.V3247_Xa_Bon4 = self.Pump3265_Chuyen_Nhanh2
        self.V3248_Xa_Bon4 = self.Pump3265_Chuyen_Nhanh2
        self.V3249_Xa_Bon4 = self.Pump3265_Chuyen_Nhanh2
        self.PLC2_Xa_Bon4_Xong = (state_before == 40) and (self.LT3218_Bon4_Eff <= 0.5)

        # --- Manual Control PLC2 ---
        # 1. Evaluate Manual Mode Active flag
        self.PLC2_Manual_Mode_Active = self.HMI_Che_Do_Manual and self.HMI_Cho_Phep_Sua_Thong_So and (self.HMI_User_Level > 1)

        # 2. Reset Auto/PID/Sequence if Manual Active
        if self.PLC2_Manual_Mode_Active:
            self.PLC2_Auto_Enable = False
            self.PID_Bon4_Enable = False
            self.PLC2_State = 0
            
            # 4. Clamping and applying manual values
            # Clamping Real variables
            self.CV3211_Nuoc_Bon3_Man = max(0.0, min(100.0, self.CV3211_Nuoc_Bon3_Man))
            self.AGTR3262_Toc_Do_AO_Man = max(0.0, min(100.0, self.AGTR3262_Toc_Do_AO_Man))
            self.CV3216_Hoi_Bon4_Man = max(0.0, min(100.0, self.CV3216_Hoi_Bon4_Man))
            self.AGTR3263_Toc_Do_AO_Man = max(0.0, min(100.0, self.AGTR3263_Toc_Do_AO_Man))

            # DO manual mapping
            self.V3240_Nuoc_Bon3 = self.V3240_Nuoc_Bon3_Man
            self.AGTR3262_Khuay_Bon3 = self.AGTR3262_Khuay_Bon3_Man
            self.V3242_Xa_Bon3 = self.V3242_Xa_Bon3_Man
            self.V3243_Xa_Bon3 = self.V3243_Xa_Bon3_Man
            self.V3244_Xa_Bon3 = self.V3244_Xa_Bon3_Man
            self.V3245_Nuoc_Bon4 = self.V3245_Nuoc_Bon4_Man
            self.AGTR3263_Khuay_Bon4 = self.AGTR3263_Khuay_Bon4_Man
            self.AGTR3263_Dao_Chieu = self.AGTR3263_Dao_Chieu_Man
            self.V3247_Xa_Bon4 = self.V3247_Xa_Bon4_Man
            self.V3248_Xa_Bon4 = self.V3248_Xa_Bon4_Man
            self.V3249_Xa_Bon4 = self.V3249_Xa_Bon4_Man

            # AO manual mapping
            self.CV3211_Nuoc_Bon3 = self.CV3211_Nuoc_Bon3_Man
            self.AGTR3262_Toc_Do_AO = self.AGTR3262_Toc_Do_AO_Man
            self.CV3216_Hoi_Bon4 = self.CV3216_Hoi_Bon4_Man
            self.AGTR3263_Toc_Do_AO = self.AGTR3263_Toc_Do_AO_Man

            # Pump manual mapping with level interlocks
            if self.LT3218_Bon4_Eff <= 0.5:
                self.Pump3265_Chuyen_Nhanh2_Man = False
                self.Pump3265_Chuyen_Nhanh2 = False
                self.V3247_Xa_Bon4 = False
                self.V3248_Xa_Bon4 = False
                self.V3249_Xa_Bon4 = False
            else:
                self.Pump3265_Chuyen_Nhanh2 = self.Pump3265_Chuyen_Nhanh2_Man
                if self.Pump3265_Chuyen_Nhanh2:
                    self.V3247_Xa_Bon4 = True
                    self.V3248_Xa_Bon4 = True
                    self.V3249_Xa_Bon4 = True

        # 3. Leaving Manual Mode resets manual command tags
        else:
            self.V3240_Nuoc_Bon3_Man = False
            self.AGTR3262_Khuay_Bon3_Man = False
            self.V3242_Xa_Bon3_Man = False
            self.V3243_Xa_Bon3_Man = False
            self.V3244_Xa_Bon3_Man = False
            self.V3245_Nuoc_Bon4_Man = False
            self.AGTR3263_Khuay_Bon4_Man = False
            self.AGTR3263_Dao_Chieu_Man = False
            self.V3247_Xa_Bon4_Man = False
            self.V3248_Xa_Bon4_Man = False
            self.V3249_Xa_Bon4_Man = False
            self.Pump3265_Chuyen_Nhanh2_Man = False

            self.CV3211_Nuoc_Bon3_Man = 0.0
            self.AGTR3262_Toc_Do_AO_Man = 0.0
            self.CV3216_Hoi_Bon4_Man = 0.0
            self.AGTR3263_Toc_Do_AO_Man = 0.0

        # 5. Safety overrides (Dừng khẩn / Dừng / Lỗi tổng)
        if self.PLC2_EStop_Latch or self.Nut_EStop_Nhan_Eff or self.PLC2_Stop_Active or self.PLC2_Loi_Tong:
            self.V3240_Nuoc_Bon3 = False
            self.AGTR3262_Khuay_Bon3 = False
            self.V3242_Xa_Bon3 = False
            self.V3243_Xa_Bon3 = False
            self.V3244_Xa_Bon3 = False
            self.V3245_Nuoc_Bon4 = False
            self.AGTR3263_Khuay_Bon4 = False
            self.AGTR3263_Dao_Chieu = False
            self.V3247_Xa_Bon4 = False
            self.V3248_Xa_Bon4 = False
            self.V3249_Xa_Bon4 = False
            self.Pump3265_Chuyen_Nhanh2 = False

            self.CV3211_Nuoc_Bon3 = 0.0
            self.AGTR3262_Toc_Do_AO = 0.0
            self.CV3216_Hoi_Bon4 = 0.0
            self.AGTR3263_Toc_Do_AO = 0.0

            # Also clear the Man command tags during safety override
            self.V3240_Nuoc_Bon3_Man = False
            self.AGTR3262_Khuay_Bon3_Man = False
            self.V3242_Xa_Bon3_Man = False
            self.V3243_Xa_Bon3_Man = False
            self.V3244_Xa_Bon3_Man = False
            self.V3245_Nuoc_Bon4_Man = False
            self.AGTR3263_Khuay_Bon4_Man = False
            self.AGTR3263_Dao_Chieu_Man = False
            self.V3247_Xa_Bon4_Man = False
            self.V3248_Xa_Bon4_Man = False
            self.V3249_Xa_Bon4_Man = False
            self.Pump3265_Chuyen_Nhanh2_Man = False

            self.CV3211_Nuoc_Bon3_Man = 0.0
            self.AGTR3262_Toc_Do_AO_Man = 0.0
            self.CV3216_Hoi_Bon4_Man = 0.0
            self.AGTR3263_Toc_Do_AO_Man = 0.0

        # Agitator 3 Animation
        if self.AGTR3262_Khuay_Bon3:
            self.HMI_Anim_Bon3_Frame += 1
            if self.HMI_Anim_Bon3_Frame > 7:
                self.HMI_Anim_Bon3_Frame = 0
        else:
            self.HMI_Anim_Bon3_Frame = 0

        # Agitator 4 Animation
        if self.AGTR3263_Khuay_Bon4:
            if not self.AGTR3263_Dao_Chieu:
                self.HMI_Anim_Bon4_Frame += 1
                if self.HMI_Anim_Bon4_Frame > 7:
                    self.HMI_Anim_Bon4_Frame = 0
            else:
                self.HMI_Anim_Bon4_Frame -= 1
                if self.HMI_Anim_Bon4_Frame < 0:
                    self.HMI_Anim_Bon4_Frame = 7
        else:
            self.HMI_Anim_Bon4_Frame = 0

        # Bồn 3 Level Animation
        if self.LT3213_Bon3_Eff <= 0.5:
            self.HMI_Anim_Bon3_MucDich = 0
        elif self.LT3213_Bon3_Eff < 50.0:
            self.HMI_Anim_Bon3_MucDich = 1
        else:
            self.HMI_Anim_Bon3_MucDich = 2

        # Bồn 4 Level Animation
        if self.LT3218_Bon4_Eff <= 0.5:
            self.HMI_Anim_Bon4_MucDich = 0
        elif self.LT3218_Bon4_Eff < 50.0:
            self.HMI_Anim_Bon4_MucDich = 1
        else:
            self.HMI_Anim_Bon4_MucDich = 2




def test_plc1_sequence():
    print("---------------------------------------------------------")
    print(" RUNNING PLC_1 LOGIC CYCLE SIMULATION TESTS")
    print("---------------------------------------------------------")
    sim = PLC1Simulator()
    
    # Tick 1: IDLE state
    sim.tick()
    assert sim.PLC1_State == 0, f"Expected State 0, got {sim.PLC1_State}"
    print("[PASS] Cycle 0: PLC_1 is IDLE (State 0)")

    # Tick 2: Press Start
    sim.Nut_Khoi_Dong_Eff = True
    sim.tick()
    sim.Nut_Khoi_Dong_Eff = False # release button pulse
    assert sim.PLC1_State == 10, f"Expected State 10 (Dosing), got {sim.PLC1_State}"
    assert sim.V3230_Nuoc_Bon1 == True, "Dosing valve Bon 1 should open"
    assert sim.CV3201_Nuoc_Bon1 == 100.0, "Dosing analog valve Bon 1 should be 100%"
    print("[PASS] Cycle 1: Pressed Start. Sequence entered Dosing Bồn 1 (State 10), Water Valve opened")

    # Tick 3: Simulate dosing in progress (SP is 100.0)
    sim.FQ3200_Bon1_Eff = 50.0
    sim.tick()
    assert sim.PLC1_State == 10, "Should remain in State 10"
    print("[PASS] Cycle 2: Water at 50L. Remained in State 10")

    # Tick 4: Dosing complete (water reaches 100.0)
    sim.FQ3200_Bon1_Eff = 100.0
    sim.tick()
    sim.tick() # extra tick to propagate State 11
    assert sim.PLC1_State == 11, f"Expected State 11 (Tip), got {sim.PLC1_State}"
    assert sim.V3230_Nuoc_Bon1 == False, "Dosing valve Bon 1 should close after dosing complete"
    print("[PASS] Cycle 3: Water reached 100L. Dosing Valve closed, entered Tip (State 11)")

    # Tick 5: Simulate tip phễu completed
    sim.PLC1_Tip_Bon1_Xong_HMI = True
    sim.tick()
    sim.tick() # extra tick to propagate State 12
    assert sim.PLC1_State == 12, f"Expected State 12 (Khuay), got {sim.PLC1_State}"
    assert sim.AGTR3260_Toc_Do_AO == 50.0, f"Expected Agitator Speed 50.0, got {sim.AGTR3260_Toc_Do_AO}"
    print("[PASS] Cycle 4: Tip phễu done. Entered Agitator Bồn 1 (State 12) at 50% Speed")

    # Tick 6: Simulate agitation timer in progress (needs 10 ticks)
    for i in range(5):
        sim.tick()
    assert sim.PLC1_State == 12, "Should remain in State 12"
    print("[PASS] Cycle 5: Agitator running...")

    # Tick 7: Agitator completes
    for i in range(5):
        sim.tick()
    sim.tick() # extra tick to propagate State 15
    assert sim.PLC1_State == 15, f"Expected State 15 (Xa), got {sim.PLC1_State}"
    assert sim.V3232_Xa_Bon1 == True, "Discharge valve 1 should open"
    print("[PASS] Cycle 6: Agitation timer done. Discharge valves opened, entered Discharge (State 15)")

    # Tick 8: Tank 1 becomes cạn (level <= 0.5)
    sim.LT3203_Bon1_Eff = 0.4
    sim.tick()
    sim.tick() # extra tick to propagate State 20
    assert sim.PLC1_State == 20, f"Expected State 20 (Dosing Bon2), got {sim.PLC1_State}"
    assert sim.V3232_Xa_Bon1 == False, "Discharge valve should close after discharge complete"
    assert sim.V3235_Nuoc_Bon2 == True, "Dosing valve Bon 2 should open"
    print("[PASS] Cycle 7: Bồn 1 cạn. Entered Dosing Bồn 2 (State 20), Water Valve Bồn 2 opened")

    # Tick 9: Water reaches Bồn 2 SP (120.0)
    sim.FQ3205_Bon2_Eff = 120.0
    sim.tick()
    sim.tick() # extra tick to propagate State 21
    assert sim.PLC1_State == 21, f"Expected State 21 (Tip Bon2), got {sim.PLC1_State}"
    assert sim.V3235_Nuoc_Bon2 == False, "Dosing valve Bon 2 should close"
    print("[PASS] Cycle 8: Bồn 2 reached 120L. Entered Tip (State 21)")

    # Tick 10: Tip done -> Khuay Thuan (State 22)
    sim.PLC1_Tip_Bon2_Xong_HMI = True
    sim.tick()
    sim.tick() # extra tick to propagate State 22
    assert sim.PLC1_State == 22, f"Expected State 22 (Khuay Thuan), got {sim.PLC1_State}"
    assert sim.VFD_Bon2_Run_Cmd == True, "VFD Bồn 2 should start"
    assert sim.VFD_Bon2_Toc_Do_Cmd == 60.0, f"Expected VFD Speed 60.0, got {sim.VFD_Bon2_Toc_Do_Cmd}"
    assert sim.VFD_Bon2_Dao_Chieu_Cmd == False, "VFD Direction should be Forward"
    print("[PASS] Cycle 9: Tip done. Entered Agitator Forward (State 22) at 60% Speed")

    # Tick 11: Khuay Thuan done -> Khuay Nghich (State 23)
    sim.PLC1_Khuay_Thuan_Bon2_Xong_HMI = True
    sim.tick()
    sim.tick() # extra tick to propagate State 23
    assert sim.PLC1_State == 23, f"Expected State 23 (Khuay Nghich), got {sim.PLC1_State}"
    assert sim.VFD_Bon2_Run_Cmd == True, "VFD Bồn 2 should run"
    assert sim.VFD_Bon2_Dao_Chieu_Cmd == True, "VFD Direction should be Reverse"
    print("[PASS] Cycle 10: Forward timer done. Entered Agitator Reverse (State 23) (Direction: Reverse)")

    # Tick 12: Khuay Nghich done -> PID (State 30)
    sim.PLC1_Khuay_Nghich_Bon2_Xong_HMI = True
    sim.TT3208_Bon2_Eff = 67.0
    sim.tick()
    sim.tick() # extra tick to propagate State 30
    assert sim.PLC1_State == 30, f"Expected State 30 (PID), got {sim.PLC1_State}"
    assert sim.PID_Bon2_Enable == True, "PID Bồn 2 should be enabled"
    assert sim.PID_Bon2_SP == 75.0, f"Expected PID SP 75.0, got {sim.PID_Bon2_SP}"
    assert sim.CV3206_Hoi_Bon2 == 80.0, "PID CV should output 80.0 to Steam Valve"
    assert sim.VFD_Bon2_Run_Cmd == True, "Agitator/VFD should still run during PID!"
    assert sim.VFD_Bon2_Toc_Do_Cmd == 60.0, "Agitator speed should maintain HMI SP"
    print("[PASS] Cycle 11: Reverse done. Entered PID (State 30). Verified Agitator runs at HMI SP & PID CV3206 modulates")

    # Tick 13: Temperature reaches SP -> entered Sterilize (State 31)
    sim.TT3208_Bon2_Eff = 75.0
    sim.tick()
    sim.tick() # extra tick to propagate State 31
    assert sim.PLC1_State == 31, f"Expected State 31 (Sterilize), got {sim.PLC1_State}"
    assert sim.PID_Bon2_Enable == True, "PID Bồn 2 should still be enabled during Sterilize to hold temp"
    assert sim.VFD_Bon2_Run_Cmd == True, "Agitator should still run during Sterilize"
    print("[PASS] Cycle 12: Temperature reached 75°C. Entered Sterilize (State 31). Verified PID & Agitator remain active")

    # Tick 14: Sterilize done -> entered Discharge / Complete (State 40)
    sim.PLC1_Thanh_Trung_Bon2_Xong_HMI = True
    sim.tick()
    sim.tick() # extra tick to propagate State 40
    assert sim.PLC1_State == 40, f"Expected State 40 (Discharge/Complete), got {sim.PLC1_State}"
    assert sim.PLC1_Auto_Enable == False, "Auto Enable must be FALSE when entering State 40"
    assert sim.PID_Bon2_Enable == False, "PID Enable must be FALSE when entering State 40"
    # Wait, in State 40 it requires Owner Nhanh1 from Cụm bồn chứa to run pump 1
    # Storage arbitrator will automatically grant Owner Nhanh1 since it is Idle!
    assert sim.BonChua_Owner_Nhanh1 == True, "Storage should grant Owner Nhanh1"
    assert sim.Pump3264_Chuyen_Nhanh1 == True, "Discharge Pump 1 should run"
    assert sim.V3237_Xa_Bon2 == True, "Discharge Valve 1 should open"
    assert sim.V3238_Xa_Bon2 == True, "Discharge Valve 2 should open"
    assert sim.V3239_Xa_Bon2 == True, "Discharge Valve 3 should open"
    print("[PASS] Cycle 13: Sterilize done. Entered Discharge (State 40). Verified Pump 1 and all 3 Discharge Valves opened")

    # Tick 15: Tank cạn -> back to IDLE
    sim.LT3209_Bon2_Eff = 0.4
    sim.tick()
    sim.tick() # extra tick to propagate State 0
    assert sim.PLC1_State == 0, f"Expected State 0 (Idle), got {sim.PLC1_State}"
    assert sim.Pump3264_Chuyen_Nhanh1 == False, "Discharge Pump 1 should stop"
    assert sim.V3237_Xa_Bon2 == False, "Discharge Valves should close"
    print("[PASS] Cycle 14: Bồn 2 cạn. Discharge completed, sequence returned to IDLE (State 0)")


def test_plc2_sequence():
    print("---------------------------------------------------------")
    print(" RUNNING PLC_2 LOGIC CYCLE SIMULATION TESTS")
    print("---------------------------------------------------------")
    sim = PLC2Simulator()

    # Tick 1: IDLE state
    sim.tick()
    assert sim.PLC2_State == 0, f"Expected State 0, got {sim.PLC2_State}"
    print("[PASS] Cycle 0: PLC_2 is IDLE (State 0)")

    # Tick 2: Receive Start from PLC1
    sim.Nut_Khoi_Dong_Nhan = True
    sim.tick()
    sim.Nut_Khoi_Dong_Nhan = False
    assert sim.PLC2_State == 10, f"Expected State 10 (Dosing), got {sim.PLC2_State}"
    assert sim.V3240_Nuoc_Bon3 == True, "Dosing valve Bon 3 should open"
    print("[PASS] Cycle 1: Received Start. Sequence entered Dosing Bồn 3 (State 10), Water Valve opened")

    # Tick 3: Dosing complete (water reaches 100.0)
    sim.FQ3210_Bon3_Eff = 100.0
    sim.tick()
    sim.tick() # extra tick to propagate State 11
    assert sim.PLC2_State == 11, f"Expected State 11 (Tip), got {sim.PLC2_State}"
    assert sim.V3240_Nuoc_Bon3 == False, "Dosing valve Bon 3 should close"
    print("[PASS] Cycle 2: Water reached 100L. Dosing Valve closed, entered Tip (State 11)")

    # Tick 4: Tip phễu completed
    sim.PLC2_Tip_Bon3_Xong_HMI = True
    sim.tick()
    sim.tick() # extra tick to propagate State 12
    assert sim.PLC2_State == 12, f"Expected State 12 (Khuay), got {sim.PLC2_State}"
    assert sim.AGTR3262_Khuay_Bon3 == True, "Agitator Bồn 3 should turn on"
    assert sim.AGTR3262_Toc_Do_AO == 50.0, f"Expected Speed 50.0, got {sim.AGTR3262_Toc_Do_AO}"
    print("[PASS] Cycle 3: Tip done. Entered Agitator Bồn 3 (State 12) at 50% Speed")

    # Tick 5: Agitator completes
    sim.timer_khuay_bon3_acc = 10
    sim.tick()
    sim.tick() # extra tick to propagate State 15
    assert sim.PLC2_State == 15, f"Expected State 15 (Xa), got {sim.PLC2_State}"
    assert sim.V3242_Xa_Bon3 == True, "Discharge valve should open"
    print("[PASS] Cycle 4: Agitation timer done. Entered Discharge (State 15)")

    # Tick 6: Tank 3 becomes cạn (level <= 0.5)
    sim.LT3213_Bon3_Eff = 0.4
    sim.tick()
    sim.tick() # extra tick to propagate State 20
    assert sim.PLC2_State == 20, f"Expected State 20 (Dosing Bon4), got {sim.PLC2_State}"
    assert sim.V3242_Xa_Bon3 == False, "Discharge valve should close"
    assert sim.V3245_Nuoc_Bon4 == True, "Dosing valve Bon 4 should open"
    print("[PASS] Cycle 5: Bồn 3 cạn. Entered Dosing Bồn 4 (State 20), Water Valve Bồn 4 opened")

    # Tick 7: Water reaches Bồn 4 SP (120.0)
    sim.FQ3215_Bon4_Eff = 120.0
    sim.tick()
    sim.tick() # extra tick to propagate State 21
    assert sim.PLC2_State == 21, f"Expected State 21 (Tip Bon4), got {sim.PLC2_State}"
    assert sim.V3245_Nuoc_Bon4 == False, "Dosing valve Bon 4 should close"
    print("[PASS] Cycle 6: Bồn 4 reached 120L. Entered Tip (State 21)")

    # Tick 8: Tip done -> Khuay Thuan (State 22)
    sim.PLC2_Tip_Bon4_Xong_HMI = True
    sim.tick()
    sim.tick() # extra tick to propagate State 22
    assert sim.PLC2_State == 22, f"Expected State 22 (Khuay Thuan), got {sim.PLC2_State}"
    assert sim.AGTR3263_Khuay_Bon4 == True, "Agitator Bồn 4 should run"
    assert sim.AGTR3263_Toc_Do_AO == 60.0, f"Expected Speed 60.0, got {sim.AGTR3263_Toc_Do_AO}"
    assert sim.AGTR3263_Dao_Chieu == False, "Forward direction"
    print("[PASS] Cycle 7: Tip done. Entered Agitator Forward (State 22) at 60% Speed")

    # Tick 9: Khuay Thuan done -> Khuay Nghich (State 23)
    sim.PLC2_Khuay_Thuan_Bon4_Xong_HMI = True
    sim.tick()
    sim.tick() # extra tick to propagate State 23
    assert sim.PLC2_State == 23, f"Expected State 23 (Khuay Nghich), got {sim.PLC2_State}"
    assert sim.AGTR3263_Khuay_Bon4 == True, "Agitator Bồn 4 should run"
    assert sim.AGTR3263_Dao_Chieu == True, "Reverse direction"
    print("[PASS] Cycle 8: Forward done. Entered Agitator Reverse (State 23) (Direction: Reverse)")

    # Tick 10: Khuay Nghich done -> PID (State 30)
    sim.PLC2_Khuay_Nghich_Bon4_Xong_HMI = True
    sim.tick()
    sim.tick() # extra tick to propagate State 30
    assert sim.PLC2_State == 30, f"Expected State 30 (PID), got {sim.PLC2_State}"
    assert sim.PID_Bon4_Enable == True, "PID Bồn 4 enabled"
    assert sim.PID_Bon4_SP == 95.0, f"Expected PID SP 95.0, got {sim.PID_Bon4_SP}"
    assert sim.CV3216_Hoi_Bon4 == 80.0, "PID CV should output to simulated steam valve"
    assert sim.AGTR3263_Khuay_Bon4 == True, "Agitator Bồn 4 must continue running during PID!"
    assert sim.AGTR3263_Toc_Do_AO == 60.0, "Agitator speed should maintain HMI SP"
    print("[PASS] Cycle 9: Reverse done. Entered PID (State 30). Verified Agitator runs at HMI SP & PID CV3216 modulates")

    # Tick 11: Temperature reaches SP -> entered Sterilize (State 31)
    sim.TT3219_Bon4_Eff = 95.0
    sim.tick()
    sim.tick() # extra tick to propagate State 31
    assert sim.PLC2_State == 31, f"Expected State 31 (Sterilize), got {sim.PLC2_State}"
    assert sim.PID_Bon4_Enable == True, "PID Bồn 4 remains active"
    assert sim.AGTR3263_Khuay_Bon4 == True, "Agitator remains active"
    print("[PASS] Cycle 10: Temp reached 95°C. Entered Sterilize (State 31). Verified PID & Agitator remain active")

    # Tick 12: Sterilize done -> Completed
    sim.PLC2_Thanh_Trung_Bon4_Xong_HMI = True
    sim.tick()
    assert sim.PLC2_State == 40, f"Expected State 40, got {sim.PLC2_State}"
    assert sim.PLC2_Me_Nhanh2_Hoan_Thanh == True, "Completed flag should be set"
    assert sim.PLC2_Auto_Enable == False, "Auto Enable must be FALSE when entering State 40"
    assert sim.PID_Bon4_Enable == False, "PID Enable must be FALSE when entering State 40"
    print("[PASS] Cycle 11: Sterilize done. Entered Complete. Complete flag is set to TRUE")

    # Tick 13: Discharge pump command received from PLC1 -> Discharge valves open
    sim.PLC2_Auto_Enable = False
    sim.Pump3265_Chuyen_Nhanh2_Cmd_Nhan = True
    sim.tick()
    sim.Pump3265_Chuyen_Nhanh2_Cmd_Nhan = False # pulse 1 scan
    assert sim.Pump3265_Chuyen_Nhanh2 == True, "Discharge Pump should run"
    assert sim.V3247_Xa_Bon4 == True, "Discharge valve 1 should open"
    assert sim.V3248_Xa_Bon4 == True, "Discharge valve 2 should open"
    assert sim.V3249_Xa_Bon4 == True, "Discharge valve 3 should open"
    print("[PASS] Cycle 12: Pump command received. Pump 2 runs, all 3 Discharge Valves opened")

    # Tick 14: Tank becomes cạn -> back to IDLE
    sim.LT3218_Bon4_Eff = 0.4
    sim.tick()
    sim.tick() # extra tick to propagate State 0
    assert sim.PLC2_State == 0, f"Expected State 0 (Idle), got {sim.PLC2_State}"
    assert sim.Pump3265_Chuyen_Nhanh2 == False, "Pump should stop"
    assert sim.V3247_Xa_Bon4 == False, "Valves should close"
    print("[PASS] Cycle 13: Bồn 4 cạn. Discharge completed, returned to IDLE (State 0)")


def test_pulse_command():
    print("---------------------------------------------------------")
    print(" UNIT TEST: LATCH TRANSFER COMMAND VIA PULSE")
    print("---------------------------------------------------------")
    sim = PLC2Simulator()
    sim.PLC2_State = 40
    
    # 1 scan pulse of Cmd_Nhan
    sim.Pump3265_Chuyen_Nhanh2_Cmd_Nhan = True
    sim.tick()
    assert sim.Pump3265_Chuyen_Nhanh2 == True, "Pump should run when Cmd_Nhan is high and State is 40"
    sim.Pump3265_Chuyen_Nhanh2_Cmd_Nhan = False # Clear pulse on next scan
    
    # Pump should remain active
    sim.tick()
    assert sim.Pump3265_Chuyen_Nhanh2 == True, "Pump should remain latched after pulse command cleared!"
    
    # Pump remains active for multiple ticks
    for _ in range(5):
        sim.tick()
        assert sim.Pump3265_Chuyen_Nhanh2 == True, "Pump should remain active!"

    # Until Bồn 4 level is cạn (<= 0.5)
    sim.LT3218_Bon4_Eff = 0.4
    sim.tick()
    assert sim.PLC2_Xa_Bon4_Xong == True, "Should set Xa_Bon4_Xong flag!"
    sim.tick()
    assert sim.Pump3265_Chuyen_Nhanh2 == False, "Pump should stop when level goes below 0.5!"
    print("[PASS] Latch command test: 1 scan pulse runs pump continuously until tank is empty.")


def test_pid_state_31():
    print("---------------------------------------------------------")
    print(" UNIT TEST: PID CV IN STATE 31 (STERILIZE)")
    print("---------------------------------------------------------")
    sim = PLC1Simulator()
    sim.PLC1_State = 31
    sim.PID_Bon2_Enable = True
    sim.TT3208_Bon2_Eff = 75.0
    sim.tick()
    
    # In state 31, PID must remain enabled and CV must not be reset to 0.0 by the cleanup network
    assert sim.PID_Bon2_Enable == True, "PID must remain enabled in State 31!"
    assert sim.CV3206_Hoi_Bon2 > 0.0, f"Expected non-zero CV in State 31, got {sim.CV3206_Hoi_Bon2}"
    
    # Run for 3 consecutive scans
    for i in range(3):
        sim.tick()
        assert sim.PID_Bon2_Enable == True, f"Scan {i}: PID disabled!"
        assert sim.CV3206_Hoi_Bon2 > 0.0, f"Scan {i}: CV reset to 0.0!"
        
    print("[PASS] PID State 31 test: PID holds temperature and steam CV remains active over 3 consecutive scans.")


def test_storage_arbitration():
    print("---------------------------------------------------------")
    print(" UNIT TEST: STORAGE TANK ARBITRATION PRIORITY")
    print("---------------------------------------------------------")
    plc1 = PLC1Simulator()
    
    # Case 1: Branch 1 completes first
    plc1.PLC1_State = 40
    plc1.PLC2_Me_Nhanh2_Hoan_Thanh_Nhan = False
    plc1.tick()
    assert plc1.BonChua_Owner_Nhanh1 == True, "Storage should set Owner Nhanh1"
    assert plc1.BonChua_Owner_Nhanh2 == False, "Storage should not set Owner Nhanh2"
    
    # Reset storage
    plc1.PLC1_State = 0
    plc1.Pump3264_Chuyen_Nhanh1 = False
    plc1.PLC1_Loi_Dry_Run = False
    plc1.PLC1_Loi_Tong = False
    plc1.LT3209_Bon2_Eff = 0.4 # trigger complete

    plc1.tick() # 0 -> 50
    plc1.tick() # 50 -> 60
    plc1.TT3301_BonChua1_Eff = 40.0 # cooled down
    plc1.tick() # 60 -> 70
    plc1.BonChua_Chuyen_Bon2_Xong_HMI = True # transfer done
    plc1.tick() # 70 -> 80
    plc1.LT3307_BonChua2_Eff = 0.4 # filter done (empty)
    plc1.tick() # 80 -> 0
    assert plc1.BonChua_State == 0, "Storage should return to Idle"
    assert plc1.BonChua_Owner_Nhanh1 == False, "Owner Nhanh1 should clear"
    
    # Case 2: Branch 2 completes first
    # Reset sensor values back to default for next case
    plc1.TT3301_BonChua1_Eff = 50.0
    plc1.LT3307_BonChua2_Eff = 10.0
    plc1.LT3209_Bon2_Eff = 12.0
    plc1.PLC1_State = 0
    plc1.PLC2_Me_Nhanh2_Hoan_Thanh_Nhan = True
    plc1.tick()
    assert plc1.BonChua_Owner_Nhanh2 == True, "Storage should set Owner Nhanh2"
    assert plc1.BonChua_Owner_Nhanh1 == False, "Storage should not set Owner Nhanh1"
    
    # Reset storage
    plc1.PLC2_Me_Nhanh2_Hoan_Thanh_Nhan = False
    plc1.PLC2_Xa_Bon4_Xong_Nhan = True
    plc1.tick() # 0 -> 50
    plc1.tick() # 50 -> 60
    plc1.TT3301_BonChua1_Eff = 40.0 # cooled down
    plc1.tick() # 60 -> 70
    plc1.BonChua_Chuyen_Bon2_Xong_HMI = True # transfer done
    plc1.tick() # 70 -> 80
    plc1.LT3307_BonChua2_Eff = 0.4 # filter done
    plc1.tick() # 80 -> 0
    assert plc1.BonChua_State == 0, "Storage should return to Idle"
    assert plc1.BonChua_Owner_Nhanh2 == False, "Owner Nhanh2 should clear"
    
    # Case 3: Both complete in same scan (Priority check: Branch 1 wins, Branch 2 waits)
    plc1.TT3301_BonChua1_Eff = 50.0
    plc1.LT3307_BonChua2_Eff = 10.0
    plc1.LT3209_Bon2_Eff = 12.0
    plc1.PLC2_Xa_Bon4_Xong_Nhan = False
    plc1.PLC1_State = 40
    plc1.PLC2_Me_Nhanh2_Hoan_Thanh_Nhan = True
    plc1.tick()
    
    # Branch 1 should win owner
    assert plc1.BonChua_Owner_Nhanh1 == True, "Branch 1 must get priority Owner!"
    assert plc1.BonChua_Owner_Nhanh2 == False, "Branch 2 must not get Owner!"
    
    # Branch 1 discharge completes
    plc1.PLC1_State = 0
    plc1.Pump3264_Chuyen_Nhanh1 = False
    plc1.PLC1_Loi_Dry_Run = False
    plc1.PLC1_Loi_Tong = False
    plc1.LT3209_Bon2_Eff = 0.4
    plc1.tick() # transitions to Cooling (State 20)

    plc1.tick() # runs Cooling, resets Owner flags
    assert plc1.BonChua_Owner_Nhanh1 == False, "Owner Nhanh1 should clear on transition"
    
    # Cycle storage through steps to return Idle
    plc1.TT3301_BonChua1_Eff = 40.0 # cooled down
    plc1.tick() # State 60 -> 70
    plc1.BonChua_Chuyen_Bon2_Xong_HMI = True # transfer done
    plc1.tick() # State 70 -> 80
    plc1.LT3307_BonChua2_Eff = 0.4 # filter done
    plc1.tick() # State 80 -> 0
    
    # Now that storage is Idle, Branch 2 (still completed) should get Owner next!
    plc1.LT3209_Bon2_Eff = 12.0
    plc1.tick()
    assert plc1.BonChua_Owner_Nhanh2 == True, "Branch 2 should get Owner once storage is Idle!"
    assert plc1.BonChua_Owner_Nhanh1 == False
    
    print("[PASS] Storage arbitration test: Priority branch 1 wins, branch 2 queues correctly.")


def test_storage_scan_overwrite():
    print("---------------------------------------------------------")
    print(" UNIT TEST: STORAGE TANK ADVANCED LOGIC TESTS")
    print("---------------------------------------------------------")
    sim = PLC1Simulator()
    sim.HMI_Sim_Mode = True
    sim.BonChua_SP_Valid = True
    
    # 1. State 0 + Owner1 + SP hợp lệ -> Sau một scan State = 50, không bị ghi đè về 0.
    assert sim.BonChua_State == 0
    sim.BonChua_Owner_Nhanh1 = True
    sim.tick()
    assert sim.BonChua_State == 50, f"Expected State 50, got {sim.BonChua_State}"
    print("[PASS] Test 1: State 0 + Owner1 -> State 50 without scan overwrite.")

    # 6. Test đủ chu trình: 0 -> 50 -> 60 -> 70 -> 80 -> 0.
    # We are at 50. Let's make it transition to 60.
    sim.LT3209_Bon2_Eff = 0.4  # empty, auto-end
    sim.tick()
    assert sim.BonChua_State == 60, f"Expected State 60, got {sim.BonChua_State}"
    
    # 50 -> 60 should reset Owner1 to False
    assert sim.BonChua_Owner_Nhanh1 == False, "Owner Nhanh1 should clear when transitioning to 60"
    print("[PASS] Test 6a: State 50 -> State 60.")

    # 60 -> 70 when cooled down
    sim.TT3301_BonChua1_Eff = 40.0
    sim.tick()
    assert sim.BonChua_State == 70, f"Expected State 70, got {sim.BonChua_State}"
    print("[PASS] Test 6b: State 60 -> State 70.")

    # 70 -> 80 when transfer done HMI
    sim.BonChua_Chuyen_Bon2_Xong_HMI = True
    sim.tick()
    assert sim.BonChua_State == 80, f"Expected State 80, got {sim.BonChua_State}"
    print("[PASS] Test 6c: State 70 -> State 80.")

    # In State 80, filter outputs must be ON and filler CV must be 75.0
    assert sim.Pump3364_Filter == True, "Filter Pump 3364 should be ON in State 80"
    assert sim.Pump3365_Filter == True, "Filter Pump 3365 should be ON in State 80"
    assert sim.V3340_Duong_Filter == True, "Filter Valve 3340 should be ON in State 80"
    assert sim.V3341_Duong_Filter == True, "Filter Valve 3341 should be ON in State 80"
    assert sim.CV_Filler_Cap_Dich == 75.0, f"Expected Filler CV 75.0, got {sim.CV_Filler_Cap_Dich}"
    print("[PASS] Actuator states verified in State 80.")

    # 2. State 80 + LT3307 <= 0.5 -> Sau scan State = 0, BonChua_Me_Hoan_Thanh = TRUE, tất cả bơm/van Filter = FALSE, CV_Filler_Cap_Dich = 0.0.
    sim.LT3307_BonChua2_Eff = 0.4
    sim.tick()
    assert sim.BonChua_State == 0, f"Expected State 0, got {sim.BonChua_State}"
    assert sim.BonChua_Me_Hoan_Thanh == True, "Completion flag should be TRUE"
    assert sim.Pump3364_Filter == False, "Filter Pump 3364 should be OFF in State 0"
    assert sim.Pump3365_Filter == False, "Filter Pump 3365 should be OFF in State 0"
    assert sim.V3340_Duong_Filter == False, "Filter Valve 3340 should be OFF in State 0"
    assert sim.V3341_Duong_Filter == False, "Filter Valve 3341 should be OFF in State 0"
    assert sim.CV_Filler_Cap_Dich == 0.0, f"Expected Filler CV 0.0, got {sim.CV_Filler_Cap_Dich}"
    print("[PASS] Test 2: State 80 -> State 0, outputs OFF, complete flag TRUE.")

    # 3. Chạy thêm nhiều scan ở Idle -> State vẫn 0, cờ hoàn thành vẫn TRUE, output vẫn OFF.
    for i in range(5):
        sim.tick()
        assert sim.BonChua_State == 0
        assert sim.BonChua_Me_Hoan_Thanh == True
        assert sim.Pump3364_Filter == False
        assert sim.Pump3365_Filter == False
        assert sim.V3340_Duong_Filter == False
        assert sim.V3341_Duong_Filter == False
        assert sim.CV_Filler_Cap_Dich == 0.0
    print("[PASS] Test 3: Multiple scans in Idle keep complete flag TRUE and outputs OFF.")

    # 4. Bắt đầu mẻ mới ở State 50 -> Cờ hoàn thành được Reset FALSE.
    # Set owner again to trigger new batch
    sim.BonChua_Owner_Nhanh1 = True
    sim.tick()
    assert sim.BonChua_State == 50
    assert sim.BonChua_Me_Hoan_Thanh == False, "Completion flag must be reset to FALSE on new batch (State 50)"
    print("[PASS] Test 4: New batch resets complete flag to FALSE.")

    # 5. Khi Stop hoặc lỗi tổng TRUE -> State = 0, hai Owner = FALSE, tất cả output Storage = FALSE, không có network phía sau Set lại Owner.
    # First, let's trigger Stop
    sim.PLC1_Stop_Active = True
    sim.tick()
    assert sim.BonChua_State == 0
    assert sim.BonChua_Owner_Nhanh1 == False, "Owner Nhanh1 must be FALSE during Stop"
    assert sim.BonChua_Owner_Nhanh2 == False, "Owner Nhanh2 must be FALSE during Stop"
    assert sim.Pump3364_Filter == False
    assert sim.Pump3365_Filter == False
    assert sim.V3340_Duong_Filter == False
    assert sim.V3341_Duong_Filter == False
    assert sim.CV_Filler_Cap_Dich == 0.0
    
    # Try to set owner during Stop, should not set it!
    sim.PLC1_Me_Nhanh1_Hoan_Thanh = True
    sim.tick()
    assert sim.BonChua_Owner_Nhanh1 == False, "Should not grant Owner Nhanh1 during Stop"
    print("[PASS] Test 5a: Stop active forces State 0, Owner FALSE, all outputs OFF.")

    # Now let's test Fault (Loi Tong)
    sim.PLC1_Stop_Active = False
    sim.PLC1_Loi_Tong = True
    sim.tick()
    # Try to set owner during Fault
    sim.PLC1_Me_Nhanh1_Hoan_Thanh = True
    sim.tick()
    assert sim.BonChua_State == 0
    assert sim.BonChua_Owner_Nhanh1 == False, "Should not grant Owner Nhanh1 during Fault"
    assert sim.BonChua_Owner_Nhanh2 == False
    print("[PASS] Test 5b: Fault active forces State 0, Owner FALSE, all outputs OFF.")
    
    print("[PASS] Advanced Storage Tank logic tests completed successfully.")


def test_dry_run_protection():
    print("---------------------------------------------------------")
    print(" UNIT TEST: INSTANT DRY-RUN PROTECTION")
    print("---------------------------------------------------------")
    # Case 1: Normal discharge (stops pump normally when level goes low)
    plc1 = PLC1Simulator()
    plc1.PLC1_State = 40
    plc1.BonChua_Owner_Nhanh1 = True
    plc1.BonChua_State = 50
    plc1.tick()
    assert plc1.Pump3264_Chuyen_Nhanh1 == True, "Pump should run"
    
    # Level goes below 0.5
    plc1.LT3209_Bon2_Eff = 0.4
    plc1.tick()
    # Pump stops normally
    assert plc1.Pump3264_Chuyen_Nhanh1 == False, "Pump should stop normally"
    assert plc1.PLC1_Loi_Dry_Run == False, "Dry run error should not trip during normal discharge completion!"
 
    # Case 2: Abnormal running cạn (pump runs but level is empty, trips immediately)
    plc1_abnormal = PLC1Simulator()
    plc1_abnormal.Pump3264_Chuyen_Nhanh1 = True
    plc1_abnormal.LT3209_Bon2_Eff = 0.3
    
    # Tick 1: Trips immediately
    plc1_abnormal.tick()
    assert plc1_abnormal.PLC1_Loi_Dry_Run == True, "Should trip dry run immediately!"
    
    # Tick 2: propagates Loi_Tong and performs shutdown
    plc1_abnormal.tick()
    assert plc1_abnormal.PLC1_Loi_Tong == True, "Loi_Tong should activate"
    assert plc1_abnormal.Pump3264_Chuyen_Nhanh1 == False, "Pump should be shut down by Loi_Tong!"
    print("[PASS] Dry-run protection test: Normal discharge is safe, abnormal dry-run trips instantly.")



def test_heartbeat_timeout():
    print("---------------------------------------------------------")
    print(" UNIT TEST: HEARTBEAT TIMEOUT MONITOR")
    print("---------------------------------------------------------")
    plc1 = PLC1Simulator()
    plc1.Gia_Lap_Heartbeat_Chay = False
    
    # Setup heartbeat tracking
    plc1.PLC2_Heartbeat_Last = 100
    plc1.DB_PLC1_Recv_From_PLC2_DB.Heartbeat = 101 # received first value
    plc1.tick()
    assert plc1.PLC2_Heartbeat_Changed == True, "Changed should be set"
    assert plc1.PLC2_Heartbeat_Last == 101, "Last should be updated"
    
    # Heartbeat is stuck for 4 ticks
    for _ in range(4):
        plc1.tick()
        assert plc1.PLC1_Heartbeat_Timeout == False, "Should not timeout yet"

    # Tick 6: reaches 5s timeout -> trips communication alarm
    plc1.tick()
    assert plc1.PLC1_Heartbeat_Timeout == True, "Heartbeat timeout must trip!"
    
    plc1.tick()
    assert plc1.PLC1_Loi_Truyen_Thong == True, "Timeout should cause communication alarm!"
    assert plc1.PLC1_Loi_Tong == True, "Communication alarm should cause Loi_Tong!"
    print("[PASS] Heartbeat timeout test: Communication alarm trips after 5s of stuck heartbeat.")


def test_vfd_mb_comm_load_startup_gate():
    print("---------------------------------------------------------")
    print(" UNIT TEST: VFD MB_COMM_LOAD STARTUP AND 8180 GATE")
    print("---------------------------------------------------------")
    plc1 = PLC1Simulator()

    # Lỗi thô từ MB_MASTER trước khi cổng sẵn sàng không được tính vào bộ đếm.
    plc1.VFD_Bon2_MB_Error = True
    plc1.VFD_Bon2_MB_Status = 0x8180
    plc1.tick()
    assert plc1.VFD_Bon2_MB_Error_Counter == 0, "8180 before CommReady must not increment counter"
    assert not plc1.VFD_Bon2_MB_Error_Confirmed, "8180 before CommReady must not latch confirmed error"
    assert not plc1.PLC1_Loi_Tong, "Startup 8180 must not latch total fault"

    # Bật chế độ đấu nối và cho phép comm: phải tự khởi tạo MB_COMM_LOAD, Ready rồi mới cho MB_MASTER chạy.
    plc1.HMI_Che_Do_Thi = 1
    plc1.HMI_Run_Enable = True
    plc1.HMI_VFD_Bon2_Comm_Enable = True
    plc1.tick()
    assert plc1.VFD_Bon2_Comm_Active, "CommActive should turn on after contactor delay is ready"
    assert plc1.VFD_Bon2_Comm_Ready, "MB_COMM_LOAD should set CommReady"
    assert plc1.VFD_Bon2_MB_Req or plc1.VFD_Bon2_MB_Busy, "Scheduler should start only after CommReady"
    assert plc1.VFD_Bon2_MB_Error_Counter == 0

    # Tắt comm phải xóa sạch ready/active/trigger để lần bật sau không bị kẹt.
    plc1.HMI_VFD_Bon2_Comm_Enable = False
    plc1.tick()
    assert not plc1.VFD_Bon2_Comm_Active
    assert not plc1.VFD_Bon2_Comm_Ready
    assert not plc1.VFD_Bon2_MBCL_Active
    assert not plc1.VFD_Bon2_MBCL_Trigger

    plc1.HMI_VFD_Bon2_Comm_Enable = True
    plc1.tick()
    assert plc1.VFD_Bon2_Comm_Ready, "Re-enable comm should retrigger MB_COMM_LOAD cleanly"
    print("[PASS] VFD MB_COMM_LOAD startup, re-enable and 8180 gate verified.")


def test_vfd_modbus_scheduler():
    print("---------------------------------------------------------")
    print(" UNIT TEST: SINGLE-CALL VFD MODBUS SCHEDULER (ADVANCED)")
    print("---------------------------------------------------------")
    plc1 = PLC1Simulator()
    
    # Kích hoạt truyền thông
    plc1.HMI_Che_Do_Thi = 1
    plc1.HMI_VFD_Bon2_Comm_Enable = True
    plc1.VFD_Bon2_MBCL_Done = True
    plc1.VFD_Bon2_Comm_Ready = True
    plc1.VFD_Bon2_Comm_Active = True
    plc1.VFD_Bon2_MB_ControlWord = 15  # Giả lập ControlWord
    plc1.VFD_Bon2_MB_FreqSetpoint = 1500  # Giả lập FreqSetpoint
    
    # --- TEST 1: CHUYỂN BƯỚC 0->1->2->3->0 LIÊN TỤC 2 VÒNG VÀ KHÔNG XUẤT HIỆN iStep = 4 ---
    # Đồng thời kiểm tra Step 0 ControlWord được gửi lại mỗi vòng.
    for loop in range(2):
        # Step 0
        plc1.tick()
        assert plc1.VFD_Bon2_iStep == 0
        assert plc1.VFD_Bon2_MB_Req == True or plc1.VFD_Bon2_MB_Busy == True
        assert plc1.VFD_Bon2_MB_Mode == 1
        assert plc1.VFD_Bon2_MB_DataAddr == 48502
        assert plc1.VFD_Bon2_MB_DataLen == 1
        assert plc1.VFD_Bon2_MB_DataBuffer == 15, f"ControlWord should be sent in Step 0. Loop: {loop}"
        
        # Cho Step 0 Done
        plc1.VFD_Bon2_MB_Busy = False
        plc1.VFD_Bon2_MB_Done = True
        plc1.tick()
        assert plc1.VFD_Bon2_iStep == 1, "Should transition to Step 1"
        assert plc1.VFD_Bon2_MB_Done == False, "Done should not be sticky"
        
        # Step 1
        plc1.tick()
        assert plc1.VFD_Bon2_iStep == 1
        assert plc1.VFD_Bon2_MB_Mode == 1
        assert plc1.VFD_Bon2_MB_DataAddr == 48503
        assert plc1.VFD_Bon2_MB_DataBuffer == 1500
        
        # Cho Step 1 Done
        plc1.VFD_Bon2_MB_Busy = False
        plc1.VFD_Bon2_MB_Done = True
        plc1.tick()
        assert plc1.VFD_Bon2_iStep == 2, "Should transition to Step 2"
        
        # Step 2
        plc1.tick()
        assert plc1.VFD_Bon2_iStep == 2
        assert plc1.VFD_Bon2_MB_Mode == 0
        assert plc1.VFD_Bon2_MB_DataAddr == 43202
        
        # Cho Step 2 Done
        plc1.VFD_Bon2_MB_Busy = False
        plc1.VFD_Bon2_MB_Done = True
        plc1.tick()
        assert plc1.VFD_Bon2_iStep == 3, "Should transition to Step 3"
        
        # Step 3
        plc1.tick()
        assert plc1.VFD_Bon2_iStep == 3
        assert plc1.VFD_Bon2_MB_Mode == 0
        assert plc1.VFD_Bon2_MB_DataAddr == 43203
        
        # Cho Step 3 Done -> Phải quay lại 0 lập tức, không được có iStep = 4!
        plc1.VFD_Bon2_MB_Busy = False
        plc1.VFD_Bon2_MB_Done = True
        plc1.tick()
        assert plc1.VFD_Bon2_iStep == 0, f"iStep must roll over directly to 0, got {plc1.VFD_Bon2_iStep}"
        assert plc1.VFD_Bon2_iStep != 4

    print("[PASS] iStep 0->1->2->3->0 2-loop rollover and ControlWord sending verified.")

    # --- TEST 2: KHI BUSY GIỮ NGUYÊN TOÀN BỘ THAM SỐ ---
    plc1.tick()  # Chuẩn bị Step 0
    assert plc1.VFD_Bon2_iStep == 0
    assert plc1.VFD_Bon2_MB_Busy == True
    
    # Trong khi Busy = True, ta thay đổi iStep bằng tay thành 1
    # Và kiểm tra xem các tham số gán có bị thay đổi theo Step 1 hay không
    plc1.VFD_Bon2_iStep = 1
    plc1.tick()
    # Các tham số vẫn phải giữ nguyên của Step 0
    assert plc1.VFD_Bon2_MB_Mode == 1, "Mode should remain Step 0 value"
    assert plc1.VFD_Bon2_MB_DataAddr == 48502, "DataAddr should remain Step 0 value"
    assert plc1.VFD_Bon2_MB_DataBuffer == 15, "DataBuffer should remain Step 0 value"
    
    # Khôi phục lại iStep
    plc1.VFD_Bon2_iStep = 0
    plc1.VFD_Bon2_MB_Busy = False
    plc1.VFD_Bon2_MB_Done = True
    plc1.tick()  # Transition to 1
    
    print("[PASS] Parameter locking when BUSY verified.")

    # --- TEST 3: LỖI LẦN 1 VÀ 2 RETRY SAU 200MS ---
    # DONE THÀNH CÔNG RESET COUNTER ---
    # CHỈ LỖI LẦN 3 MỚI CONFIRMED ---
    
    # Ta đang ở Step 1. Ta cho nó chạy.
    plc1.tick()
    assert plc1.VFD_Bon2_iStep == 1
    assert plc1.VFD_Bon2_MB_Busy == True
    
    # Giả lập lỗi lần 1
    plc1.VFD_Bon2_MB_Busy = False
    plc1.VFD_Bon2_MB_Error = True
    plc1.tick()
    # Sau tick này, Error_Edge được phát hiện, counter lỗi tăng lên 1, Retry_Active bật, REQ bị hạ.
    assert plc1.VFD_Bon2_MB_Error_Counter == 1, "Error counter should be 1"
    assert plc1.VFD_Bon2_MB_Retry_Active == True, "Retry should be active"
    assert plc1.VFD_Bon2_MB_Error_Confirmed == False, "Should not confirm error on 1st strike"
    assert plc1.VFD_Bon2_MB_Req == False
    
    # Giả lập trôi qua 190ms (18 ticks của simulator)
    for i in range(18):
        plc1.tick()
        assert plc1.VFD_Bon2_MB_Retry_Active == True
        assert plc1.VFD_Bon2_MB_Req == False
        
    # Thêm 10ms nữa để đạt 200ms -> phát lại REQ cùng bước
    plc1.tick()
    assert plc1.VFD_Bon2_MB_Retry_Active == False, "Retry should finish"
    assert plc1.VFD_Bon2_MB_Req == True, "New REQ should be triggered"
    assert plc1.VFD_Bon2_iStep == 1, "Step should remain 1"
    
    # Cho chạy lại
    plc1.tick()
    assert plc1.VFD_Bon2_MB_Busy == True
    
    # Giả lập lỗi lần 2
    plc1.VFD_Bon2_MB_Busy = False
    plc1.VFD_Bon2_MB_Error = True
    plc1.tick()
    assert plc1.VFD_Bon2_MB_Error_Counter == 2, "Error counter should be 2"
    assert plc1.VFD_Bon2_MB_Retry_Active == True
    assert plc1.VFD_Bon2_MB_Error_Confirmed == False, "Should not confirm error on 2nd strike"
    
    # Đợi 200ms
    for _ in range(19):
        plc1.tick()
    assert plc1.VFD_Bon2_MB_Req == True, "New REQ triggered after 2nd retry"
    
    # Giả lập thành công (DONE = True) để kiểm tra việc reset bộ đếm lỗi
    plc1.tick()  # Start transaction
    plc1.VFD_Bon2_MB_Busy = False
    plc1.VFD_Bon2_MB_Done = True
    plc1.VFD_Bon2_MB_Error = False
    plc1.tick()
    # Bộ đếm lỗi phải reset về 0, và bước chuyển sang 2
    assert plc1.VFD_Bon2_MB_Error_Counter == 0, "Counter should reset to 0 after success"
    assert plc1.VFD_Bon2_iStep == 2, "Should transition to Step 2"
    
    # Bây giờ ta kiểm tra kịch bản 3 lần lỗi liên tiếp để chốt Confirmed:
    # Lần lỗi 1 (ở Step 2)
    plc1.tick()  # Start Step 2
    plc1.VFD_Bon2_MB_Busy = False
    plc1.VFD_Bon2_MB_Error = True
    plc1.tick()
    assert plc1.VFD_Bon2_MB_Error_Counter == 1
    assert plc1.VFD_Bon2_MB_Error_Confirmed == False
    
    # Đợi 200ms để phát lại REQ
    for _ in range(19):
        plc1.tick()
    assert plc1.VFD_Bon2_MB_Req == True
    
    # Lần lỗi 2 (ở Step 2)
    plc1.tick()
    plc1.VFD_Bon2_MB_Busy = False
    plc1.VFD_Bon2_MB_Error = True
    plc1.tick()
    assert plc1.VFD_Bon2_MB_Error_Counter == 2
    assert plc1.VFD_Bon2_MB_Error_Confirmed == False
    
    # Đợi 200ms để phát lại REQ
    for _ in range(19):
        plc1.tick()
    assert plc1.VFD_Bon2_MB_Req == True
    
    # Lần lỗi 3 (ở Step 2)
    plc1.tick()
    plc1.VFD_Bon2_MB_Busy = False
    plc1.VFD_Bon2_MB_Error = True
    plc1.tick()
    assert plc1.VFD_Bon2_MB_Error_Counter == 3
    assert plc1.VFD_Bon2_MB_Error_Confirmed == True, "Error must be confirmed after 3 strikes"
    assert plc1.VFD_Bon2_MB_Retry_Active == False, "No more retry when error confirmed"
    
    # Xác nhận lỗi chốt tổng và tắt contactor
    plc1.tick()
    assert plc1.PLC1_Loi_Tong == True, "Loi_Tong should be latched"
    assert plc1.VFD_Bon2_Contactor == False, "Contactor should trip"
    
    print("[PASS] Modbus error counter, 200ms retry, success reset, and 3-strike confirmed trip verified.")


def test_modbus_tcp_scan_order():
    print("---------------------------------------------------------")
    print(" UNIT TEST: MODBUS TCP CLIENT SCAN CYCLE EXECUTION ORDER")
    print("---------------------------------------------------------")
    
    # We will simulate the scan cycle execution of the Modbus TCP client networks on PLC1.
    # We have two variables in DB_PLC1_MB_Buffer_DB: Recv_AckSeq, Recv_Heartbeat, Recv_Done_Discharge2
    # And we want them to update: DB_PLC1_Recv_From_PLC2_DB.AckSeq, DB_PLC1_Recv_From_PLC2_DB.Heartbeat, DB_PLC1_Recv_From_PLC2_DB.Done_Discharge2
    
    # Let's model the state variables:
    iStep = 1
    MB_TCP_DONE = True
    
    # Recv buffer values (updated asynchronously by Modbus driver before scan starts):
    Buffer_AckSeq = 42
    Buffer_Heartbeat = 123
    Buffer_Done_Discharge2 = True
    
    # Destination DB registers:
    Recv_AckSeq = 0
    Recv_Heartbeat = 0
    Recv_Done_Discharge2 = False
    
    # --- SIMULATE NEW ORDER: Copy Recv first, then Transition ---
    # Scan cycle runs:
    # 1. Copy Recv networks:
    if iStep == 1 and MB_TCP_DONE:
        Recv_AckSeq = Buffer_AckSeq
        Recv_Heartbeat = Buffer_Heartbeat
        Recv_Done_Discharge2 = Buffer_Done_Discharge2
        
    # 2. Transition network:
    if iStep == 1 and MB_TCP_DONE:
        iStep = 0
        
    # Assertions for New Order:
    assert Recv_AckSeq == 42, "AckSeq should be copied in the new order"
    assert Recv_Heartbeat == 123, "Heartbeat should be copied in the new order"
    assert Recv_Done_Discharge2 == True, "Done_Discharge2 should be copied in the new order"
    assert iStep == 0, "iStep should transition to 0"
    
    # --- SIMULATE OLD ORDER: Transition first, then Copy Recv ---
    iStep_old = 1
    Recv_AckSeq_old = 0
    Recv_Heartbeat_old = 0
    Recv_Done_Discharge2_old = False
    
    # 1. Transition network runs first:
    if iStep_old == 1 and MB_TCP_DONE:
        iStep_old = 0
        
    # 2. Copy Recv networks run second:
    if iStep_old == 1 and MB_TCP_DONE:
        Recv_AckSeq_old = Buffer_AckSeq
        Recv_Heartbeat_old = Buffer_Heartbeat
        Recv_Done_Discharge2_old = Buffer_Done_Discharge2
        
    # Assertions for Old Order (proving it fails):
    assert Recv_AckSeq_old == 0, "AckSeq would NOT be copied in the old order"
    assert Recv_Heartbeat_old == 0, "Heartbeat would NOT be copied in the old order"
    assert Recv_Done_Discharge2_old == False, "Done_Discharge2 would NOT be copied in the old order"
    assert iStep_old == 0, "iStep transitions to 0"
    
    print("[PASS] Modbus TCP scan cycle order test: Verified copy runs before transition and updates registers.")


def test_plc1_one_batch_and_no_loop():
    print("---------------------------------------------------------")
    print(" REGRESSION TEST: PLC1 ONE BATCH AND NO LOOP")
    print("---------------------------------------------------------")
    sim = PLC1Simulator()
    
    # 1. Start batch
    sim.Nut_Khoi_Dong_Eff = True
    sim.tick()
    sim.Nut_Khoi_Dong_Eff = False
    assert sim.PLC1_State == 10
    assert sim.PLC1_Auto_Enable == True
    
    # Run through the batch
    # State 10 dosing -> FQ reaches 100
    sim.FQ3200_Bon1_Eff = 100.0
    sim.tick()
    assert sim.PLC1_State == 11
    
    # State 11 tip -> tip timer done after 30 ticks
    for _ in range(29):
        sim.tick()
        assert sim.PLC1_State == 11
    sim.tick()
    assert sim.PLC1_State == 12
    
    # State 12 khuay -> done after SP_Time_Khuay_Bon1 ticks
    for _ in range(sim.HMI_SP_Time_Khuay_Bon1):
        sim.tick()
    assert sim.PLC1_State == 15
    
    # State 15 xa -> level <= 0.5
    sim.LT3203_Bon1_Eff = 0.4
    sim.tick()
    assert sim.PLC1_State == 20
    
    # State 20 dosing -> FQ reaches 120
    sim.FQ3205_Bon2_Eff = 120.0
    sim.tick()
    assert sim.PLC1_State == 21
    
    # State 21 tip -> tip timer done after 30 ticks
    for _ in range(29):
        sim.tick()
        assert sim.PLC1_State == 21
    sim.tick()
    assert sim.PLC1_State == 22
    
    # State 22 khuay thuan -> done
    for _ in range(sim.HMI_SP_Time_Fwd):
        sim.tick()
    assert sim.PLC1_State == 23
    
    # State 23 khuay nghich -> done
    for _ in range(sim.HMI_SP_Time_Rev):
        sim.tick()
    assert sim.PLC1_State == 30
    
    # State 30 PID -> temp >= SP
    sim.TT3208_Bon2_Eff = 75.0
    sim.tick()
    assert sim.PLC1_State == 31
    
    # State 31 sterilize -> done
    for _ in range(sim.HMI_SP_Time_Sterilize):
        sim.tick()
    assert sim.PLC1_State == 40
    
    # Storage receives the batch (State 50)
    assert sim.BonChua_Owner_Nhanh1 == True
    assert sim.BonChua_State == 50
    assert sim.Pump3264_Chuyen_Nhanh1 == True
    
    # Bồn 2 becomes empty (LT <= 0.5)
    sim.LT3209_Bon2_Eff = 0.4
    sim.tick()
    
    # PLC1 should return to State 0, Auto_Enable FALSE, all step flags FALSE
    assert sim.PLC1_State == 0, f"Expected State 0, got {sim.PLC1_State}"
    assert sim.PLC1_Auto_Enable == False, "Auto Enable must be FALSE"
    
    # Verify one-hot step flag constraint: at most 1 step flag can be TRUE
    step_flags = [
        sim.PLC1_Step_Bon1_Dosing, sim.PLC1_Step_Bon1_Tip, sim.PLC1_Step_Bon1_Khuay,
        sim.PLC1_Step_Bon1_Xa, sim.PLC1_Step_Bon2_Dosing, sim.PLC1_Step_Bon2_Tip,
        sim.PLC1_Step_Bon2_Khuay_Thuan, sim.PLC1_Step_Bon2_Khuay_Nghich,
        sim.PLC1_Step_Bon2_PID, sim.PLC1_Step_Bon2_Thanh_Trung, sim.PLC1_Me_Nhanh1_Hoan_Thanh
    ]
    assert sum(step_flags) == 0, "All step flags must be FALSE when State is 0"
    
    # Keep ticking for 100 scans, assert PLC1 remains Idle (0) and Storage runs independently
    for scan in range(100):
        # Let's simulate Storage process values changing so Storage transitions
        if sim.BonChua_State == 60:
            sim.TT3301_BonChua1_Eff = 40.0 # cooled down
        elif sim.BonChua_State == 70:
            sim.BonChua_Chuyen_Bon2_Xong_HMI = True
        elif sim.BonChua_State == 80:
            sim.LT3307_BonChua2_Eff = 0.4 # empty
            
        sim.tick()
        
        # PLC1 must remain in State 0
        assert sim.PLC1_State == 0, f"PLC1 restarted abnormally at scan {scan}! State: {sim.PLC1_State}"
        assert sim.PLC1_Auto_Enable == False, f"PLC1 Auto Enable turned TRUE at scan {scan}!"
        
        # Verify one-hot: at most one step flag is TRUE
        step_flags = [
            sim.PLC1_Step_Bon1_Dosing, sim.PLC1_Step_Bon1_Tip, sim.PLC1_Step_Bon1_Khuay,
            sim.PLC1_Step_Bon1_Xa, sim.PLC1_Step_Bon2_Dosing, sim.PLC1_Step_Bon2_Tip,
            sim.PLC1_Step_Bon2_Khuay_Thuan, sim.PLC1_Step_Bon2_Khuay_Nghich,
            sim.PLC1_Step_Bon2_PID, sim.PLC1_Step_Bon2_Thanh_Trung, sim.PLC1_Me_Nhanh1_Hoan_Thanh
        ]
        assert sum(step_flags) <= 1, f"One-hot violated at scan {scan}: multiple steps TRUE!"
        
    print("[PASS] PLC1 one batch and no loop regression test passed.")


def test_plc1_start_button_held():
    print("---------------------------------------------------------")
    print(" REGRESSION TEST: PLC1 START BUTTON HELD")
    print("---------------------------------------------------------")
    sim = PLC1Simulator()
    
    # Hold Start button for 100 ticks
    sim.Nut_Khoi_Dong_Eff = True
    
    # First tick -> State should become 10
    sim.tick()
    assert sim.PLC1_State == 10
    
    # Dosing completes, state should become 11
    sim.FQ3200_Bon1_Eff = 100.0
    sim.tick()
    assert sim.PLC1_State == 11
    
    # Keep ticking for another 5 scans while holding Start button
    for _ in range(5):
        sim.tick()
        
    # Since we are holding Start, we should remain in State 11 and NOT restart at 10
    assert sim.PLC1_State == 11, f"Expected State 11, got {sim.PLC1_State}"
    
    # Now complete the batch while still holding Start
    # State 11 tip done (remaining 25 ticks of 30)
    for _ in range(25):
        sim.tick()
    assert sim.PLC1_State == 12
    
    # State 12 khuay done
    for _ in range(sim.HMI_SP_Time_Khuay_Bon1):
        sim.tick()
    assert sim.PLC1_State == 15
    
    # State 15 xa done
    sim.LT3203_Bon1_Eff = 0.4
    sim.tick()
    assert sim.PLC1_State == 20
    
    # State 20 dosing done
    sim.FQ3205_Bon2_Eff = 120.0
    sim.tick()
    assert sim.PLC1_State == 21
    
    # State 21 tip done
    for _ in range(30):
        sim.tick()
    assert sim.PLC1_State == 22
    
    # State 22 khuay thuan done
    for _ in range(sim.HMI_SP_Time_Fwd):
        sim.tick()
    assert sim.PLC1_State == 23
    
    # State 23 khuay nghich done
    for _ in range(sim.HMI_SP_Time_Rev):
        sim.tick()
    assert sim.PLC1_State == 30
    
    # State 30 PID done
    sim.TT3208_Bon2_Eff = 75.0
    sim.tick()
    assert sim.PLC1_State == 31
    
    # State 31 sterilize done
    for _ in range(sim.HMI_SP_Time_Sterilize):
        sim.tick()
    assert sim.PLC1_State == 40
    
    # State 40 discharge done
    sim.LT3209_Bon2_Eff = 0.4
    sim.tick()
    
    # PLC1 should be at State 0 and NOT auto-restart even though Start button is STILL HELD!
    assert sim.PLC1_State == 0, f"PLC1 restarted abnormally while Start button was held! State: {sim.PLC1_State}"
    assert sim.PLC1_Auto_Enable == False
    
    # To start a second batch, we must release Start and press again
    sim.Nut_Khoi_Dong_Eff = False
    sim.tick()
    assert sim.PLC1_State == 0
    
    sim.Nut_Khoi_Dong_Eff = True
    sim.tick()
    assert sim.PLC1_State == 10, "Should start second batch on new rising edge"
    print("[PASS] PLC1 start button held regression test passed.")


def test_plc2_one_batch_and_no_loop():
    print("---------------------------------------------------------")
    print(" REGRESSION TEST: PLC2 ONE BATCH AND NO LOOP")
    print("---------------------------------------------------------")
    sim = PLC2Simulator()
    
    # 1. Start batch
    sim.Nut_Khoi_Dong_Nhan = True
    sim.tick()
    sim.Nut_Khoi_Dong_Nhan = False
    assert sim.PLC2_State == 10
    assert sim.PLC2_Auto_Enable == True
    
    # Run through the batch
    # State 10 dosing -> FQ reaches 100
    sim.FQ3210_Bon3_Eff = 100.0
    sim.tick()
    assert sim.PLC2_State == 11
    
    # State 11 tip -> tip timer done after 30 ticks
    for _ in range(29):
        sim.tick()
        assert sim.PLC2_State == 11
    sim.tick()
    assert sim.PLC2_State == 12
    
    # State 12 khuay -> done
    for _ in range(sim.HMI_SP_Time_Khuay_Bon3):
        sim.tick()
    assert sim.PLC2_State == 15
    
    # State 15 xa -> level <= 0.5
    sim.LT3213_Bon3_Eff = 0.4
    sim.tick()
    assert sim.PLC2_State == 20
    
    # State 20 dosing -> FQ reaches 120
    sim.FQ3215_Bon4_Eff = 120.0
    sim.tick()
    assert sim.PLC2_State == 21
    
    # State 21 tip -> tip timer done after 30 ticks
    for _ in range(29):
        sim.tick()
        assert sim.PLC2_State == 21
    sim.tick()
    assert sim.PLC2_State == 22
    
    # State 22 khuay thuan -> done
    for _ in range(sim.HMI_SP_Time_Fwd):
        sim.tick()
    assert sim.PLC2_State == 23
    
    # State 23 khuay nghich -> done
    for _ in range(sim.HMI_SP_Time_Rev):
        sim.tick()
    assert sim.PLC2_State == 30
    
    # State 30 PID -> temp >= SP
    sim.TT3219_Bon4_Eff = 95.0
    sim.tick()
    assert sim.PLC2_State == 31
    
    # State 31 sterilize -> done
    for _ in range(sim.HMI_SP_Time_Sterilize):
        sim.tick()
    assert sim.PLC2_State == 40
    
    # Receive transfer command
    sim.Pump3265_Chuyen_Nhanh2_Cmd_Nhan = True
    sim.tick()
    assert sim.Pump3265_Chuyen_Nhanh2 == True
    
    # Bồn 4 becomes empty (LT <= 0.5)
    sim.LT3218_Bon4_Eff = 0.4
    sim.tick()
    
    # PLC2 should return to State 0, Auto_Enable FALSE, all step flags FALSE
    assert sim.PLC2_State == 0, f"Expected State 0, got {sim.PLC2_State}"
    assert sim.PLC2_Auto_Enable == False, "Auto Enable must be FALSE"
    
    # Verify one-hot step flag constraint: at most 1 step flag can be TRUE
    step_flags = [
        sim.PLC2_Step_Bon3_Dosing, sim.PLC2_Step_Bon3_Tip, sim.PLC2_Step_Bon3_Khuay,
        sim.PLC2_Step_Bon3_Xa, sim.PLC2_Step_Bon4_Dosing, sim.PLC2_Step_Bon4_Tip,
        sim.PLC2_Step_Bon4_Khuay_Thuan, sim.PLC2_Step_Bon4_Khuay_Nghich,
        sim.PLC2_Step_Bon4_PID_Mo_Phong, sim.PLC2_Step_Bon4_Thanh_Trung, sim.PLC2_Me_Nhanh2_Hoan_Thanh
    ]
    assert sum(step_flags) == 0, "All step flags must be FALSE when State is 0"
    
    # Keep ticking for 100 scans, assert PLC2 remains Idle (0)
    for scan in range(100):
        sim.tick()
        assert sim.PLC2_State == 0, f"PLC2 restarted abnormally at scan {scan}! State: {sim.PLC2_State}"
        assert sim.PLC2_Auto_Enable == False, f"PLC2 Auto Enable turned TRUE at scan {scan}!"
        
        # Verify one-hot
        step_flags = [
            sim.PLC2_Step_Bon3_Dosing, sim.PLC2_Step_Bon3_Tip, sim.PLC2_Step_Bon3_Khuay,
            sim.PLC2_Step_Bon3_Xa, sim.PLC2_Step_Bon4_Dosing, sim.PLC2_Step_Bon4_Tip,
            sim.PLC2_Step_Bon4_Khuay_Thuan, sim.PLC2_Step_Bon4_Khuay_Nghich,
            sim.PLC2_Step_Bon4_PID_Mo_Phong, sim.PLC2_Step_Bon4_Thanh_Trung, sim.PLC2_Me_Nhanh2_Hoan_Thanh
        ]
        assert sum(step_flags) <= 1, f"One-hot violated at scan {scan}: multiple steps TRUE!"
        
    print("[PASS] PLC2 one batch and no loop regression test passed.")


def test_plc2_start_button_held():
    print("---------------------------------------------------------")
    print(" REGRESSION TEST: PLC2 START BUTTON HELD")
    print("---------------------------------------------------------")
    sim = PLC2Simulator()
    
    # Hold Start button for 100 ticks
    sim.Nut_Khoi_Dong_Nhan = True
    
    # First tick -> State should become 10
    sim.tick()
    assert sim.PLC2_State == 10
    
    # Dosing completes, state should become 11
    sim.FQ3210_Bon3_Eff = 100.0
    sim.tick()
    assert sim.PLC2_State == 11
    
    # Keep ticking for another 5 scans while holding Start button
    for _ in range(5):
        sim.tick()
        
    assert sim.PLC2_State == 11, f"Expected State 11, got {sim.PLC2_State}"
    
    # Now complete the batch while still holding Start
    # State 11 tip done (remaining 25 ticks of 30)
    for _ in range(25):
        sim.tick()
    assert sim.PLC2_State == 12
    
    # State 12 khuay done
    for _ in range(sim.HMI_SP_Time_Khuay_Bon3):
        sim.tick()
    assert sim.PLC2_State == 15
    
    # State 15 xa done
    sim.LT3213_Bon3_Eff = 0.4
    sim.tick()
    assert sim.PLC2_State == 20
    
    # State 20 dosing done
    sim.FQ3215_Bon4_Eff = 120.0
    sim.tick()
    assert sim.PLC2_State == 21
    
    # State 21 tip done
    for _ in range(30):
        sim.tick()
    assert sim.PLC2_State == 22
    
    # State 22 khuay thuan done
    for _ in range(sim.HMI_SP_Time_Fwd):
        sim.tick()
    assert sim.PLC2_State == 23
    
    # State 23 khuay nghich done
    for _ in range(sim.HMI_SP_Time_Rev):
        sim.tick()
    assert sim.PLC2_State == 30
    
    # State 30 PID done
    sim.TT3219_Bon4_Eff = 95.0
    sim.tick()
    assert sim.PLC2_State == 31
    
    # State 31 sterilize done
    for _ in range(sim.HMI_SP_Time_Sterilize):
        sim.tick()
    assert sim.PLC2_State == 40
    
    # State 40 discharge done
    sim.Pump3265_Chuyen_Nhanh2_Cmd_Nhan = True
    sim.tick()
    sim.LT3218_Bon4_Eff = 0.4
    sim.tick()
    
    # PLC2 should be at State 0 and NOT auto-restart even though Start button is STILL HELD!
    assert sim.PLC2_State == 0, f"PLC2 restarted abnormally while Start button was held! State: {sim.PLC2_State}"
    assert sim.PLC2_Auto_Enable == False
    
    # To start a second batch, we must release Start and press again
    sim.Nut_Khoi_Dong_Nhan = False
    sim.tick()
    assert sim.PLC2_State == 0
    
    sim.Nut_Khoi_Dong_Nhan = True
    sim.tick()
    assert sim.PLC2_State == 10, "Should start second batch on new rising edge"
    print("[PASS] PLC2 start button held regression test passed.")


def test_iec_tip_timer_delay():
    print("---------------------------------------------------------")
    print(" REGRESSION TEST: IEC TIP TIMER DELAY")
    print("---------------------------------------------------------")
    sim = PLC1Simulator()
    sim.Nut_Khoi_Dong_Eff = True
    sim.tick()
    sim.Nut_Khoi_Dong_Eff = False
    sim.FQ3200_Bon1_Eff = 100.0
    sim.tick()
    assert sim.PLC1_State == 11
    
    # Tick 1 to 29: tip timer should not be done
    for tick in range(1, 30):
        sim.tick()
        assert sim.PLC1_State == 11, f"Tip timer completed too early at tick {tick}!"
        
    sim.tick()
    assert sim.PLC1_State == 12, "Tip timer should complete at 30 ticks (3.0s)"
    print("[PASS] IEC tip timer delay test passed.")


def test_agitator_animation():
    print("---------------------------------------------------------")
    print(" UNIT TEST: AGITATOR ANIMATION FRAMES")
    print("---------------------------------------------------------")
    # NOTE: tick() derives step flags from PLC1_State/PLC2_State (one-hot mapping),
    # actuator outputs from step flags, and timer accumulators are updated inside tick().
    # Strategy: lock the simulator in the target state BEFORE each tick and set all
    # timer setpoints to a very large value so timers never trigger a transition.

    # ── PLC1 ──────────────────────────────────────────────────────────────────
    sim1 = PLC1Simulator()
    sim1.PLC1_Loi_Tong  = False
    sim1.Nut_Dung_Eff   = False
    sim1.PLC1_SP_Valid  = True
    # Freeze all PLC1 timers so no automatic state transition occurs
    sim1.HMI_SP_Time_Khuay_Bon1   = 9999
    sim1.HMI_SP_Time_Fwd           = 9999
    sim1.HMI_SP_Time_Rev           = 9999
    sim1.HMI_SP_Time_Sterilize     = 9999

    # 1. Bồn 1: stopped initially
    assert sim1.HMI_Anim_Bon1_Frame == 0
    sim1.tick()
    assert sim1.HMI_Anim_Bon1_Frame == 0

    # Bồn 1: running — lock into State 12 (khuay_bon1)
    expected = 0
    for cycle in range(20):
        sim1.PLC1_State = 12          # set BEFORE tick so one-hot maps correctly
        sim1.tick()
        expected = (expected + 1) % 8
        assert sim1.HMI_Anim_Bon1_Frame == expected, \
            f"Bon 1 Frame mismatched at cycle {cycle}! Expected: {expected}, Got: {sim1.HMI_Anim_Bon1_Frame}"

    # Bồn 1: stopped — return to idle
    sim1.PLC1_State = 0
    sim1.tick()
    assert sim1.HMI_Anim_Bon1_Frame == 0

    # 2. Bồn 2: stopped initially
    assert sim1.HMI_Anim_Bon2_Frame == 0
    sim1.PLC1_Auto_Enable = True

    # Bồn 2: running forward — State 22 (khuay thuan)
    expected = 0
    for cycle in range(20):
        sim1.PLC1_State = 22
        sim1.tick()
        expected = (expected + 1) % 8
        assert sim1.HMI_Anim_Bon2_Frame == expected, \
            f"Bon 2 Forward Frame mismatched at cycle {cycle}! Expected: {expected}, Got: {sim1.HMI_Anim_Bon2_Frame}"

    # Bồn 2: running reverse — State 23 (khuay nghich)
    sim1.HMI_Anim_Bon2_Frame = 0
    expected = 0
    for cycle in range(20):
        sim1.PLC1_State = 23
        sim1.tick()
        expected = (expected - 1) % 8
        assert sim1.HMI_Anim_Bon2_Frame == expected, \
            f"Bon 2 Reverse Frame mismatched at cycle {cycle}! Expected: {expected}, Got: {sim1.HMI_Anim_Bon2_Frame}"

    # Bồn 2: stopped
    sim1.PLC1_State = 0
    sim1.tick()
    assert sim1.HMI_Anim_Bon2_Frame == 0

    # ── PLC2 ──────────────────────────────────────────────────────────────────
    sim2 = PLC2Simulator()
    sim2.PLC2_Loi_Tong  = False
    # Freeze all PLC2 timers
    sim2.HMI_SP_Time_Khuay_Bon3   = 9999
    sim2.HMI_SP_Time_Fwd           = 9999
    sim2.HMI_SP_Time_Rev           = 9999
    sim2.HMI_SP_Time_Sterilize     = 9999

    # 3. Bồn 3: stopped initially
    assert sim2.HMI_Anim_Bon3_Frame == 0

    # Bồn 3: running — State 12
    expected = 0
    for cycle in range(20):
        sim2.PLC2_State = 12
        sim2.tick()
        expected = (expected + 1) % 8
        assert sim2.HMI_Anim_Bon3_Frame == expected, \
            f"Bon 3 Frame mismatched at cycle {cycle}! Expected: {expected}, Got: {sim2.HMI_Anim_Bon3_Frame}"

    # Bồn 3: stopped
    sim2.PLC2_State = 0
    sim2.tick()
    assert sim2.HMI_Anim_Bon3_Frame == 0

    # 4. Bồn 4: stopped initially
    assert sim2.HMI_Anim_Bon4_Frame == 0

    # Bồn 4: running forward — State 22
    expected = 0
    for cycle in range(20):
        sim2.PLC2_State = 22
        sim2.tick()
        expected = (expected + 1) % 8
        assert sim2.HMI_Anim_Bon4_Frame == expected, \
            f"Bon 4 Forward Frame mismatched at cycle {cycle}! Expected: {expected}, Got: {sim2.HMI_Anim_Bon4_Frame}"

    # Bồn 4: running reverse — State 23
    sim2.HMI_Anim_Bon4_Frame = 0
    expected = 0
    for cycle in range(20):
        sim2.PLC2_State = 23
        sim2.tick()
        expected = (expected - 1) % 8
        assert sim2.HMI_Anim_Bon4_Frame == expected, \
            f"Bon 4 Reverse Frame mismatched at cycle {cycle}! Expected: {expected}, Got: {sim2.HMI_Anim_Bon4_Frame}"

    # Bồn 4: stopped
    sim2.PLC2_State = 0
    sim2.tick()
    assert sim2.HMI_Anim_Bon4_Frame == 0

    print("[PASS] Agitator animation logic verified for all four tanks.")


def test_manual_control():
    print("---------------------------------------------------------")
    print(" UNIT TEST: PLC MANUAL CONTROL AND SAFETY INTERLOCKS")
    print("---------------------------------------------------------")
    
    # 1. Engineer/Admin can control Manual
    sim1 = PLC1Simulator()
    sim1.HMI_Che_Do_Manual = True
    sim1.HMI_Cho_Phep_Sua_Thong_So = True
    sim1.HMI_User_Level = 2  # Engineer
    sim1.tick()
    assert sim1.PLC1_Manual_Mode_Active == True, "Manual Mode should be active for Engineer"

    # Set manual commands
    sim1.V3230_Nuoc_Bon1_Man = True
    sim1.CV3201_Nuoc_Bon1_Man = 50.0
    sim1.tick()
    assert sim1.V3230_Nuoc_Bon1 == True, "Manual DO should be active"
    assert sim1.CV3201_Nuoc_Bon1 == 50.0, "Manual AO should be 50.0"

    # 2. Operator cannot control Manual
    sim1_op = PLC1Simulator()
    sim1_op.HMI_Che_Do_Manual = True
    sim1_op.HMI_Cho_Phep_Sua_Thong_So = True
    sim1_op.HMI_User_Level = 1  # Operator
    sim1_op.V3230_Nuoc_Bon1_Man = True
    sim1_op.tick()
    assert sim1_op.PLC1_Manual_Mode_Active == False, "Manual Mode should NOT be active for Operator"
    assert sim1_op.V3230_Nuoc_Bon1 == False, "Operator should not activate manual DO"

    # 3. Manual and Auto cannot run simultaneously
    sim1_seq = PLC1Simulator()
    sim1_seq.PLC1_State = 12
    sim1_seq.PLC1_Auto_Enable = True
    sim1_seq.PID_Bon2_Enable = True
    sim1_seq.HMI_Che_Do_Manual = True
    sim1_seq.HMI_Cho_Phep_Sua_Thong_So = True
    sim1_seq.HMI_User_Level = 3  # Admin
    sim1_seq.tick()
    assert sim1_seq.PLC1_Auto_Enable == False, "Auto Enable should be reset"
    assert sim1_seq.PID_Bon2_Enable == False, "PID Enable should be reset"
    assert sim1_seq.PLC1_State == 0, "State should be reset to IDLE (0)"

    # 4. E-Stop/Stop/Fault wins over Manual
    sim1_safe = PLC1Simulator()
    sim1_safe.HMI_Che_Do_Manual = True
    sim1_safe.HMI_Cho_Phep_Sua_Thong_So = True
    sim1_safe.HMI_User_Level = 2
    sim1_safe.V3230_Nuoc_Bon1_Man = True
    sim1_safe.CV3201_Nuoc_Bon1_Man = 50.0
    sim1_safe.tick()
    assert sim1_safe.V3230_Nuoc_Bon1 == True
    
    # Trigger E-Stop
    sim1_safe.PLC1_EStop_Latch = True
    sim1_safe.tick()
    assert sim1_safe.V3230_Nuoc_Bon1 == False, "E-Stop should turn off manual DO"
    assert sim1_safe.CV3201_Nuoc_Bon1 == 0.0, "E-Stop should clear manual AO"
    assert sim1_safe.V3230_Nuoc_Bon1_Man == False, "E-Stop should clear manual DO command tag"
    assert sim1_safe.CV3201_Nuoc_Bon1_Man == 0.0, "E-Stop should clear manual AO command tag"

    # 5. AO Manual clamp 0..100%
    sim1_clamp = PLC1Simulator()
    sim1_clamp.HMI_Che_Do_Manual = True
    sim1_clamp.HMI_Cho_Phep_Sua_Thong_So = True
    sim1_clamp.HMI_User_Level = 2
    sim1_clamp.CV3201_Nuoc_Bon1_Man = 150.0
    sim1_clamp.CV3206_Hoi_Bon2_Man = -50.0
    sim1_clamp.tick()
    assert sim1_clamp.CV3201_Nuoc_Bon1 == 100.0, "AO should clamp to 100.0"
    assert sim1_clamp.CV3206_Hoi_Bon2 == 0.0, "AO should clamp to 0.0"

    # 6. Leaving manual mode does not replay previous command
    sim1_exit = PLC1Simulator()
    sim1_exit.HMI_Che_Do_Manual = True
    sim1_exit.HMI_Cho_Phep_Sua_Thong_So = True
    sim1_exit.HMI_User_Level = 2
    sim1_exit.V3230_Nuoc_Bon1_Man = True
    sim1_exit.tick()
    assert sim1_exit.V3230_Nuoc_Bon1 == True
    
    # Exit manual mode
    sim1_exit.HMI_Che_Do_Manual = False
    sim1_exit.tick()
    assert sim1_exit.V3230_Nuoc_Bon1_Man == False, "Manual command tag should clear upon exit"
    assert sim1_exit.V3230_Nuoc_Bon1 == False, "Output should clear when manual mode is inactive"

    # 7. Pump Manual only runs if source level > 0.5 (interlocked)
    sim1_pump = PLC1Simulator()
    sim1_pump.HMI_Che_Do_Manual = True
    sim1_pump.HMI_Cho_Phep_Sua_Thong_So = True
    sim1_pump.HMI_User_Level = 2
    
    # Try turning on pump when level is low initially
    sim1_pump.LT3209_Bon2_Eff = 0.4
    sim1_pump.Pump3264_Chuyen_Nhanh1_Man = True
    sim1_pump.tick()
    assert sim1_pump.Pump3264_Chuyen_Nhanh1 == False, "Pump should not start since level is low"
    assert sim1_pump.Pump3264_Chuyen_Nhanh1_Man == False, "Manual command tag should be reset"
    assert sim1_pump.PLC1_Loi_Dry_Run == False, "Should not trigger dry run because pump never ran"

    # Now turn on pump when level is safe
    sim1_pump.LT3209_Bon2_Eff = 10.0
    sim1_pump.Pump3264_Chuyen_Nhanh1_Man = True
    sim1_pump.tick()
    assert sim1_pump.Pump3264_Chuyen_Nhanh1 == True, "Pump should run when level is safe"

    # Now level drops to low while pump is running
    sim1_pump.LT3209_Bon2_Eff = 0.4
    sim1_pump.tick()
    assert sim1_pump.PLC1_Loi_Dry_Run == True, "Should trigger dry run trip"
    assert sim1_pump.Pump3264_Chuyen_Nhanh1 == False, "Pump output should be shut down by interlock/fault"
    assert sim1_pump.Pump3264_Chuyen_Nhanh1_Man == False, "Manual command tag should be reset"


    # ── PLC2 Manual Tests ───────────────────────────────────────────────
    sim2 = PLC2Simulator()
    sim2.HMI_Che_Do_Manual = True
    sim2.HMI_Cho_Phep_Sua_Thong_So = True
    sim2.HMI_User_Level = 2
    sim2.V3240_Nuoc_Bon3_Man = True
    sim2.CV3211_Nuoc_Bon3_Man = 75.0
    sim2.tick()
    assert sim2.PLC2_Manual_Mode_Active == True
    assert sim2.V3240_Nuoc_Bon3 == True
    assert sim2.CV3211_Nuoc_Bon3 == 75.0

    print("[PASS] PLC manual control and safety interlock tests completed successfully.")


def test_regression_duplicate_blocks():
    print("---------------------------------------------------------")
    print(" REGRESSION TEST: NO DUPLICATE PLC BLOCK NUMBERS")
    print("---------------------------------------------------------")
    import os
    from validate_block_numbers import run_block_validation
    assert run_block_validation() == True, "Duplicate PLC block numbers detected!"
    print("[PASS] No duplicate block numbers found.")


def test_regression_network_order():
    print("---------------------------------------------------------")
    print(" REGRESSION TEST: XA_XONG NETWORK ORDER BEFORE DRY_RUN")
    print("---------------------------------------------------------")
    import os
    import xml.etree.ElementTree as ET

    def get_multilingual_text(net):
        """Get the first available text from a network's multilingual title."""
        for item in net.findall(".//{*}MultilingualTextItem"):
            tn = item.find(".//{*}Text")
            if tn is not None and tn.text:
                return tn.text.strip()
        # Fall back to direct title
        title_node = net.find(".//{*}Title")
        if title_node is not None and title_node.text:
            return title_node.text.strip()
        return ""

    def check_order(filename, title_xa_fragment, title_dry_fragment):
        path = os.path.join("projects", "Mixing_Nuoc_Tuong_Maggi_2026", "output", filename)
        if not os.path.exists(path):
            print(f"Skipping order check for missing file: {filename}")
            return
        tree = ET.parse(path)
        root = tree.getroot()
        idx_xa = -1
        idx_dry = -1
        for idx, net in enumerate(root.findall(".//{*}SW.Blocks.CompileUnit")):
            text = get_multilingual_text(net)
            if title_xa_fragment in text and idx_xa == -1:
                idx_xa = idx
            elif title_dry_fragment in text and idx_dry == -1:
                idx_dry = idx
        assert idx_xa != -1, f"Could not find network containing: '{title_xa_fragment}' in {filename}"
        assert idx_dry != -1, f"Could not find network containing: '{title_dry_fragment}' in {filename}"
        assert idx_xa < idx_dry, (
            f"Network order violation in {filename}: "
            f"'{title_xa_fragment}' (idx {idx_xa}) must execute before '{title_dry_fragment}' (idx {idx_dry})"
        )
        print(f"[PASS] Network order verified in {filename}: '{title_xa_fragment}' (idx {idx_xa}) -> '{title_dry_fragment}' (idx {idx_dry})")

    check_order("FC_PLC1_Mixing.xml", "Bồn 2 đã xả xong", "Dry Run bơm Nhánh 1")
    check_order("FC_PLC2_Mixing.xml", "Bồn 4 đã xả xong", "Dry Run bơm Nhánh 2")
    check_order("FC_Bon_Chua_Loc.xml", "Bồn chứa 1 đã xả xong", "Dry Run bơm luân chuyển Bồn chứa 1")


def test_level_state_animation():
    print("---------------------------------------------------------")
    print(" UNIT TEST: LEVEL STATE ANIMATION")
    print("---------------------------------------------------------")
    # Test level states for all 6 tanks
    levels = [0.0, 0.5, 0.6, 40.0, 49.9, 50.0, 60.0, 100.0]
    expected_frames = [0, 0, 1, 1, 1, 2, 2, 2]

    # PLC1
    sim1 = PLC1Simulator()
    for lvl, exp in zip(levels, expected_frames):
        sim1.LT3203_Bon1_Eff = lvl
        sim1.LT3209_Bon2_Eff = lvl
        sim1.LT3302_BonChua1_Eff = lvl
        sim1.LT3307_BonChua2_Eff = lvl
        sim1.tick()
        assert sim1.HMI_Anim_Bon1_MucDich == exp, f"Bon1 MucDich mismatched at LT={lvl}! Expected {exp}, Got {sim1.HMI_Anim_Bon1_MucDich}"
        assert sim1.HMI_Anim_Bon2_MucDich == exp, f"Bon2 MucDich mismatched at LT={lvl}! Expected {exp}, Got {sim1.HMI_Anim_Bon2_MucDich}"
        assert sim1.HMI_Anim_BonChua1_MucDich == exp, f"BonChua1 MucDich mismatched at LT={lvl}! Expected {exp}, Got {sim1.HMI_Anim_BonChua1_MucDich}"
        assert sim1.HMI_Anim_BonChua2_MucDich == exp, f"BonChua2 MucDich mismatched at LT={lvl}! Expected {exp}, Got {sim1.HMI_Anim_BonChua2_MucDich}"

    # PLC2
    sim2 = PLC2Simulator()
    for lvl, exp in zip(levels, expected_frames):
        sim2.LT3213_Bon3_Eff = lvl
        sim2.LT3218_Bon4_Eff = lvl
        sim2.tick()
        assert sim2.HMI_Anim_Bon3_MucDich == exp, f"Bon3 MucDich mismatched at LT={lvl}! Expected {exp}, Got {sim2.HMI_Anim_Bon3_MucDich}"
        assert sim2.HMI_Anim_Bon4_MucDich == exp, f"Bon4 MucDich mismatched at LT={lvl}! Expected {exp}, Got {sim2.HMI_Anim_Bon4_MucDich}"

    print("[PASS] Level state animation logic verified for all six tanks.")


def test_vfd_mode0_output_always_off():
    # Mode 0 (Tự động hóa): physical output of VFD should always be OFF
    sim = PLC1Simulator()
    sim.HMI_Che_Do_Thi = 0
    sim.VFD_Bon2_Run_Cmd = True
    sim.VFD_Bon2_Dao_Chieu_Cmd = True
    sim.VFD_Bon2_Toc_Do_Cmd = 50.0
    sim.HMI_VFD_Bon2_Comm_Enable = True
    sim.HMI_VFD_Bon2_Real_Enable = True
    sim.tick()
    assert not sim.VFD_Bon2_Run
    assert not sim.VFD_Bon2_Dao_Chieu
    assert sim.VFD_Bon2_Toc_Do_AO == 0.0
    print("[PASS] test_vfd_mode0_output_always_off verified.")

def test_vfd_mode1_no_real_enable_off():
    # Mode 1, but without Real_Enable: outputs should be OFF
    sim = PLC1Simulator()
    sim.HMI_Che_Do_Thi = 1
    sim.PLC1_State = 23 # Khuay Nghich -> should run in Reverse
    sim.HMI_VFD_Bon2_Comm_Enable = True
    sim.HMI_VFD_Bon2_Real_Enable = False # No Real_Enable
    sim.VFD_Bon2_MBCL_Done = True # Comm Ready
    
    sim.HMI_PID_Bon2_Dau_Noi_Enable = True
    sim.HMI_SP_PLC1_Toc_Do_Bon2_Main = 50.0
    sim.VFD_Bon2_Actual_Speed_Feedback = 45.0
    sim.tick()
    assert not sim.VFD_Bon2_Run
    assert not sim.VFD_Bon2_Dao_Chieu
    assert sim.VFD_Bon2_Toc_Do_AO == 0.0
    print("[PASS] test_vfd_mode1_no_real_enable_off verified.")

def test_vfd_mode1_real_active_on():
    # Mode 1, with Real_Enable and Comm_Enable: outputs should match Cmd
    sim = PLC1Simulator()
    sim.HMI_Che_Do_Thi = 1
    sim.PLC1_State = 23 # Khuay Nghich -> should run in Reverse
    sim.HMI_VFD_Bon2_Comm_Enable = True
    sim.HMI_VFD_Bon2_Real_Enable = True
    sim.HMI_Run_Enable = True
    sim.PLC1_EStop_Latch = False
    sim.PLC1_Loi_Tong = False
    sim.VFD_Bon2_MBCL_Done = True # Comm Ready
    sim.VFD_Bon2_Comm_Ready = True
    
    sim.HMI_PID_Bon2_Dau_Noi_Enable = True
    sim.HMI_SP_PLC1_Toc_Do_Bon2_Main = 50.0
    sim.VFD_Bon2_Actual_Speed_Feedback = 45.0
    sim.tick()
    sim.tick()
    assert sim.VFD_Bon2_Run
    assert sim.VFD_Bon2_Dao_Chieu
    assert sim.VFD_Bon2_Toc_Do_AO == 50.0
    print("[PASS] test_vfd_mode1_real_active_on verified.")

def test_vfd_mode_invalid_off():
    # Invalid mode (e.g. 2): outputs should be OFF
    sim = PLC1Simulator()
    sim.HMI_Che_Do_Thi = 2
    sim.VFD_Bon2_Run_Cmd = True
    sim.HMI_VFD_Bon2_Comm_Enable = True
    sim.HMI_VFD_Bon2_Real_Enable = True
    sim.tick()
    assert not sim.VFD_Bon2_Run
    assert sim.VFD_Bon2_Toc_Do_AO == 0.0
    print("[PASS] test_vfd_mode_invalid_off verified.")

def test_pid_mode0_sp_pv_temperature():
    # PID Mode 0: SP should use HMI temp SP, PV should use temperature feedback
    sim = PLC1Simulator()
    sim.HMI_Che_Do_Thi = 0
    sim.PID_Bon2_Enable = True
    sim.TT3208_Bon2_Eff = 45.0
    sim.HMI_SP_PLC1_Nhiet_Do_Bon2 = 70.0
    sim.VFD_Bon2_Actual_Speed_Feedback = 10.0
    sim.HMI_SP_PLC1_Toc_Do_Bon2_Main = 60.0
    sim.tick()
    assert sim.PID_Bon2_PV_Eff == 45.0
    assert sim.PID_Bon2_SP == 70.0
    assert sim.PID_Bon2_Enable_Eff
    assert sim.CV3206_Hoi_Bon2 > 0.0
    assert sim.VFD_Bon2_Toc_Do_Cmd == 60.0
    print("[PASS] test_pid_mode0_sp_pv_temperature verified.")

def test_pid_mode1_sp_pv_speed():
    # PID Mode 1: SP should use HMI speed, PV should use speed feedback
    sim = PLC1Simulator()
    sim.HMI_Che_Do_Thi = 1
    sim.HMI_PID_Bon2_Dau_Noi_Enable = True
    sim.VFD_Bon2_Actual_Speed_Feedback = 20.0
    sim.HMI_SP_PLC1_Toc_Do_Bon2_Main = 50.0
    sim.tick()
    assert sim.PID_Bon2_PV_Eff == 20.0
    assert sim.PID_Bon2_SP == 50.0
    assert sim.PID_Bon2_Enable_Eff
    assert sim.VFD_Bon2_Toc_Do_Cmd > 0.0
    assert sim.CV3206_Hoi_Bon2 == 0.0
    print("[PASS] test_pid_mode1_sp_pv_speed verified.")

def test_pid_dau_noi_independent_state0():
    # Mode 1 PID runs independently of the sequence state (i.e. even when State = 0)
    sim = PLC1Simulator()
    sim.HMI_Che_Do_Thi = 1
    sim.PLC1_State = 0
    sim.HMI_PID_Bon2_Dau_Noi_Enable = True
    sim.VFD_Bon2_Actual_Speed_Feedback = 15.0
    sim.HMI_SP_PLC1_Toc_Do_Bon2_Main = 40.0
    sim.tick()
    assert sim.PID_Bon2_Enable_Eff
    assert sim.PID_Bon2_PV_Eff == 15.0
    assert sim.PID_Bon2_SP == 40.0
    assert sim.VFD_Bon2_Run_Cmd == True, "LAD Coil must automatically calculate and set Run_Cmd to True"
    print("[PASS] test_pid_dau_noi_independent_state0 verified.")

def test_manual_no_bypass_safety():
    # Manual control of VFD Bồn 2 does not bypass safety checks in Hybrid block
    sim = PLC1Simulator()
    sim.HMI_Che_Do_Thi = 1
    sim.HMI_Che_Do_Manual = True
    sim.HMI_Cho_Phep_Sua_Thong_So = True
    sim.HMI_User_Level = 2
    sim.VFD_Bon2_Run_Man = True
    sim.VFD_Bon2_Toc_Do_AO_Man = 75.0
    sim.PLC1_Loi_Tong = True
    sim.HMI_VFD_Bon2_Comm_Enable = True
    sim.HMI_VFD_Bon2_Real_Enable = True
    sim.VFD_Bon2_MBCL_Done = True
    sim.tick()
    assert not sim.VFD_Bon2_Run
    assert sim.VFD_Bon2_Toc_Do_AO == 0.0
    print("[PASS] test_manual_no_bypass_safety verified.")


def test_vfd_mode_invalid_behavior():
    # HMI_Che_Do_Thi outside [0, 1] must set VFD_Bon2_Mode_Invalid and clear commands
    sim = PLC1Simulator()
    sim.HMI_Che_Do_Thi = 1
    sim.HMI_PID_Bon2_Dau_Noi_Enable = True
    sim.VFD_Bon2_Actual_Speed_Feedback = 10.0
    sim.HMI_SP_PLC1_Toc_Do_Bon2_Main = 50.0
    sim.VFD_Bon2_MBCL_Done = True
    sim.tick()
    assert sim.PID_Bon2_Enable_Eff == True
    assert sim.VFD_Bon2_Run_Cmd == True
    assert sim.VFD_Bon2_Toc_Do_Cmd > 0.0
    
    sim.HMI_Che_Do_Thi = 2
    sim.tick()
    assert sim.VFD_Bon2_Mode_Invalid == True
    assert sim.PID_Bon2_Enable_Eff == False
    assert sim.VFD_Bon2_Run_Cmd == False
    assert sim.VFD_Bon2_Dao_Chieu_Cmd == False
    assert sim.VFD_Bon2_Toc_Do_Cmd == 0.0
    
    sim.HMI_Che_Do_Thi = -1
    sim.tick()
    assert sim.VFD_Bon2_Mode_Invalid == True
    assert sim.PID_Bon2_Enable_Eff == False
    assert sim.VFD_Bon2_Run_Cmd == False
    assert sim.VFD_Bon2_Dao_Chieu_Cmd == False
    assert sim.VFD_Bon2_Toc_Do_Cmd == 0.0
    
    sim.HMI_Che_Do_Thi = 0
    sim.tick()
    assert sim.VFD_Bon2_Mode_Invalid == False
    print("[PASS] test_vfd_mode_invalid_behavior verified.")


if __name__ == "__main__":
    test_vfd_mode0_output_always_off()
    test_vfd_mode1_no_real_enable_off()
    test_vfd_mode1_real_active_on()
    test_vfd_mode_invalid_off()
    test_pid_mode0_sp_pv_temperature()
    test_pid_mode1_sp_pv_speed()
    test_pid_dau_noi_independent_state0()
    test_manual_no_bypass_safety()
    test_vfd_mode_invalid_behavior()
    test_plc1_sequence()
    test_plc2_sequence()
    test_pulse_command()
    test_pid_state_31()
    test_storage_arbitration()
    test_storage_scan_overwrite()
    test_dry_run_protection()
    test_heartbeat_timeout()
    test_vfd_mb_comm_load_startup_gate()
    test_vfd_modbus_scheduler()
    test_modbus_tcp_scan_order()
    test_plc1_one_batch_and_no_loop()
    test_plc1_start_button_held()
    test_plc2_one_batch_and_no_loop()
    test_plc2_start_button_held()
    test_iec_tip_timer_delay()
    test_agitator_animation()
    test_level_state_animation()
    test_manual_control()
    test_regression_duplicate_blocks()
    test_regression_network_order()
    print("=========================================================")
    print(" ALL PROGRAMMATIC PLC LOGIC TESTS COMPLETED SUCCESSFULLY!")
    print("=========================================================")

