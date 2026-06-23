import xml.etree.ElementTree as ET

tree = ET.parse(r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\Screen1_HMI_Tags.xml")
root = tree.getroot()

found_time_tag = False
for elem in root.iter():
    tag_local = elem.tag.split('}')[-1]
    if tag_local == "Hmi.Tag.Tag":
        # check if it is of type Time
        dyn_type = elem.find(".//{*}DataType")
        # since we might have namespaces, let's search manually
        dtype_name = ""
        for item in elem.iter():
            if item.tag.split('}')[-1] == "DataType":
                name_el = item.find(".//{*}Name")
                if name_el is not None:
                    dtype_name = name_el.text
                    break
        
        if dtype_name == "Time":
            found_time_tag = True
            print("TIME TAG FOUND!")
            for child in list(elem):
                child_local = child.tag.split('}')[-1]
                print("  CHILD:", child.tag, "->", child_local)
                if child_local == "AttributeList":
                    for attr in list(child):
                        attr_local = attr.tag.split('}')[-1]
                        print("    ATTR:", attr_local, ":", attr.text)
                elif child_local == "LinkList":
                    for link in list(child):
                        link_local = link.tag.split('}')[-1]
                        print("    LINK:", link_local, ":")
                        for lchild in list(link):
                            print("      ", lchild.tag.split('}')[-1], ":", lchild.text)
            break

if not found_time_tag:
    print("No HMI tag of type Time found in Screen1_HMI_Tags.xml")
