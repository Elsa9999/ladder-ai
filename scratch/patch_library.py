# -*- coding: utf-8 -*-
import re
import subprocess

file_path = "Ladder/Agent_LAD_Library.py"

# Restore original content to start fresh
subprocess.run(["git", "checkout", file_path])

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Define format_symbol_path and get_integer_type
helper_funcs = """def format_symbol_path(path_str):
    components = path_str.split(".")
    xml_parts = []
    for x in components:
        if x.startswith("%") and len(x) > 2:
            slice_type = x[1].lower()
            slice_idx = x[2:]
            if xml_parts:
                xml_parts[-1] = xml_parts[-1].replace("<Component ", f'<Component SliceAccessModifier="{slice_type}{slice_idx}" ', 1)
        # Check if x has array syntax like "Name[index]"
        elif "[" in x and x.endswith("]"):
            base_name = x[:x.find("[")]
            index_str = x[x.find("[")+1:-1]
            xml_parts.append(
                f'<Component Name="{base_name}" AccessModifier="Array">'
                f'<Access Scope="LiteralConstant">'
                f'<Constant>'
                f'<ConstantType>DInt</ConstantType>'
                f'<ConstantValue>{index_str}</ConstantValue>'
                f'</Constant>'
                f'</Access>'
                f'</Component>'
            )
        else:
            xml_parts.append(f'<Component Name="{x}" />')
    return "".join(xml_parts)

def get_integer_type(value_str):
    try:
        int_val = int(value_str)
        if -32768 <= int_val <= 32767:
            return "Int"
        elif 32768 <= int_val <= 65535:
            return "UDInt"
        elif -2147483648 <= int_val <= 2147483647:
            return "DInt"
        else:
            return "UDInt"
    except ValueError:
        return "Int"

class UIDGen:"""

content = content.replace("class UIDGen:", helper_funcs)

# Perform replacement for all splitjoin occurrences line-by-line
lines = content.splitlines()
pattern = r'""\.join\(\s*(?:\[\s*)?.*?for\s+x\s+in\s+(.*?)\.split\((?:"\."|\'\.\')\)(?:\s*\])?\s*\)'

for i, line in enumerate(lines):
    if 'split(' in line and 'Component Name' in line:
        m = re.search(pattern, line)
        if m:
            expr = m.group(1)
            line_new = re.sub(pattern, f'format_symbol_path({expr})', line)
            lines[i] = line_new

content = "\n".join(lines)

# Perform exact string replacements for the hardcoded "Int" type conversions:
content = content.replace('ctype = "Real" if is_real else "Int"', 'ctype = "Real" if is_real else get_integer_type(value_str)')
content = content.replace('ctype_str = "Real" if is_real else "Int"', 'ctype_str = "Real" if is_real else get_integer_type(in2_raw)')
content = content.replace('ctype_str = "Real" if is_real1 else "Int"', 'ctype_str = "Real" if is_real1 else get_integer_type(in1_raw)')
content = content.replace('ctype_str = "Real" if is_real2 else "Int"', 'ctype_str = "Real" if is_real2 else get_integer_type(in2_raw)')
content = content.replace('ctype_str = "Real" if is_real1 else "Int"', 'ctype_str = "Real" if is_real1 else get_integer_type(in1_raw)')
content = content.replace('ctype_str = "Real" if is_real1 else "Int"', 'ctype_str = "Real" if is_real1 else get_integer_type(in1_raw)')
content = content.replace('ctype_str = "Real" if is_real else "Int"', 'ctype_str = "Real" if is_real else get_integer_type(tag_raw)')

# Fix the pin_types checks: only return LiteralConstant if value_str is numeric!
original_pin_types_check = """        if pin_name in pin_types:
            return f'<Access Scope="LiteralConstant" UId="{tag_uid}"><Constant><ConstantType>{pin_types[pin_name]}</ConstantType><ConstantValue>{value_str}</ConstantValue></Constant></Access>'"""

replacement_pin_types_check = """        if pin_name in pin_types:
            try:
                float(value_str)
                return f'<Access Scope="LiteralConstant" UId="{tag_uid}"><Constant><ConstantType>{pin_types[pin_name]}</ConstantType><ConstantValue>{value_str}</ConstantValue></Constant></Access>'
            except ValueError:
                pass"""

content = content.replace(original_pin_types_check, replacement_pin_types_check)

# Add "OPEN" / OpenCon logic for GENERIC block calls
original_generic_iopins = """                # Process Inputs
                for pin_name, tag_raw in inputs.items():
                    tag_uid = self.uid_gen.next()
                    accesses.append(self._get_access_xml(pin_name, tag_raw, tag_uid))
                    w_in = self.uid_gen.next()
                    wires.append(f'<Wire UId="{w_in}"><IdentCon UId="{tag_uid}" /><NameCon UId="{gen_uid}" Name="{pin_name}" /></Wire>')

                # Process Outputs
                for pin_name, tag_raw in outputs.items():
                    tag_uid = self.uid_gen.next()
                    accesses.append(
                        f'<Access Scope="GlobalVariable" UId="{tag_uid}">'
                        f'<Symbol>{ format_symbol_path(tag_raw) }</Symbol>'
                        f'</Access>'
                    )
                    w_out = self.uid_gen.next()
                    wires.append(f'<Wire UId="{w_out}"><NameCon UId="{gen_uid}" Name="{pin_name}" /><IdentCon UId="{tag_uid}" /></Wire>')"""

replacement_generic_iopins = """                # Process Inputs
                for pin_name, tag_raw in inputs.items():
                    if tag_raw == "OPEN" or tag_raw == "" or tag_raw is None:
                        open_uid = self.uid_gen.next()
                        w_in = self.uid_gen.next()
                        wires.append(f'<Wire UId="{w_in}"><OpenCon UId="{open_uid}" /><NameCon UId="{gen_uid}" Name="{pin_name}" /></Wire>')
                    else:
                        tag_uid = self.uid_gen.next()
                        accesses.append(self._get_access_xml(pin_name, tag_raw, tag_uid))
                        w_in = self.uid_gen.next()
                        wires.append(f'<Wire UId="{w_in}"><IdentCon UId="{tag_uid}" /><NameCon UId="{gen_uid}" Name="{pin_name}" /></Wire>')

                # Process Outputs
                for pin_name, tag_raw in outputs.items():
                    if tag_raw == "OPEN" or tag_raw == "" or tag_raw is None:
                        open_uid = self.uid_gen.next()
                        w_out = self.uid_gen.next()
                        wires.append(f'<Wire UId="{w_out}"><NameCon UId="{gen_uid}" Name="{pin_name}" /><OpenCon UId="{open_uid}" /></Wire>')
                    else:
                        tag_uid = self.uid_gen.next()
                        accesses.append(
                            f'<Access Scope="GlobalVariable" UId="{tag_uid}">'
                            f'<Symbol>{ format_symbol_path(tag_raw) }</Symbol>'
                            f'</Access>'
                        )
                        w_out = self.uid_gen.next()
                        wires.append(f'<Wire UId="{w_out}"><NameCon UId="{gen_uid}" Name="{pin_name}" /><IdentCon UId="{tag_uid}" /></Wire>')"""

content = content.replace(original_generic_iopins, replacement_generic_iopins)

# Add _get_symbol_access_xml method definition to TIALadderBuilder
content = content.replace(
    '        self.uid_gen = UIDGen(start=20)',
    '''        self.uid_gen = UIDGen(start=20)

    def _get_symbol_access_xml(self, value, tag_uid):
        value_str = str(value)
        if value_str.startswith("#"):
            comp_str = format_symbol_path(value_str[1:])
            return f'<Access Scope="LocalVariable" UId="{tag_uid}"><Symbol>{comp_str}</Symbol></Access>'
        else:
            comp_str = format_symbol_path(value_str)
            return f'<Access Scope="GlobalVariable" UId="{tag_uid}"><Symbol>{comp_str}</Symbol></Access>\''''
)

# Replace in _get_access_xml to support local variables
content = content.replace(
    """        except ValueError:
            # Symbolic name with dots
            comp_str = format_symbol_path(value_str)
            return f'<Access Scope="GlobalVariable" UId="{tag_uid}"><Symbol>{comp_str}</Symbol></Access>'""",
    """        except ValueError:
            # Symbolic name with dots
            return self._get_symbol_access_xml(value_str, tag_uid)"""
)

# Replace all hardcoded GlobalVariable accesses in blocks
content = content.replace(
    '''                accesses.append(
                    f'<Access Scope="GlobalVariable" UId="{var_uid}">'
                    f'<Symbol>{ format_symbol_path(comp[1]) }</Symbol>'
                    f'</Access>'
                )''',
    '                accesses.append(self._get_symbol_access_xml(comp[1], var_uid))'
)

content = content.replace(
    '                accesses.append(f\'<Access Scope="GlobalVariable" UId="{var1_uid}"><Symbol>{ format_symbol_path(tag1) }</Symbol></Access>\')\n                accesses.append(f\'<Access Scope="GlobalVariable" UId="{var2_uid}"><Symbol>{ format_symbol_path(tag2) }</Symbol></Access>\')',
    '                accesses.append(self._get_symbol_access_xml(tag1, var1_uid))\n                accesses.append(self._get_symbol_access_xml(tag2, var2_uid))'
)

content = content.replace(
    '                accesses.append(f\'<Access Scope="GlobalVariable" UId="{var1_uid}"><Symbol>{ format_symbol_path(tag1) }</Symbol></Access>\')\n                accesses.append(f\'<Access Scope="GlobalVariable" UId="{var2_uid}"><Symbol>{ format_symbol_path(tag2) }</Symbol></Access>\')\n                accesses.append(f\'<Access Scope="GlobalVariable" UId="{var3_uid}"><Symbol>{ format_symbol_path(tag3) }</Symbol></Access>\')',
    '                accesses.append(self._get_symbol_access_xml(tag1, var1_uid))\n                accesses.append(self._get_symbol_access_xml(tag2, var2_uid))\n                accesses.append(self._get_symbol_access_xml(tag3, var3_uid))'
)

content = content.replace(
    '                    accesses.append(f\'<Access Scope="GlobalVariable" UId="{var_uid}"><Symbol>{ format_symbol_path(param_tag) }</Symbol></Access>\')',
    '                    accesses.append(self._get_symbol_access_xml(param_tag, var_uid))'
)

content = content.replace(
    '                accesses.append(f\'<Access Scope="GlobalVariable" UId="{var_uid}"><Symbol>{ format_symbol_path(tag) }</Symbol></Access>\')',
    '                accesses.append(self._get_symbol_access_xml(tag, var_uid))'
)

content = content.replace(
    '''                # in1 is always a GlobalVariable
                accesses.append(
                    f'<Access Scope="GlobalVariable" UId="{in1_uid}">'
                    f'<Symbol>{ format_symbol_path(in1_tag) }</Symbol>'
                    f'</Access>'
                )''',
    '''                # in1 is always a GlobalVariable
                accesses.append(self._get_symbol_access_xml(in1_tag, in1_uid))'''
)

content = content.replace(
    '''                else:
                    accesses.append(
                        f'<Access Scope="GlobalVariable" UId="{in2_uid}">'
                        f'<Symbol>{ format_symbol_path(in2_raw) }</Symbol>'
                        f'</Access>'
                    )''',
    '''                else:
                    accesses.append(self._get_symbol_access_xml(in2_raw, in2_uid))'''
)

content = content.replace(
    '''                accesses.append(
                    f'<Access Scope="GlobalVariable" UId="{dst_uid}">'
                    f'<Symbol>{ format_symbol_path(dst_tag) }</Symbol>'
                    f'</Access>'
                )''',
    '                accesses.append(self._get_symbol_access_xml(dst_tag, dst_uid))'
)

# MATH, MATH1, CONV in1, in2, out
content = content.replace(
    '''                else:
                    accesses.append(
                        f'<Access Scope="GlobalVariable" UId="{in1_uid}">'
                        f'<Symbol>{ format_symbol_path(in1_raw) }</Symbol>'
                        f'</Access>'
                    )''',
    '''                else:
                    accesses.append(self._get_symbol_access_xml(in1_raw, in1_uid))'''
)

content = content.replace(
    '''                # OUT
                accesses.append(
                    f'<Access Scope="GlobalVariable" UId="{out_uid}">'
                    f'<Symbol>{ format_symbol_path(out_tag) }</Symbol>'
                    f'</Access>'
                )''',
    '''                # OUT
                accesses.append(self._get_symbol_access_xml(out_tag, out_uid))'''
)

# PID_Compact
content = content.replace(
    '''                        else:
                            accesses.append(
                                f'<Access Scope="GlobalVariable" UId="{tag_uid}">'
                                f'<Symbol>{ format_symbol_path(tag_raw) }</Symbol>'
                                f'</Access>'
                            )''',
    '''                        else:
                            accesses.append(self._get_symbol_access_xml(tag_raw, tag_uid))'''
)

content = content.replace(
    '''                        accesses.append(
                            f'<Access Scope="GlobalVariable" UId="{tag_uid}">'
                            f'<Symbol>{ format_symbol_path(tag_raw) }</Symbol>'
                            f'</Access>'
                        )''',
    '                        accesses.append(self._get_symbol_access_xml(tag_raw, tag_uid))'
)

# TON
content = content.replace(
    '''                else:
                    accesses.append(
                        f'<Access Scope="GlobalVariable" UId="{pt_uid}">'
                        f'<Symbol>{ format_symbol_path(time_val) }</Symbol>'
                        f'</Access>'
                    )''',
    '''                else:
                    accesses.append(self._get_symbol_access_xml(time_val, pt_uid))'''
)

content = content.replace(
    '                # Wire Q output\n                if q_tag:\n                    w_q = self.uid_gen.next()\n                    q_uid = self.uid_gen.next()\n                    accesses.append(f\'<Access Scope="GlobalVariable" UId="{q_uid}"><Symbol>{ format_symbol_path(q_tag) }</Symbol></Access>\')',
    '                # Wire Q output\n                if q_tag:\n                    w_q = self.uid_gen.next()\n                    q_uid = self.uid_gen.next()\n                    accesses.append(self._get_symbol_access_xml(q_tag, q_uid))'
)

content = content.replace(
    '                # Wire ET output\n                if et_tag:\n                    w_et = self.uid_gen.next()\n                    et_uid = self.uid_gen.next()\n                    accesses.append(f\'<Access Scope="GlobalVariable" UId="{et_uid}"><Symbol>{ format_symbol_path(et_tag) }</Symbol></Access>\')',
    '                # Wire ET output\n                if et_tag:\n                    w_et = self.uid_gen.next()\n                    et_uid = self.uid_gen.next()\n                    accesses.append(self._get_symbol_access_xml(et_tag, et_uid))'
)

# GENERIC output
content = content.replace(
    '''                        accesses.append(
                            f'<Access Scope="GlobalVariable" UId="{tag_uid}">'
                            f'<Symbol>{ format_symbol_path(tag_raw) }</Symbol>'
                            f'</Access>'
                        )''',
    '                        accesses.append(self._get_symbol_access_xml(tag_raw, tag_uid))'
)

# Initialize self.temp_vars = [] in TIALadderBuilder.__init__
content = content.replace(
    '        self.timers = []\n        self.uid_gen = UIDGen(start=20)',
    '        self.timers = []\n        self.temp_vars = []\n        self.uid_gen = UIDGen(start=20)'
)

# Add add_temp_var method definition to TIALadderBuilder
content = content.replace(
    '    def generate_xml(self):',
    '''    def add_temp_var(self, name, datatype):
        self.temp_vars.append((name, datatype))

    def generate_xml(self):'''
)

# Replace all <Section Name="Temp" /> with {temp_section} in generate_xml template
content = content.replace('<Section Name="Temp" />', '{temp_section}')

# Update generate_xml to support temp variable section
content = content.replace(
    '''    def generate_xml(self):
        static_timers = ""
        for t in self.timers:
            static_timers += f'<Member Name="{t}" Datatype="IEC_TIMER" Accessibility="Public" />\\n          \'''',
    '''    def generate_xml(self):
        static_timers = ""
        for t in self.timers:
            static_timers += f'<Member Name="{t}" Datatype="IEC_TIMER" Accessibility="Public" />\\n          \'
        temp_members = ""
        for name, dtype in self.temp_vars:
            temp_members += f'<Member Name="{name}" Datatype="{dtype}" Accessibility="Public" />\\n          \'
        temp_section = f'<Section Name="Temp">\\n          {temp_members}</Section>\' if temp_members else \'<Section Name="Temp" />\''''
)

# Add OR3 handler to _build_network
content = content.replace(
    '            elif ctype == "OR2":',
    '''            elif ctype == "OR3":
                tag1 = comp[1]
                tag2 = comp[2]
                tag3 = comp[3]
                var1_uid = self.uid_gen.next()
                var2_uid = self.uid_gen.next()
                var3_uid = self.uid_gen.next()
                part1_uid = self.uid_gen.next()
                part2_uid = self.uid_gen.next()
                part3_uid = self.uid_gen.next()
                or_uid = self.uid_gen.next()
                
                accesses.append(self._get_symbol_access_xml(tag1, var1_uid))
                accesses.append(self._get_symbol_access_xml(tag2, var2_uid))
                accesses.append(self._get_symbol_access_xml(tag3, var3_uid))
                
                parts.append(f'<Part Name="Contact" UId="{part1_uid}" />')
                parts.append(f'<Part Name="Contact" UId="{part2_uid}" />')
                parts.append(f'<Part Name="Contact" UId="{part3_uid}" />')
                parts.append(f'<Part Name="O" UId="{or_uid}"><TemplateValue Name="Card" Type="Cardinality">3</TemplateValue></Part>')
                
                w_in = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_in}">{prev_conn_str}<NameCon UId="{part1_uid}" Name="in" /><NameCon UId="{part2_uid}" Name="in" /><NameCon UId="{part3_uid}" Name="in" /></Wire>')
                
                w_op1 = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_op1}"><IdentCon UId="{var1_uid}" /><NameCon UId="{part1_uid}" Name="operand" /></Wire>')
                w_op2 = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_op2}"><IdentCon UId="{var2_uid}" /><NameCon UId="{part2_uid}" Name="operand" /></Wire>')
                w_op3 = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_op3}"><IdentCon UId="{var3_uid}" /><NameCon UId="{part3_uid}" Name="operand" /></Wire>')

                w_out1 = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_out1}"><NameCon UId="{part1_uid}" Name="out" /><NameCon UId="{or_uid}" Name="in1" /></Wire>')
                w_out2 = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_out2}"><NameCon UId="{part2_uid}" Name="out" /><NameCon UId="{or_uid}" Name="in2" /></Wire>')
                w_out3 = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_out3}"><NameCon UId="{part3_uid}" Name="out" /><NameCon UId="{or_uid}" Name="in3" /></Wire>')

                prev_uid = or_uid
                prev_pin = "out"

            elif ctype == "OR2":'''
)

content = content.replace(
    't_type = "Cardinality" if t_name == "Card" else "Type"',
    't_type = "Cardinality" if (t_name == "Card" or t_name.startswith("card")) else "Type"'
)

content = content.replace(
    '                  <Culture>vi-VN</Culture>\n                  <Text>{title}</Text>',
    '                  <Culture>en-US</Culture>\n                  <Text>{title}</Text>'
)

original_cmp = '''            elif ctype.startswith("CMP_"):
                op_map = {"CMP_GT": "Gt", "CMP_GE": "Ge", "CMP_LT": "Lt",
                          "CMP_LE": "Le", "CMP_EQ": "Eq", "CMP_NE": "Ne"}
                part_name = op_map.get(ctype, "Gt")
                in1_tag = comp[1]  # left operand (variable)
                in2_raw = comp[2]  # right operand (variable or literal)

                in1_uid = self.uid_gen.next()
                in2_uid = self.uid_gen.next()
                cmp_uid = self.uid_gen.next()

                # in1 is always a GlobalVariable
                accesses.append(self._get_symbol_access_xml(in1_tag, in1_uid))

                # Detect type based on tag name or context
                if "ErrorBits" in in1_tag:
                    type_str = "DWord"
                elif "Time" in in1_tag:
                    type_str = "Time"
                elif "iStep" in in1_tag or "State" in in1_tag or "Heartbeat" in in1_tag or "Status" in in1_tag or "Counter" in in1_tag or "Round" in in1_tag or "Seq" in in1_tag:
                    type_str = "Int"
                else:
                    type_str = "Real"'''

replacement_cmp = '''            elif ctype.startswith("CMP_"):
                # Support _Int, _Real, _DWord, etc. suffixes
                suffix = None
                base_ctype = ctype
                for s in ["_Int", "_Real", "_DWord", "_DInt", "_UDInt", "_Word", "_USInt", "_UInt"]:
                    if ctype.endswith(s):
                        suffix = s[1:]
                        base_ctype = ctype[:-len(s)]
                        break
                op_map = {"CMP_GT": "Gt", "CMP_GE": "Ge", "CMP_LT": "Lt",
                          "CMP_LE": "Le", "CMP_EQ": "Eq", "CMP_NE": "Ne"}
                part_name = op_map.get(base_ctype, "Gt")
                in1_tag = comp[1]  # left operand (variable)
                in2_raw = comp[2]  # right operand (variable or literal)

                in1_uid = self.uid_gen.next()
                in2_uid = self.uid_gen.next()
                cmp_uid = self.uid_gen.next()

                # in1 is always a GlobalVariable
                accesses.append(self._get_symbol_access_xml(in1_tag, in1_uid))

                # Detect type based on tag name or context
                if suffix:
                    type_str = suffix
                elif "ErrorBits" in in1_tag:
                    type_str = "DWord"
                elif "Time" in in1_tag:
                    type_str = "Time"
                elif "iStep" in in1_tag or "State" in in1_tag or "Heartbeat" in in1_tag or "Status" in in1_tag or "Counter" in in1_tag or "Round" in in1_tag or "Seq" in in1_tag:
                    type_str = "Int"
                else:
                    type_str = "Real"'''

content = content.replace(original_cmp, replacement_cmp)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patching of Ladder/Agent_LAD_Library.py completed.")
