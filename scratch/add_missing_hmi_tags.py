import xml.etree.ElementTree as ET

xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\Screen1_HMI_Tags.xml"

tree = ET.parse(xml_path)
root = tree.getroot()

# The ObjectList of Hmi.Tag.TagTable is the parent of Hmi.Tag.Tag elements
tag_table = root.find(".//Hmi.Tag.TagTable")
if tag_table is None:
    print("Error: TagTable not found in XML!")
    exit(1)

object_list = tag_table.find("ObjectList")
if object_list is None:
    print("Error: ObjectList not found under TagTable!")
    exit(1)

# Helper to create a Hmi.Tag.Tag element
def create_internal_tag(tag_id, name, coding, length, dtype_name, comment_text):
    tag = ET.Element("Hmi.Tag.Tag", attrib={"ID": tag_id, "CompositionName": "Tags"})
    
    # AttributeList
    attrs = ET.SubElement(tag, "AttributeList")
    ET.SubElement(attrs, "AcquisitionTriggerMode").text = "Visible"
    ET.SubElement(attrs, "AddressAccessMode").text = "Symbolic"
    ET.SubElement(attrs, "Coding").text = coding
    ET.SubElement(attrs, "ConfirmationType").text = "None"
    ET.SubElement(attrs, "GmpRelevant").text = "false"
    ET.SubElement(attrs, "JobNumber").text = "0"
    ET.SubElement(attrs, "Length").text = str(length)
    ET.SubElement(attrs, "LinearScaling").text = "false"
    ET.SubElement(attrs, "LogicalAddress")
    ET.SubElement(attrs, "MandatoryCommenting").text = "false"
    ET.SubElement(attrs, "Name").text = name
    ET.SubElement(attrs, "Persistency").text = "false"
    ET.SubElement(attrs, "QualityCode").text = "false"
    ET.SubElement(attrs, "ScalingHmiHigh").text = "100"
    ET.SubElement(attrs, "ScalingHmiLow").text = "0"
    ET.SubElement(attrs, "ScalingPlcHigh").text = "10"
    ET.SubElement(attrs, "ScalingPlcLow").text = "0"
    ET.SubElement(attrs, "StartValue")
    ET.SubElement(attrs, "SubstituteValue")
    ET.SubElement(attrs, "SubstituteValueUsage").text = "None"
    ET.SubElement(attrs, "Synchronization").text = "false"
    ET.SubElement(attrs, "UpdateMode").text = "ProjectWide"
    ET.SubElement(attrs, "UseMultiplexing").text = "false"
    
    # LinkList
    links = ET.SubElement(tag, "LinkList")
    acq = ET.SubElement(links, "AcquisitionCycle", attrib={"TargetID": "@OpenLink"})
    ET.SubElement(acq, "Name").text = "1 s"
    dtype = ET.SubElement(links, "DataType", attrib={"TargetID": "@OpenLink"})
    ET.SubElement(dtype, "Name").text = dtype_name
    hmi_dtype = ET.SubElement(links, "HmiDataType", attrib={"TargetID": "@OpenLink"})
    ET.SubElement(hmi_dtype, "Name").text = dtype_name
    
    # ObjectList
    obj_list = ET.SubElement(tag, "ObjectList")
    comment = ET.SubElement(obj_list, "MultilingualText", attrib={"ID": f"C_{tag_id}", "CompositionName": "Comment"})
    comment_items = ET.SubElement(comment, "ObjectList")
    comment_item = ET.SubElement(comment_items, "MultilingualTextItem", attrib={"ID": f"CI_{tag_id}", "CompositionName": "Items"})
    comment_item_attrs = ET.SubElement(comment_item, "AttributeList")
    ET.SubElement(comment_item_attrs, "Culture").text = "en-US"
    ET.SubElement(comment_item_attrs, "Text").text = comment_text
    
    return tag

# Create the 4 missing tags
missing_tags = [
    ("T_101", "GIA_TRI_NHIET_DO_DOC_VE", "IEEE754Float", 4, "Real", "Dummy internal tag for bon tron 1 temperature"),
    ("T_102", "nguyen_lieu_tron_1", "Binary", 1, "Bool", "Dummy internal tag for bon tron 1 material"),
    ("T_103", "cap_nuoc_tron_1", "Binary", 1, "Bool", "Dummy internal tag for bon tron 1 water"),
    ("T_104", "start", "Binary", 1, "Bool", "Dummy internal tag for bon tron 1 start button"),
]

for tag_id, name, coding, length, dtype_name, comment in missing_tags:
    # Check if tag already exists in the file to avoid duplicates
    existing = False
    for tag_el in object_list.findall("Hmi.Tag.Tag"):
        name_el = tag_el.find("AttributeList/Name")
        if name_el is not None and name_el.text == name:
            existing = True
            break
            
    if existing:
        print(f"Tag {name} already exists in the file. Skipping.")
    else:
        new_tag_el = create_internal_tag(tag_id, name, coding, length, dtype_name, comment)
        object_list.append(new_tag_el)
        print(f"Added tag {name} (ID: {tag_id}) to Screen1_HMI_Tags.xml")

# Save file with indentation
ET.indent(tree)
tree.write(xml_path, encoding="utf-8", xml_declaration=True)
print("Saved modified Screen1_HMI_Tags.xml")
