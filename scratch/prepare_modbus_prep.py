# -*- coding: utf-8 -*-
import os

def generate_tags_xml(table_name, tags_list):
    blocks = []
    next_id = 1
    for name, dtype, address in tags_list:
        tag_id = next_id
        text_id = next_id + 1
        text_item_id = next_id + 2
        next_id += 3
        blocks.append(f'''      <SW.Tags.PlcTag ID="{tag_id}" CompositionName="Tags">
        <AttributeList>
          <DataTypeName>{dtype}</DataTypeName>
          <ExternalAccessible>true</ExternalAccessible>
          <ExternalVisible>true</ExternalVisible>
          <ExternalWritable>true</ExternalWritable>
          <LogicalAddress>{address}</LogicalAddress>
          <Name>{name}</Name>
        </AttributeList>
        <ObjectList>
          <MultilingualText ID="{text_id}" CompositionName="Comment">
            <ObjectList>
              <MultilingualTextItem ID="{text_item_id}" CompositionName="Items">
                <AttributeList>
                  <Culture>en-US</Culture>
                  <Text>{name} Modbus Tag</Text>
                </AttributeList>
              </MultilingualTextItem>
            </ObjectList>
          </MultilingualText>
        </ObjectList>
      </SW.Tags.PlcTag>''')
    
    return f'''<?xml version="1.0" encoding="utf-8"?>
<Document>
  <Engineering version="V18" />
  <DocumentInfo>
    <Created>2026-06-07T00:00:00Z</Created>
    <ExportSetting>WithDefaults</ExportSetting>
  </DocumentInfo>
  <SW.Tags.PlcTagTable ID="0">
    <AttributeList>
      <Name>{table_name}</Name>
    </AttributeList>
    <ObjectList>
{chr(10).join(blocks)}
    </ObjectList>
  </SW.Tags.PlcTagTable>
</Document>
'''

def generate_db_xml(db_name, db_number, members_xml, is_standard=True):
    layout = "Standard" if is_standard else "Optimized"
    autonumber = "false" if db_number is not None else "true"
    number_attr = f"<Number>{db_number}</Number>" if db_number is not None else ""
    
    return f'''<?xml version="1.0" encoding="utf-8"?>
<Document>
  <Engineering version="V18" />
  <DocumentInfo>
    <Created>2026-06-07T00:00:00Z</Created>
    <ExportSetting>WithDefaults</ExportSetting>
  </DocumentInfo>
  <SW.Blocks.GlobalDB ID="0">
    <AttributeList>
      <AutoNumber>{autonumber}</AutoNumber>
      <HeaderAuthor />
      <HeaderFamily />
      <HeaderName />
      <HeaderVersion>0.1</HeaderVersion>
      <Interface>
        <Sections xmlns="http://www.siemens.com/automation/Openness/SW/Interface/v5">
          <Section Name="Static">
{members_xml}
          </Section>
        </Sections>
      </Interface>
      <IsOnlyStoredInLoadMemory>false</IsOnlyStoredInLoadMemory>
      <IsWriteProtectedInAS>false</IsWriteProtectedInAS>
      <MemoryLayout>{layout}</MemoryLayout>
      <Name>{db_name}</Name>
      <Namespace />
      {number_attr}
      <ProgrammingLanguage>DB</ProgrammingLanguage>
    </AttributeList>
    <ObjectList>
      <MultilingualText ID="1" CompositionName="Comment">
        <ObjectList>
          <MultilingualTextItem ID="2" CompositionName="Items">
            <AttributeList>
              <Culture>en-US</Culture>
              <Text>DB communication via Modbus TCP</Text>
            </AttributeList>
          </MultilingualTextItem>
        </ObjectList>
      </MultilingualText>
      <MultilingualText ID="3" CompositionName="Title">
        <ObjectList>
          <MultilingualTextItem ID="4" CompositionName="Items">
            <AttributeList>
              <Culture>en-US</Culture>
              <Text>{db_name}</Text>
            </AttributeList>
          </MultilingualTextItem>
        </ObjectList>
      </MultilingualText>
    </ObjectList>
  </SW.Blocks.GlobalDB>
</Document>'''

# Members for DB_MB_Client_Data
db_mb_client_data_members = '''            <Member Name="Send_Words" Datatype="Array[0..2] of Int" Remanence="NonRetain" Accessibility="Public">
              <AttributeList>
                <BooleanAttribute Name="ExternalAccessible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalVisible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalWritable" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="SetPoint" SystemDefined="true">false</BooleanAttribute>
              </AttributeList>
            </Member>
            <Member Name="Recv_Words" Datatype="Array[0..9] of Int" Remanence="NonRetain" Accessibility="Public">
              <AttributeList>
                <BooleanAttribute Name="ExternalAccessible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalVisible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalWritable" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="SetPoint" SystemDefined="true">false</BooleanAttribute>
              </AttributeList>
            </Member>'''

# Members for DB_MB_Client_Conn (with start values)
db_mb_client_conn_members = '''            <Member Name="MB_TCP" Datatype="TCON_IP_v4" Remanence="NonRetain" Accessibility="Public">
              <AttributeList>
                <BooleanAttribute Name="ExternalAccessible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalVisible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalWritable" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="SetPoint" SystemDefined="true">false</BooleanAttribute>
              </AttributeList>
              <Sections>
                <Section Name="None">
                  <Member Name="InterfaceId" Datatype="HW_ANY">
                    <StartValue>64</StartValue>
                  </Member>
                  <Member Name="ID" Datatype="CONN_OUC">
                    <StartValue>5</StartValue>
                  </Member>
                  <Member Name="ConnectionType" Datatype="Byte">
                    <StartValue>11</StartValue>
                  </Member>
                  <Member Name="ActiveEstablished" Datatype="Bool">
                    <StartValue>true</StartValue>
                  </Member>
                  <Member Name="RemoteAddress" Datatype="Array[1..4] of Byte">
                    <Sections>
                      <Section Name="None">
                        <Member Name="1" Datatype="Byte"><StartValue>192</StartValue></Member>
                        <Member Name="2" Datatype="Byte"><StartValue>168</StartValue></Member>
                        <Member Name="3" Datatype="Byte"><StartValue>0</StartValue></Member>
                        <Member Name="4" Datatype="Byte"><StartValue>2</StartValue></Member>
                      </Section>
                    </Sections>
                  </Member>
                  <Member Name="RemotePort" Datatype="UInt">
                    <StartValue>502</StartValue>
                  </Member>
                  <Member Name="LocalPort" Datatype="UInt">
                    <StartValue>0</StartValue>
                  </Member>
                </Section>
              </Sections>
            </Member>'''

# Members for DB_MB_Client_Conn (without start values in case the first one fails)
db_mb_client_conn_no_start_members = '''            <Member Name="MB_TCP" Datatype="TCON_IP_v4" Remanence="NonRetain" Accessibility="Public">
              <AttributeList>
                <BooleanAttribute Name="ExternalAccessible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalVisible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalWritable" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="SetPoint" SystemDefined="true">false</BooleanAttribute>
              </AttributeList>
            </Member>'''

# Members for DB_Modbus_Holding_Register
db_modbus_holding_members = '''            <Member Name="CmdSeq" Datatype="Int" Remanence="NonRetain" Accessibility="Public">
              <AttributeList>
                <BooleanAttribute Name="ExternalAccessible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalVisible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalWritable" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="SetPoint" SystemDefined="true">false</BooleanAttribute>
              </AttributeList>
            </Member>
            <Member Name="CmdBools" Datatype="Int" Remanence="NonRetain" Accessibility="Public">
              <AttributeList>
                <BooleanAttribute Name="ExternalAccessible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalVisible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalWritable" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="SetPoint" SystemDefined="true">false</BooleanAttribute>
              </AttributeList>
            </Member>
            <Member Name="Heartbeat_Client" Datatype="Int" Remanence="NonRetain" Accessibility="Public">
              <AttributeList>
                <BooleanAttribute Name="ExternalAccessible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalVisible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalWritable" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="SetPoint" SystemDefined="true">false</BooleanAttribute>
              </AttributeList>
            </Member>
            <Member Name="AckSeq" Datatype="Int" Remanence="NonRetain" Accessibility="Public">
              <AttributeList>
                <BooleanAttribute Name="ExternalAccessible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalVisible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalWritable" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="SetPoint" SystemDefined="true">false</BooleanAttribute>
              </AttributeList>
            </Member>
            <Member Name="StatusBools" Datatype="Int" Remanence="NonRetain" Accessibility="Public">
              <AttributeList>
                <BooleanAttribute Name="ExternalAccessible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalVisible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalWritable" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="SetPoint" SystemDefined="true">false</BooleanAttribute>
              </AttributeList>
            </Member>
            <Member Name="State" Datatype="Int" Remanence="NonRetain" Accessibility="Public">
              <AttributeList>
                <BooleanAttribute Name="ExternalAccessible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalVisible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalWritable" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="SetPoint" SystemDefined="true">false</BooleanAttribute>
              </AttributeList>
            </Member>
            <Member Name="PID_Bon4_SP" Datatype="Real" Remanence="NonRetain" Accessibility="Public">
              <AttributeList>
                <BooleanAttribute Name="ExternalAccessible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalVisible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalWritable" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="SetPoint" SystemDefined="true">false</BooleanAttribute>
              </AttributeList>
            </Member>
            <Member Name="PID_Bon4_PV" Datatype="Real" Remanence="NonRetain" Accessibility="Public">
              <AttributeList>
                <BooleanAttribute Name="ExternalAccessible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalVisible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalWritable" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="SetPoint" SystemDefined="true">false</BooleanAttribute>
              </AttributeList>
            </Member>
            <Member Name="PID_Bon4_CV" Datatype="Real" Remanence="NonRetain" Accessibility="Public">
              <AttributeList>
                <BooleanAttribute Name="ExternalAccessible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalVisible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalWritable" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="SetPoint" SystemDefined="true">false</BooleanAttribute>
              </AttributeList>
            </Member>
            <Member Name="Heartbeat_Server" Datatype="Int" Remanence="NonRetain" Accessibility="Public">
              <AttributeList>
                <BooleanAttribute Name="ExternalAccessible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalVisible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalWritable" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="SetPoint" SystemDefined="true">false</BooleanAttribute>
              </AttributeList>
            </Member>'''

# Members for DB_MB_Server_Conn (with start values)
db_mb_server_conn_members = '''            <Member Name="MB_TCP_SERVER" Datatype="TCON_IP_v4" Remanence="NonRetain" Accessibility="Public">
              <AttributeList>
                <BooleanAttribute Name="ExternalAccessible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalVisible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalWritable" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="SetPoint" SystemDefined="true">false</BooleanAttribute>
              </AttributeList>
              <Sections>
                <Section Name="None">
                  <Member Name="InterfaceId" Datatype="HW_ANY">
                    <StartValue>64</StartValue>
                  </Member>
                  <Member Name="ID" Datatype="CONN_OUC">
                    <StartValue>5</StartValue>
                  </Member>
                  <Member Name="ConnectionType" Datatype="Byte">
                    <StartValue>11</StartValue>
                  </Member>
                  <Member Name="ActiveEstablished" Datatype="Bool">
                    <StartValue>false</StartValue>
                  </Member>
                  <Member Name="RemoteAddress" Datatype="Array[1..4] of Byte">
                    <Sections>
                      <Section Name="None">
                        <Member Name="1" Datatype="Byte"><StartValue>192</StartValue></Member>
                        <Member Name="2" Datatype="Byte"><StartValue>168</StartValue></Member>
                        <Member Name="3" Datatype="Byte"><StartValue>0</StartValue></Member>
                        <Member Name="4" Datatype="Byte"><StartValue>1</StartValue></Member>
                      </Section>
                    </Sections>
                  </Member>
                  <Member Name="RemotePort" Datatype="UInt">
                    <StartValue>0</StartValue>
                  </Member>
                  <Member Name="LocalPort" Datatype="UInt">
                    <StartValue>502</StartValue>
                  </Member>
                </Section>
              </Sections>
            </Member>'''

# Members for DB_MB_Server_Conn (without start values)
db_mb_server_conn_no_start_members = '''            <Member Name="MB_TCP_SERVER" Datatype="TCON_IP_v4" Remanence="NonRetain" Accessibility="Public">
              <AttributeList>
                <BooleanAttribute Name="ExternalAccessible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalVisible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalWritable" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="SetPoint" SystemDefined="true">false</BooleanAttribute>
              </AttributeList>
            </Member>'''

# Create folders
os.makedirs("output_temp/PLC_1_Modbus_Prep", exist_ok=True)
os.makedirs("output_temp/PLC_2_Modbus_Prep", exist_ok=True)

# PLC_1 Tags
plc1_tags = [
    ("Clock_1Hz", "Bool", "%M0.5"),
    ("FirstScan", "Bool", "%M1.0"),
    ("MB_Write_Req", "Bool", "%M10.0"),
    ("MB_Read_Req", "Bool", "%M10.1"),
    ("MB_Write_Done", "Bool", "%M10.2"),
    ("MB_Write_Busy", "Bool", "%M10.3"),
    ("MB_Write_Error", "Bool", "%M10.4"),
    ("MB_Read_Done", "Bool", "%M10.5"),
    ("MB_Read_Busy", "Bool", "%M10.6"),
    ("MB_Read_Error", "Bool", "%M10.7"),
    ("MB_Write_Status", "Word", "%MW12"),
    ("MB_Read_Status", "Word", "%MW14"),
]

# PLC_2 Tags
plc2_tags = [
    ("MB_Server_NDR", "Bool", "%M10.0"),
    ("MB_Server_DR", "Bool", "%M10.1"),
    ("MB_Server_Error", "Bool", "%M10.2"),
    ("MB_Server_Status", "Word", "%MW12"),
]

# Write PLC_1 files
with open("output_temp/PLC_1_Modbus_Prep/AI_Tags.xml", "w", encoding="utf-8") as f:
    f.write(generate_tags_xml("AI_Tags", plc1_tags))

with open("output_temp/PLC_1_Modbus_Prep/DB_MB_Client_Data.xml", "w", encoding="utf-8") as f:
    f.write(generate_db_xml("DB_MB_Client_Data", 10, db_mb_client_data_members, is_standard=True))

with open("output_temp/PLC_1_Modbus_Prep/DB_MB_Client_Conn.xml", "w", encoding="utf-8") as f:
    f.write(generate_db_xml("DB_MB_Client_Conn", 11, db_mb_client_conn_no_start_members, is_standard=True))

# Write PLC_2 files
with open("output_temp/PLC_2_Modbus_Prep/AI_Tags.xml", "w", encoding="utf-8") as f:
    f.write(generate_tags_xml("AI_Tags", plc2_tags))

with open("output_temp/PLC_2_Modbus_Prep/DB_Modbus_Holding_Register.xml", "w", encoding="utf-8") as f:
    f.write(generate_db_xml("DB_Modbus_Holding_Register", 12, db_modbus_holding_members, is_standard=True))

with open("output_temp/PLC_2_Modbus_Prep/DB_MB_Server_Conn.xml", "w", encoding="utf-8") as f:
    f.write(generate_db_xml("DB_MB_Server_Conn", 13, db_mb_server_conn_no_start_members, is_standard=True))

print("XML generation finished!")
