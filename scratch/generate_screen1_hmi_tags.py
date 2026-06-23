# -*- coding: utf-8 -*-
import csv
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

csv_numeric = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\screen1_mapping_dry_run.csv"
csv_graphic = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\graphic_mapping_dry_run.csv"
xml_out = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\Screen1_HMI_Tags.xml"

# Parse numeric HMI tags (24 tags)
numeric_tags = []
if os.path.exists(csv_numeric):
    with open(csv_numeric, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if not row or row[0].startswith('#'):
                continue
            obj_name = row[1].strip()
            if obj_name == "ObjectName" or obj_name == "(missing)" or not obj_name:
                continue
            tag_name = row[8].strip()
            data_type = row[9].strip()
            connection = row[10].strip()
            rationale = row[14].strip() if len(row) > 14 else f"Numeric IOField {obj_name}"
            
            numeric_tags.append({
                "TagName": tag_name,
                "DataType": data_type,
                "Connection": connection,
                "Rationale": rationale
            })
else:
    print(f"Error: Numeric CSV not found at {csv_numeric}")
    sys.exit(1)

# Parse graphic HMI tags (41 tags)
graphic_tags = []
if os.path.exists(csv_graphic):
    with open(csv_graphic, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if not row or row[0].startswith('#'):
                continue
            obj_name = row[0].strip()
            if obj_name == "ObjectName" or obj_name == "(missing)" or not obj_name:
                continue
            tag_name = row[6].strip()
            data_type = row[9].strip()
            connection = row[8].strip()
            rationale = f"Graphic IOField {obj_name} for {tag_name}"
            
            graphic_tags.append({
                "TagName": tag_name,
                "DataType": data_type,
                "Connection": connection,
                "Rationale": rationale
            })
else:
    print(f"Error: Graphic CSV not found at {csv_graphic}")
    sys.exit(1)

# Merge tags and prevent duplicates
merged_tags = {}
for t in numeric_tags:
    merged_tags[t["TagName"]] = t

for t in graphic_tags:
    if t["TagName"] not in merged_tags:
        merged_tags[t["TagName"]] = t
    else:
        # Check connection/type consistency
        existing = merged_tags[t["TagName"]]
        if existing["DataType"] != t["DataType"] or existing["Connection"] != t["Connection"]:
            print(f"Warning: Tag {t['TagName']} duplicate has inconsistent type/connection!")

print(f"Total unique HMI tags to generate: {len(merged_tags)}")

# Generate Tag Table XML
with open(xml_out, "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="utf-8"?>\n')
    f.write('<Document>\n')
    f.write('  <Engineering version="V18" />\n')
    f.write('  <Hmi.Tag.TagTable ID="0">\n')
    f.write('    <AttributeList>\n')
    f.write('      <Name>Screen1_HMI_Tags</Name>\n')
    f.write('    </AttributeList>\n')
    f.write('    <ObjectList>\n')
    
    for i, (tag_name, tag) in enumerate(sorted(merged_tags.items()), start=1):
        tag_id = f"T_{i}"
        
        # Determine Length and Coding based on data type
        dtype = tag["DataType"]
        if dtype == "Real":
            coding = "IEEE754Float"
            length = 4
        elif dtype == "Int":
            coding = "Binary"
            length = 2
        elif dtype == "Bool":
            coding = "Binary"
            length = 1
        else:
            coding = "Binary"
            length = 2
            
        f.write(f'      <Hmi.Tag.Tag ID="{tag_id}" CompositionName="Tags">\n')
        f.write('        <AttributeList>\n')
        f.write('          <AcquisitionTriggerMode>Visible</AcquisitionTriggerMode>\n')
        f.write('          <AddressAccessMode>Symbolic</AddressAccessMode>\n')
        f.write(f'          <Coding>{coding}</Coding>\n')
        f.write('          <ConfirmationType>None</ConfirmationType>\n')
        f.write('          <GmpRelevant>false</GmpRelevant>\n')
        f.write('          <JobNumber>0</JobNumber>\n')
        f.write(f'          <Length>{length}</Length>\n')
        f.write('          <LinearScaling>false</LinearScaling>\n')
        f.write('          <LogicalAddress />\n')
        f.write('          <MandatoryCommenting>false</MandatoryCommenting>\n')
        f.write(f'          <Name>{tag["TagName"]}</Name>\n')
        f.write('          <Persistency>false</Persistency>\n')
        f.write('          <QualityCode>false</QualityCode>\n')
        f.write('          <ScalingHmiHigh>100</ScalingHmiHigh>\n')
        f.write('          <ScalingHmiLow>0</ScalingHmiLow>\n')
        f.write('          <ScalingPlcHigh>10</ScalingPlcHigh>\n')
        f.write('          <ScalingPlcLow>0</ScalingPlcLow>\n')
        f.write('          <StartValue />\n')
        f.write('          <SubstituteValue />\n')
        f.write('          <SubstituteValueUsage>None</SubstituteValueUsage>\n')
        f.write('          <Synchronization>false</Synchronization>\n')
        f.write('          <UpdateMode>ProjectWide</UpdateMode>\n')
        f.write('          <UseMultiplexing>false</UseMultiplexing>\n')
        f.write('        </AttributeList>\n')
        f.write('        <LinkList>\n')
        f.write('          <AcquisitionCycle TargetID="@OpenLink">\n')
        f.write('            <Name>1 s</Name>\n')
        f.write('          </AcquisitionCycle>\n')
        f.write('          <Connection TargetID="@OpenLink">\n')
        f.write(f'            <Name>{tag["Connection"]}</Name>\n')
        f.write('          </Connection>\n')
        f.write('          <ControllerTag TargetID="@OpenLink">\n')
        f.write(f'            <Name>{tag["TagName"]}</Name>\n')
        f.write('          </ControllerTag>\n')
        f.write('          <DataType TargetID="@OpenLink">\n')
        f.write(f'            <Name>{tag["DataType"]}</Name>\n')
        f.write('          </DataType>\n')
        f.write('          <HmiDataType TargetID="@OpenLink">\n')
        f.write(f'            <Name>{tag["DataType"]}</Name>\n')
        f.write('          </HmiDataType>\n')
        f.write('        </LinkList>\n')
        f.write('        <ObjectList>\n')
        f.write(f'          <MultilingualText ID="C_{i}" CompositionName="Comment">\n')
        f.write('            <ObjectList>\n')
        f.write(f'              <MultilingualTextItem ID="CI_{i}" CompositionName="Items">\n')
        f.write('                <AttributeList>\n')
        f.write('                  <Culture>en-US</Culture>\n')
        f.write(f'                  <Text>{tag["Rationale"]}</Text>\n')
        f.write('                </AttributeList>\n')
        f.write('              </MultilingualTextItem>\n')
        f.write('            </ObjectList>\n')
        f.write('          </MultilingualText>\n')
        f.write('        </ObjectList>\n')
        f.write('      </Hmi.Tag.Tag>\n')
        
    f.write('    </ObjectList>\n')
    f.write('  </Hmi.Tag.TagTable>\n')
    f.write('</Document>\n')

print(f"Successfully generated HMI tag XML with {len(merged_tags)} tags.")
