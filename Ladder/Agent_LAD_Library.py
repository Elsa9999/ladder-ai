# CHÍNH SÁCH LẬP TRÌNH 100% LADDER:
# Mọi dự án sinh từ workspace này phải tạo tên biến (Tag name) bằng tiếng Việt không dấu (ASCII), nhưng tiêu đề mạng (Network Title) và chú thích (Comment) bắt buộc phải dùng tiếng Việt có dấu chuẩn UTF-8.
# Thư viện này chỉ là công cụ hỗ trợ sinh XML; tuyệt đối không được sinh mã nguồn SCL logic cho PLC.
import sys, os
from datetime import datetime

class UIDGen:
    def __init__(self, start=20):
        self.val = start
    def next(self):
        self.val += 1
        return self.val

class TIALadderBuilder:
    def __init__(self, fb_name="FB_Tu_Dong_Sinh", block_id="100", block_type="FB"):
        self.fb_name = fb_name
        self.block_id = block_id
        self.block_type = block_type
        self.networks = ""
        self.timers = []
        self.uid_gen = UIDGen(start=20)

    def _get_access_xml(self, pin_name, value, tag_uid):
        value_str = str(value)
        value_upper = value_str.upper()
        # 0. Bool constant (e.g. TRUE, FALSE)
        if value_upper in ("TRUE", "FALSE"):
            return f'<Access Scope="LiteralConstant" UId="{tag_uid}"><Constant><ConstantType>Bool</ConstantType><ConstantValue>{value_str.lower()}</ConstantValue></Constant></Access>'
        # 1. TypedConstant (e.g. T#5S, W#16#0100)
        if value_upper.startswith("T#") or value_upper.startswith("W#16#"):
            return f'<Access Scope="TypedConstant" UId="{tag_uid}"><Constant><ConstantValue>{value_str}</ConstantValue></Constant></Access>'
        # 2. Remote Pointer
        if value_upper.startswith("P#") and pin_name.startswith("ADDR_"):
            return f'<Access Scope="LiteralConstant" UId="{tag_uid}"><Constant><ConstantType>Remote</ConstantType><ConstantValue>{value_str}</ConstantValue></Constant></Access>'
        # 3. Any Pointer
        if value_upper.startswith("P#") and (pin_name.startswith("RD_") or pin_name.startswith("SD_")):
            return f'<Access Scope="LiteralConstant" UId="{tag_uid}"><Constant><ConstantType>Any</ConstantType><ConstantValue>{value_str}</ConstantValue></Constant></Access>'
        # 4. Pin-specific types
        pin_types = {
            "PORT": "PORT",
            "BAUD": "UDInt",
            "MB_ADDR": "UInt",
            "MODE": "USInt",
            "MB_MODE": "USInt",
            "DATA_ADDR": "UDInt",
            "MB_DATA_ADDR": "UDInt",
            "DATA_LEN": "UInt",
            "MB_DATA_LEN": "UInt",
            "PARITY": "UInt",
        }
        if pin_name in pin_types:
            return f'<Access Scope="LiteralConstant" UId="{tag_uid}"><Constant><ConstantType>{pin_types[pin_name]}</ConstantType><ConstantValue>{value_str}</ConstantValue></Constant></Access>'
        # 5. Default numeric check
        try:
            float(value_str)
            is_real = '.' in value_str
            ctype = "Real" if is_real else "Int"
            return f'<Access Scope="LiteralConstant" UId="{tag_uid}"><Constant><ConstantType>{ctype}</ConstantType><ConstantValue>{value_str}</ConstantValue></Constant></Access>'
        except ValueError:
            # Symbolic name with dots
            comp_str = "".join([f'<Component Name="{x}" />' for x in value_str.split(".")])
            return f'<Access Scope="GlobalVariable" UId="{tag_uid}"><Symbol>{comp_str}</Symbol></Access>'

    def _build_network(self, title, elements):
        net_uid = self.uid_gen.next()
        accesses = []
        parts = []
        wires = []

        POWER_UID = 21

        prev_uid = POWER_UID
        prev_pin = "en"

        for i, comp in enumerate(elements):
            ctype = comp[0]
            prev_conn_str = '<Powerrail />' if prev_uid == 21 else f'<NameCon UId="{prev_uid}" Name="{prev_pin}" />'

            if ctype in ("NO", "NC"):
                var_uid = self.uid_gen.next()
                part_uid = self.uid_gen.next()
                part_name = "Contact"
                negated_tag = '<Negated Name="operand" />' if ctype == "NC" else ""

                accesses.append(
                    f'<Access Scope="GlobalVariable" UId="{var_uid}">'
                    f'<Symbol>{ "".join(["<Component Name=\"" + x + "\" />" for x in comp[1].split(".")]) }</Symbol>'
                    f'</Access>'
                )

                parts.append(
                    f'<Part Name="{part_name}" UId="{part_uid}">'
                    f'{negated_tag}</Part>' if negated_tag else
                    f'<Part Name="{part_name}" UId="{part_uid}" />'
                )

                w_in = self.uid_gen.next()
                wires.append(
                    f'<Wire UId="{w_in}">'
                    f'{prev_conn_str}'
                    f'<NameCon UId="{part_uid}" Name="in" /></Wire>'
                )
                w_op = self.uid_gen.next()
                wires.append(
                    f'<Wire UId="{w_op}">'
                    f'<IdentCon UId="{var_uid}" />'
                    f'<NameCon UId="{part_uid}" Name="operand" /></Wire>'
                )

                prev_uid = part_uid
                prev_pin = "out"

            elif ctype in ("Coil", "SetCoil", "ResetCoil"):
                var_uid = self.uid_gen.next()
                part_uid = self.uid_gen.next()
                part_name = "Coil"
                if ctype == "SetCoil":
                    part_name = "SCoil"
                elif ctype == "ResetCoil":
                    part_name = "RCoil"

                accesses.append(
                    f'<Access Scope="GlobalVariable" UId="{var_uid}">'
                    f'<Symbol>{ "".join(["<Component Name=\"" + x + "\" />" for x in comp[1].split(".")]) }</Symbol>'
                    f'</Access>'
                )
                parts.append(f'<Part Name="{part_name}" UId="{part_uid}" />')

                w_in = self.uid_gen.next()
                wires.append(
                    f'<Wire UId="{w_in}">'
                    f'{prev_conn_str}'
                    f'<NameCon UId="{part_uid}" Name="in" /></Wire>'
                )
                w_op = self.uid_gen.next()
                wires.append(
                    f'<Wire UId="{w_op}">'
                    f'<IdentCon UId="{var_uid}" />'
                    f'<NameCon UId="{part_uid}" Name="operand" /></Wire>'
                )

                prev_uid = part_uid
                prev_pin = "out"

            elif ctype == "OR2":
                tag1 = comp[1]
                tag2 = comp[2]
                var1_uid = self.uid_gen.next()
                var2_uid = self.uid_gen.next()
                part1_uid = self.uid_gen.next()
                part2_uid = self.uid_gen.next()
                or_uid = self.uid_gen.next()
                
                accesses.append(f'<Access Scope="GlobalVariable" UId="{var1_uid}"><Symbol>{ "".join(["<Component Name=\"" + x + "\" />" for x in tag1.split(".")]) }</Symbol></Access>')
                accesses.append(f'<Access Scope="GlobalVariable" UId="{var2_uid}"><Symbol>{ "".join(["<Component Name=\"" + x + "\" />" for x in tag2.split(".")]) }</Symbol></Access>')
                
                parts.append(f'<Part Name="Contact" UId="{part1_uid}" />')
                parts.append(f'<Part Name="Contact" UId="{part2_uid}" />')
                parts.append(f'<Part Name="O" UId="{or_uid}"><TemplateValue Name="Card" Type="Cardinality">2</TemplateValue></Part>')
                
                w_in = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_in}">{prev_conn_str}<NameCon UId="{part1_uid}" Name="in" /><NameCon UId="{part2_uid}" Name="in" /></Wire>')
                
                w_op1 = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_op1}"><IdentCon UId="{var1_uid}" /><NameCon UId="{part1_uid}" Name="operand" /></Wire>')
                w_op2 = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_op2}"><IdentCon UId="{var2_uid}" /><NameCon UId="{part2_uid}" Name="operand" /></Wire>')

                w_out1 = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_out1}"><NameCon UId="{part1_uid}" Name="out" /><NameCon UId="{or_uid}" Name="in1" /></Wire>')
                w_out2 = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_out2}"><NameCon UId="{part2_uid}" Name="out" /><NameCon UId="{or_uid}" Name="in2" /></Wire>')

                prev_uid = or_uid
                prev_pin = "out"

            elif ctype == "CALL_FC":
                fc_name = comp[1]
                param_tag = comp[2] if len(comp) > 2 else None
                call_uid = self.uid_gen.next()
                
                if param_tag:
                    var_uid = self.uid_gen.next()
                    accesses.append(f'<Access Scope="GlobalVariable" UId="{var_uid}"><Symbol>{ "".join(["<Component Name=\"" + x + "\" />" for x in param_tag.split(".")]) }</Symbol></Access>')
                    parts.append(f'<Call UId="{call_uid}"><CallInfo Name="{fc_name}" BlockType="FC"><Parameter Name="bDangChay" Section="Input" Type="Bool" /></CallInfo></Call>')
                    w_in = self.uid_gen.next()
                    wires.append(f'<Wire UId="{w_in}">{prev_conn_str}<NameCon UId="{call_uid}" Name="en" /></Wire>')
                    w_p = self.uid_gen.next()
                    wires.append(f'<Wire UId="{w_p}"><IdentCon UId="{var_uid}" /><NameCon UId="{call_uid}" Name="bDangChay" /></Wire>')
                else:
                    parts.append(f'<Call UId="{call_uid}"><CallInfo Name="{fc_name}" BlockType="FC" /></Call>')
                    w_in = self.uid_gen.next()
                    wires.append(f'<Wire UId="{w_in}">{prev_conn_str}<NameCon UId="{call_uid}" Name="en" /></Wire>')
                
                prev_uid = call_uid
                prev_pin = "eno"

            elif ctype == "PBox":
                tag = comp[1]
                var_uid = self.uid_gen.next()
                part_uid = self.uid_gen.next()
                
                accesses.append(f'<Access Scope="GlobalVariable" UId="{var_uid}"><Symbol>{ "".join(["<Component Name=\"" + x + "\" />" for x in tag.split(".")]) }</Symbol></Access>')
                parts.append(f'<Part Name="PBox" UId="{part_uid}" />')
                
                w_in = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_in}">{prev_conn_str}<NameCon UId="{part_uid}" Name="in" /></Wire>')
                
                w_op = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_op}"><IdentCon UId="{var_uid}" /><NameCon UId="{part_uid}" Name="bit" /></Wire>')
                
                prev_uid = part_uid
                prev_pin = "out"

            # =========================================================
            # CMP: Comparison contacts (Gt, Ge, Lt, Le, Eq, Ne)
            # Usage: ("CMP_GT", "DB1.var", "60.0")       -> var > 60.0
            #        ("CMP_GE", "DB1.var", "DB1.limit")   -> var >= limit
            #        ("CMP_LT", "DB1.var", "0.02")        -> var < 0.02
            # =========================================================
            elif ctype.startswith("CMP_"):
                op_map = {"CMP_GT": "Gt", "CMP_GE": "Ge", "CMP_LT": "Lt",
                          "CMP_LE": "Le", "CMP_EQ": "Eq", "CMP_NE": "Ne"}
                part_name = op_map.get(ctype, "Gt")
                in1_tag = comp[1]  # left operand (variable)
                in2_raw = comp[2]  # right operand (variable or literal)

                in1_uid = self.uid_gen.next()
                in2_uid = self.uid_gen.next()
                cmp_uid = self.uid_gen.next()

                # in1 is always a GlobalVariable
                accesses.append(
                    f'<Access Scope="GlobalVariable" UId="{in1_uid}">'
                    f'<Symbol>{ "".join(["<Component Name=\"" + x + "\" />" for x in in1_tag.split(".")]) }</Symbol>'
                    f'</Access>'
                )

                # Detect type based on tag name or context
                if "ErrorBits" in in1_tag:
                    type_str = "DWord"
                elif "Time" in in1_tag:
                    type_str = "Time"
                elif "iStep" in in1_tag or "State" in in1_tag or "Heartbeat" in in1_tag or "Status" in in1_tag or "Counter" in in1_tag or "Round" in in1_tag or "Seq" in in1_tag:
                    type_str = "Int"
                else:
                    type_str = "Real"

                # in2: detect literal (starts with digit or minus or T#) vs variable
                is_time_const = in2_raw.startswith("T#")
                try:
                    if is_time_const:
                        raise ValueError()
                    float(in2_raw)
                    is_literal = True
                    is_real = '.' in in2_raw
                except ValueError:
                    if is_time_const:
                        is_literal = True
                    else:
                        is_literal = False

                if is_literal:
                    if is_time_const:
                        accesses.append(
                            f'<Access Scope="TypedConstant" UId="{in2_uid}">'
                            f'<Constant><ConstantValue>{in2_raw}</ConstantValue></Constant>'
                            f'</Access>'
                        )
                    else:
                        if type_str == "DWord":
                            ctype_str = "DWord"
                        else:
                            ctype_str = "Real" if is_real else "Int"
                        accesses.append(
                            f'<Access Scope="LiteralConstant" UId="{in2_uid}">'
                            f'<Constant><ConstantType>{ctype_str}</ConstantType><ConstantValue>{in2_raw}</ConstantValue></Constant>'
                            f'</Access>'
                        )
                else:
                    accesses.append(
                        f'<Access Scope="GlobalVariable" UId="{in2_uid}">'
                        f'<Symbol>{ "".join(["<Component Name=\"" + x + "\" />" for x in in2_raw.split(".")]) }</Symbol>'
                        f'</Access>'
                    )

                parts.append(f'<Part Name="{part_name}" UId="{cmp_uid}"><TemplateValue Name="SrcType" Type="Type">{type_str}</TemplateValue></Part>')

                w_pre = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_pre}">{prev_conn_str}<NameCon UId="{cmp_uid}" Name="pre" /></Wire>')
                w_in1 = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_in1}"><IdentCon UId="{in1_uid}" /><NameCon UId="{cmp_uid}" Name="in1" /></Wire>')
                w_in2 = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_in2}"><IdentCon UId="{in2_uid}" /><NameCon UId="{cmp_uid}" Name="in2" /></Wire>')

                prev_uid = cmp_uid
                prev_pin = "out"

            # =========================================================
            # MOVE: Assign a value to an output variable
            # Usage: ("MOVE", "3", "DB1.Mode")  -> Move literal 3 into DB1.Mode
            #        ("MOVE", "DB1.src", "DB1.dst") -> Move variable
            # =========================================================
            elif ctype == "MOVE":
                src_raw = comp[1]
                dst_tag = comp[2]

                src_uid = self.uid_gen.next()
                dst_uid = self.uid_gen.next()
                move_uid = self.uid_gen.next()

                accesses.append(self._get_access_xml("in", src_raw, src_uid))
                accesses.append(
                    f'<Access Scope="GlobalVariable" UId="{dst_uid}">'
                    f'<Symbol>{ "".join(["<Component Name=\"" + x + "\" />" for x in dst_tag.split(".")]) }</Symbol>'
                    f'</Access>'
                )

                parts.append(f'<Part Name="Move" UId="{move_uid}"><TemplateValue Name="Card" Type="Cardinality">1</TemplateValue></Part>')

                w_en = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_en}">{prev_conn_str}<NameCon UId="{move_uid}" Name="en" /></Wire>')
                w_in = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_in}"><IdentCon UId="{src_uid}" /><NameCon UId="{move_uid}" Name="in" /></Wire>')
                w_out = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_out}"><NameCon UId="{move_uid}" Name="out1" /><IdentCon UId="{dst_uid}" /></Wire>')

                prev_uid = move_uid
                prev_pin = "eno"

            elif ctype.startswith("MATH_"):
                op = ctype.split("_")[1].capitalize()  # "Add", "Sub", "Mul", "Div"
                in1_raw = comp[1]
                in2_raw = comp[2]
                out_tag = comp[3]

                math_uid = self.uid_gen.next()
                in1_uid = self.uid_gen.next()
                in2_uid = self.uid_gen.next()
                out_uid = self.uid_gen.next()

                if op in ("Add", "Mul"):
                    parts.append(f'<Part Name="{op}" UId="{math_uid}"><TemplateValue Name="Card" Type="Cardinality">2</TemplateValue><AutomaticTyped Name="SrcType" /></Part>')
                else:
                    parts.append(f'<Part Name="{op}" UId="{math_uid}"><AutomaticTyped Name="SrcType" /></Part>')

                # IN1
                try:
                    float(in1_raw)
                    is_lit1 = True
                    is_real1 = '.' in in1_raw
                except ValueError:
                    is_lit1 = False

                if is_lit1:
                    ctype_str = "Real" if is_real1 else "Int"
                    accesses.append(
                        f'<Access Scope="LiteralConstant" UId="{in1_uid}">'
                        f'<Constant><ConstantType>{ctype_str}</ConstantType><ConstantValue>{in1_raw}</ConstantValue></Constant>'
                        f'</Access>'
                    )
                else:
                    accesses.append(
                        f'<Access Scope="GlobalVariable" UId="{in1_uid}">'
                        f'<Symbol>{ "".join(["<Component Name=\"" + x + "\" />" for x in in1_raw.split(".")]) }</Symbol>'
                        f'</Access>'
                    )

                # IN2
                try:
                    float(in2_raw)
                    is_lit2 = True
                    is_real2 = '.' in in2_raw
                except ValueError:
                    is_lit2 = False

                if is_lit2:
                    ctype_str = "Real" if is_real2 else "Int"
                    accesses.append(
                        f'<Access Scope="LiteralConstant" UId="{in2_uid}">'
                        f'<Constant><ConstantType>{ctype_str}</ConstantType><ConstantValue>{in2_raw}</ConstantValue></Constant>'
                        f'</Access>'
                    )
                else:
                    accesses.append(
                        f'<Access Scope="GlobalVariable" UId="{in2_uid}">'
                        f'<Symbol>{ "".join(["<Component Name=\"" + x + "\" />" for x in in2_raw.split(".")]) }</Symbol>'
                        f'</Access>'
                    )

                # OUT
                accesses.append(
                    f'<Access Scope="GlobalVariable" UId="{out_uid}">'
                    f'<Symbol>{ "".join(["<Component Name=\"" + x + "\" />" for x in out_tag.split(".")]) }</Symbol>'
                    f'</Access>'
                )

                w_en = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_en}">{prev_conn_str}<NameCon UId="{math_uid}" Name="en" /></Wire>')
                
                w_in1 = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_in1}"><IdentCon UId="{in1_uid}" /><NameCon UId="{math_uid}" Name="in1" /></Wire>')
                
                w_in2 = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_in2}"><IdentCon UId="{in2_uid}" /><NameCon UId="{math_uid}" Name="in2" /></Wire>')
                
                w_out = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_out}"><NameCon UId="{math_uid}" Name="out" /><IdentCon UId="{out_uid}" /></Wire>')

                prev_uid = math_uid
                prev_pin = "eno"

            elif ctype.startswith("MATH1_"):
                op = ctype.split("_")[1].capitalize()  # "Abs", "Sqr", "Sqrt", "Sin", "Cos"
                in1_raw = comp[1]
                out_tag = comp[2]

                math_uid = self.uid_gen.next()
                in1_uid = self.uid_gen.next()
                out_uid = self.uid_gen.next()

                parts.append(f'<Part Name="{op}" UId="{math_uid}"><TemplateValue Name="SrcType" Type="Type">Real</TemplateValue></Part>')

                # IN1
                try:
                    float(in1_raw)
                    is_lit1 = True
                    is_real1 = '.' in in1_raw
                except ValueError:
                    is_lit1 = False

                if is_lit1:
                    ctype_str = "Real" if is_real1 else "Int"
                    accesses.append(
                        f'<Access Scope="LiteralConstant" UId="{in1_uid}">'
                        f'<Constant><ConstantType>{ctype_str}</ConstantType><ConstantValue>{in1_raw}</ConstantValue></Constant>'
                        f'</Access>'
                    )
                else:
                    accesses.append(
                        f'<Access Scope="GlobalVariable" UId="{in1_uid}">'
                        f'<Symbol>{ "".join(["<Component Name=\"" + x + "\" />" for x in in1_raw.split(".")]) }</Symbol>'
                        f'</Access>'
                    )

                # OUT
                accesses.append(
                    f'<Access Scope="GlobalVariable" UId="{out_uid}">'
                    f'<Symbol>{ "".join(["<Component Name=\"" + x + "\" />" for x in out_tag.split(".")]) }</Symbol>'
                    f'</Access>'
                )

                w_en = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_en}">{prev_conn_str}<NameCon UId="{math_uid}" Name="en" /></Wire>')
                
                w_in1 = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_in1}"><IdentCon UId="{in1_uid}" /><NameCon UId="{math_uid}" Name="in" /></Wire>')
                
                w_out = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_out}"><NameCon UId="{math_uid}" Name="out" /><IdentCon UId="{out_uid}" /></Wire>')

                prev_uid = math_uid
                prev_pin = "eno"

            elif ctype.startswith("CONV_"):
                op = ctype.split("_")[1].capitalize()  # "Convert", "Round", "Ceil", "Floor"
                in1_raw = comp[1]
                out_tag = comp[2]
                src_type = comp[3] if len(comp) > 3 else "Real"
                dst_type = comp[4] if len(comp) > 4 else "DInt"

                conv_uid = self.uid_gen.next()
                in1_uid = self.uid_gen.next()
                out_uid = self.uid_gen.next()

                if op == "Convert":
                    parts.append(f'<Part Name="Convert" UId="{conv_uid}"><TemplateValue Name="SrcType" Type="Type">{src_type}</TemplateValue><TemplateValue Name="DestType" Type="Type">{dst_type}</TemplateValue></Part>')
                else:
                    parts.append(f'<Part Name="{op}" UId="{conv_uid}"><TemplateValue Name="SrcType" Type="Type">{src_type}</TemplateValue><TemplateValue Name="DestType" Type="Type">{dst_type}</TemplateValue></Part>')

                # IN1
                try:
                    float(in1_raw)
                    is_lit1 = True
                    is_real1 = '.' in in1_raw
                except ValueError:
                    is_lit1 = False

                if is_lit1:
                    ctype_str = "Real" if is_real1 else "Int"
                    accesses.append(
                        f'<Access Scope="LiteralConstant" UId="{in1_uid}">'
                        f'<Constant><ConstantType>{ctype_str}</ConstantType><ConstantValue>{in1_raw}</ConstantValue></Constant>'
                        f'</Access>'
                    )
                else:
                    accesses.append(
                        f'<Access Scope="GlobalVariable" UId="{in1_uid}">'
                        f'<Symbol>{ "".join(["<Component Name=\"" + x + "\" />" for x in in1_raw.split(".")]) }</Symbol>'
                        f'</Access>'
                    )

                # OUT
                accesses.append(
                    f'<Access Scope="GlobalVariable" UId="{out_uid}">'
                    f'<Symbol>{ "".join(["<Component Name=\"" + x + "\" />" for x in out_tag.split(".")]) }</Symbol>'
                    f'</Access>'
                )

                w_en = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_en}">{prev_conn_str}<NameCon UId="{conv_uid}" Name="en" /></Wire>')
                
                w_in1 = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_in1}"><IdentCon UId="{in1_uid}" /><NameCon UId="{conv_uid}" Name="in" /></Wire>')
                
                w_out = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_out}"><NameCon UId="{conv_uid}" Name="out" /><IdentCon UId="{out_uid}" /></Wire>')

                prev_uid = conv_uid
                prev_pin = "eno"

            elif ctype == "GENERIC":
                # Tuple: ("GENERIC", part_name, inputs_dict, outputs_dict, template_dict, instance_db)
                part_name = comp[1]
                inputs = comp[2] if len(comp) > 2 else {}
                outputs = comp[3] if len(comp) > 3 else {}
                templates = comp[4] if len(comp) > 4 else {}
                inst_db = comp[5] if len(comp) > 5 else None

                gen_uid = self.uid_gen.next()
                
                # Build Part
                version_str = ""
                if "Version" in templates:
                    version_str = f' Version="{templates["Version"]}"'
                    del templates["Version"]

                part_xml = f'<Part Name="{part_name}"{version_str} UId="{gen_uid}">'
                if inst_db:
                    if inst_db not in self.timers: # Hack to reuse DB list
                        self.timers.append(inst_db)
                    inst_uid = self.uid_gen.next()
                    scope_val = "GlobalVariable" if (inst_db.endswith("_DB") or "GET_DB" in inst_db or "PUT_DB" in inst_db) else "LocalVariable"
                    part_xml += f'<Instance Scope="{scope_val}" UId="{inst_uid}"><Component Name="{inst_db}" /></Instance>'
                
                if "Equation" in templates:
                    part_xml += f'<Equation>{templates["Equation"]}</Equation>'
                    del templates["Equation"]

                for t_name, t_val in templates.items():
                    t_type = "Cardinality" if t_name == "Card" else "Type"
                    part_xml += f'<TemplateValue Name="{t_name}" Type="{t_type}">{t_val}</TemplateValue>'
                
                part_xml += '</Part>'
                parts.append(part_xml)

                # Connect EN from previous block
                w_en = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_en}">{prev_conn_str}<NameCon UId="{gen_uid}" Name="en" /></Wire>')

                # Process Inputs
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
                        f'<Symbol>{ "".join(["<Component Name=\"" + x + "\" />" for x in tag_raw.split(".")]) }</Symbol>'
                        f'</Access>'
                    )
                    w_out = self.uid_gen.next()
                    wires.append(f'<Wire UId="{w_out}"><NameCon UId="{gen_uid}" Name="{pin_name}" /><IdentCon UId="{tag_uid}" /></Wire>')

                prev_uid = gen_uid
                prev_pin = "eno"

            elif ctype.startswith("PID_Compact"):
                # Tuple: ("PID_Compact", db_name, inputs, outputs, version)
                # Vi du: ("PID_Compact", "PID_Compact_1", {"Setpoint": "AI_Nhiet_Do_SP", "Input": "AI_Nhiet_Do_PV"}, {"Output": "AI_PID_Output"}, "1.2")
                part_name = ctype
                db_name = comp[1]
                inputs = comp[2] if len(comp) > 2 else {}
                outputs = comp[3] if len(comp) > 3 else {}
                version = comp[4] if len(comp) > 4 else "1.2"

                pid_uid = self.uid_gen.next()
                inst_uid = self.uid_gen.next()

                comp_str = "".join([f'<Component Name="{x}" />' for x in db_name.split(".")])
                parts.append(
                    f'<Part Name="{part_name}" Version="{version}" UId="{pid_uid}">'
                    f'<Instance Scope="GlobalVariable" UId="{inst_uid}">'
                    f'{comp_str}</Instance>'
                    f'</Part>'
                )

                w_en = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_en}">{prev_conn_str}<NameCon UId="{pid_uid}" Name="en" /></Wire>')

                if version.startswith("2."):
                    all_inputs = ["Setpoint", "Input", "Input_PER", "Disturbance", "ManualEnable", "ManualValue", "ModeActivate", "Mode", "ErrorAck", "Reset"]
                else:
                    all_inputs = ["Setpoint", "Input", "Input_PER", "ManualEnable", "ManualValue", "Reset"]

                for pin in all_inputs:
                    if pin in inputs and inputs[pin]:
                        tag_raw = inputs[pin]
                        tag_uid = self.uid_gen.next()
                        try:
                            float(tag_raw)
                            is_lit = True
                            is_real = '.' in tag_raw
                        except ValueError:
                            is_lit = False

                        if is_lit:
                            ctype_str = "Real" if is_real else "Int"
                            accesses.append(
                                f'<Access Scope="LiteralConstant" UId="{tag_uid}">'
                                f'<Constant><ConstantType>{ctype_str}</ConstantType><ConstantValue>{tag_raw}</ConstantValue></Constant>'
                                f'</Access>'
                            )
                        else:
                            accesses.append(
                                f'<Access Scope="GlobalVariable" UId="{tag_uid}">'
                                f'<Symbol>{ "".join(["<Component Name=\"" + x + "\" />" for x in tag_raw.split(".")]) }</Symbol>'
                                f'</Access>'
                            )
                        w_in = self.uid_gen.next()
                        wires.append(f'<Wire UId="{w_in}"><IdentCon UId="{tag_uid}" /><NameCon UId="{pid_uid}" Name="{pin}" /></Wire>')
                    else:
                        open_uid = self.uid_gen.next()
                        w_in = self.uid_gen.next()
                        wires.append(f'<Wire UId="{w_in}"><OpenCon UId="{open_uid}" /><NameCon UId="{pid_uid}" Name="{pin}" /></Wire>')

                if version.startswith("2."):
                    all_outputs = ["ScaledInput", "Output", "Output_PER", "Output_PWM", "SetpointLimit_H", "SetpointLimit_L", "InputWarning_H", "InputWarning_L", "State", "Error", "ErrorBits"]
                else:
                    all_outputs = ["ScaledInput", "Output", "Output_PER", "Output_PWM", "SetpointLimit_H", "SetpointLimit_L", "InputWarning_H", "InputWarning_L", "State", "Error"]

                for pin in all_outputs:
                    if pin in outputs and outputs[pin]:
                        tag_raw = outputs[pin]
                        tag_uid = self.uid_gen.next()
                        accesses.append(
                            f'<Access Scope="GlobalVariable" UId="{tag_uid}">'
                            f'<Symbol>{ "".join(["<Component Name=\"" + x + "\" />" for x in tag_raw.split(".")]) }</Symbol>'
                            f'</Access>'
                        )
                        w_out = self.uid_gen.next()
                        wires.append(f'<Wire UId="{w_out}"><NameCon UId="{pid_uid}" Name="{pin}" /><IdentCon UId="{tag_uid}" /></Wire>')
                    else:
                        open_uid = self.uid_gen.next()
                        w_out = self.uid_gen.next()
                        wires.append(f'<Wire UId="{w_out}"><NameCon UId="{pid_uid}" Name="{pin}" /><OpenCon UId="{open_uid}" /></Wire>')

                prev_uid = pid_uid
                prev_pin = "eno"

            elif ctype == "TON":
                db_name = comp[1]
                time_val = comp[2]
                q_tag = comp[3] if len(comp) > 3 else None
                et_tag = comp[4] if len(comp) > 4 else None

                if db_name not in self.timers:
                    self.timers.append(db_name)

                inst_uid = self.uid_gen.next()
                part_uid = self.uid_gen.next()
                pt_uid = self.uid_gen.next()

                try:
                    float(time_val) # not a valid time string anyway if it's float
                    is_lit = False
                except:
                    is_lit = time_val.startswith("T#")

                if is_lit:
                    accesses.append(
                        f'<Access Scope="TypedConstant" UId="{pt_uid}">'
                        f'<Constant><ConstantValue>{time_val}</ConstantValue></Constant>'
                        f'</Access>'
                    )
                else:
                    accesses.append(
                        f'<Access Scope="GlobalVariable" UId="{pt_uid}">'
                        f'<Symbol>{ "".join(["<Component Name=\"" + x + "\" />" for x in time_val.split(".")]) }</Symbol>'
                        f'</Access>'
                    )

                is_global = "." in db_name or db_name not in self.timers
                scope_str = "GlobalVariable"
                comp_str = "".join([f'<Component Name="{x}" />' for x in db_name.split(".")])
                parts.append(
                    f'<Part Name="TON" Version="1.0" UId="{part_uid}">'
                    f'<Instance Scope="{scope_str}" UId="{inst_uid}">'
                    f'{comp_str}</Instance>'
                    f'<TemplateValue Name="time_type" Type="Type">Time</TemplateValue>'
                    f'</Part>'
                )

                w_in = self.uid_gen.next()
                wires.append(
                    f'<Wire UId="{w_in}">'
                    f'{prev_conn_str}'
                    f'<NameCon UId="{part_uid}" Name="IN" /></Wire>'
                )
                w_pt = self.uid_gen.next()
                wires.append(
                    f'<Wire UId="{w_pt}">'
                    f'<IdentCon UId="{pt_uid}" />'
                    f'<NameCon UId="{part_uid}" Name="PT" /></Wire>'
                )

                prev_uid = part_uid
                prev_pin = "Q"

                # Wire Q output
                if q_tag:
                    w_q = self.uid_gen.next()
                    q_uid = self.uid_gen.next()
                    accesses.append(f'<Access Scope="GlobalVariable" UId="{q_uid}"><Symbol>{ "".join(["<Component Name=\"" + x + "\" />" for x in q_tag.split(".")]) }</Symbol></Access>')
                    wires.append(f'<Wire UId="{w_q}"><NameCon UId="{part_uid}" Name="Q" /><IdentCon UId="{q_uid}" /></Wire>')
                else:
                    open_uid = self.uid_gen.next()
                    w_q = self.uid_gen.next()
                    wires.append(f'<Wire UId="{w_q}"><NameCon UId="{part_uid}" Name="Q" /><OpenCon UId="{open_uid}" /></Wire>')

                # Wire ET output
                if et_tag:
                    w_et = self.uid_gen.next()
                    et_uid = self.uid_gen.next()
                    accesses.append(f'<Access Scope="GlobalVariable" UId="{et_uid}"><Symbol>{ "".join(["<Component Name=\"" + x + "\" />" for x in et_tag.split(".")]) }</Symbol></Access>')
                    wires.append(f'<Wire UId="{w_et}"><NameCon UId="{part_uid}" Name="ET" /><IdentCon UId="{et_uid}" /></Wire>')
                else:
                    open_uid = self.uid_gen.next()
                    w_et = self.uid_gen.next()
                    wires.append(f'<Wire UId="{w_et}"><NameCon UId="{part_uid}" Name="ET" /><OpenCon UId="{open_uid}" /></Wire>')

            elif ctype == "CTU":
                # Tuple: ("CTU", db_name, inputs, outputs, value_type, version)
                db_name = comp[1]
                inputs = comp[2] if len(comp) > 2 else {}
                outputs = comp[3] if len(comp) > 3 else {}
                val_type = comp[4] if len(comp) > 4 else "Int"
                version = comp[5] if len(comp) > 5 else "1.0"

                ctu_uid = self.uid_gen.next()
                inst_uid = self.uid_gen.next()

                is_global = "." in db_name or db_name not in self.timers
                scope_str = "GlobalVariable"
                comp_str = "".join([f'<Component Name="{x}" />' for x in db_name.split(".")])

                parts.append(
                    f'<Part Name="CTU" Version="{version}" UId="{ctu_uid}">'
                    f'<Instance Scope="{scope_str}" UId="{inst_uid}">'
                    f'{comp_str}</Instance>'
                    f'<TemplateValue Name="value_type" Type="Type">{val_type}</TemplateValue>'
                    f'</Part>'
                )

                # Connect CU from previous block
                w_cu = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_cu}">{prev_conn_str}<NameCon UId="{ctu_uid}" Name="CU" /></Wire>')

                # Process inputs (R, PV)
                all_inputs = ["R", "PV"]
                for pin in all_inputs:
                    if pin in inputs and inputs[pin] is not None and inputs[pin] != "":
                        tag_raw = inputs[pin]
                        tag_uid = self.uid_gen.next()
                        accesses.append(self._get_access_xml(pin, tag_raw, tag_uid))
                        w_in = self.uid_gen.next()
                        wires.append(f'<Wire UId="{w_in}"><IdentCon UId="{tag_uid}" /><NameCon UId="{ctu_uid}" Name="{pin}" /></Wire>')
                    else:
                        open_uid = self.uid_gen.next()
                        w_in = self.uid_gen.next()
                        wires.append(f'<Wire UId="{w_in}"><OpenCon UId="{open_uid}" /><NameCon UId="{ctu_uid}" Name="{pin}" /></Wire>')

                # Process outputs (Q, CV)
                all_outputs = ["Q", "CV"]
                for pin in all_outputs:
                    if pin in outputs and outputs[pin]:
                        tag_raw = outputs[pin]
                        tag_uid = self.uid_gen.next()
                        accesses.append(self._get_access_xml(pin, tag_raw, tag_uid))
                        w_out = self.uid_gen.next()
                        wires.append(f'<Wire UId="{w_out}"><NameCon UId="{ctu_uid}" Name="{pin}" /><IdentCon UId="{tag_uid}" /></Wire>')
                    else:
                        open_uid = self.uid_gen.next()
                        w_out = self.uid_gen.next()
                        wires.append(f'<Wire UId="{w_out}"><NameCon UId="{ctu_uid}" Name="{pin}" /><OpenCon UId="{open_uid}" /></Wire>')

                prev_uid = ctu_uid
                prev_pin = "Q"

            elif ctype == "MB_COMM_LOAD":
                # Tuple: ("MB_COMM_LOAD", db_name, inputs, outputs, version)
                db_name = comp[1]
                inputs = comp[2] if len(comp) > 2 else {}
                outputs = comp[3] if len(comp) > 3 else {}
                version = comp[4] if len(comp) > 4 else "2.1"

                mcl_uid = self.uid_gen.next()
                inst_uid = self.uid_gen.next()

                comp_str = "".join([f'<Component Name="{x}" />' for x in db_name.split(".")])
                parts.append(
                    f'<Part Name="MB_COMM_LOAD" Version="{version}" UId="{mcl_uid}">'
                    f'<Instance Scope="GlobalVariable" UId="{inst_uid}">'
                    f'{comp_str}</Instance>'
                    f'</Part>'
                )

                # Connect EN from previous block
                w_en = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_en}">{prev_conn_str}<NameCon UId="{mcl_uid}" Name="en" /></Wire>')

                # Process inputs
                all_inputs = ["REQ", "PORT", "BAUD", "PARITY", "FLOW_CTRL", "RTS_ON_DLY", "RTS_OFF_DLY", "RESP_TO", "MB_DB"]
                for pin in all_inputs:
                    if pin in inputs and inputs[pin] is not None and inputs[pin] != "":
                        tag_raw = inputs[pin]
                        tag_uid = self.uid_gen.next()
                        accesses.append(self._get_access_xml(pin, tag_raw, tag_uid))
                        w_in = self.uid_gen.next()
                        wires.append(f'<Wire UId="{w_in}"><IdentCon UId="{tag_uid}" /><NameCon UId="{mcl_uid}" Name="{pin}" /></Wire>')
                    else:
                        open_uid = self.uid_gen.next()
                        w_in = self.uid_gen.next()
                        wires.append(f'<Wire UId="{w_in}"><OpenCon UId="{open_uid}" /><NameCon UId="{mcl_uid}" Name="{pin}" /></Wire>')

                # Process outputs
                all_outputs = ["DONE", "ERROR", "STATUS"]
                for pin in all_outputs:
                    if pin in outputs and outputs[pin]:
                        tag_raw = outputs[pin]
                        tag_uid = self.uid_gen.next()
                        accesses.append(self._get_access_xml(pin, tag_raw, tag_uid))
                        w_out = self.uid_gen.next()
                        wires.append(f'<Wire UId="{w_out}"><NameCon UId="{mcl_uid}" Name="{pin}" /><IdentCon UId="{tag_uid}" /></Wire>')
                    else:
                        open_uid = self.uid_gen.next()
                        w_out = self.uid_gen.next()
                        wires.append(f'<Wire UId="{w_out}"><NameCon UId="{mcl_uid}" Name="{pin}" /><OpenCon UId="{open_uid}" /></Wire>')

                prev_uid = mcl_uid
                prev_pin = "eno"

            elif ctype == "MB_MASTER":
                # Tuple: ("MB_MASTER", db_name, inputs, outputs, version)
                db_name = comp[1]
                inputs = comp[2] if len(comp) > 2 else {}
                outputs = comp[3] if len(comp) > 3 else {}
                version = comp[4] if len(comp) > 4 else "2.2"

                mbm_uid = self.uid_gen.next()
                inst_uid = self.uid_gen.next()

                comp_str = "".join([f'<Component Name="{x}" />' for x in db_name.split(".")])
                parts.append(
                    f'<Part Name="MB_MASTER" Version="{version}" UId="{mbm_uid}">'
                    f'<Instance Scope="GlobalVariable" UId="{inst_uid}">'
                    f'{comp_str}</Instance>'
                    f'</Part>'
                )

                # Connect EN from previous block
                w_en = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_en}">{prev_conn_str}<NameCon UId="{mbm_uid}" Name="en" /></Wire>')

                # Process inputs
                all_inputs = ["REQ", "MB_ADDR", "MODE", "DATA_ADDR", "DATA_LEN", "DATA_PTR"]
                for pin in all_inputs:
                    if pin in inputs and inputs[pin] is not None and inputs[pin] != "":
                        tag_raw = inputs[pin]
                        tag_uid = self.uid_gen.next()
                        accesses.append(self._get_access_xml(pin, tag_raw, tag_uid))
                        w_in = self.uid_gen.next()
                        wires.append(f'<Wire UId="{w_in}"><IdentCon UId="{tag_uid}" /><NameCon UId="{mbm_uid}" Name="{pin}" /></Wire>')
                    else:
                        open_uid = self.uid_gen.next()
                        w_in = self.uid_gen.next()
                        wires.append(f'<Wire UId="{w_in}"><OpenCon UId="{open_uid}" /><NameCon UId="{mbm_uid}" Name="{pin}" /></Wire>')

                # Process outputs
                all_outputs = ["DONE", "BUSY", "ERROR", "STATUS"]
                for pin in all_outputs:
                    if pin in outputs and outputs[pin]:
                        tag_raw = outputs[pin]
                        tag_uid = self.uid_gen.next()
                        accesses.append(self._get_access_xml(pin, tag_raw, tag_uid))
                        w_out = self.uid_gen.next()
                        wires.append(f'<Wire UId="{w_out}"><NameCon UId="{mbm_uid}" Name="{pin}" /><IdentCon UId="{tag_uid}" /></Wire>')
                    else:
                        open_uid = self.uid_gen.next()
                        w_out = self.uid_gen.next()
                        wires.append(f'<Wire UId="{w_out}"><NameCon UId="{mbm_uid}" Name="{pin}" /><OpenCon UId="{open_uid}" /></Wire>')

                prev_uid = mbm_uid
                prev_pin = "eno"

            elif ctype in ("GET", "PUT"):
                # Tuple: ("GET", db_name, inputs, outputs, version)
                db_name = comp[1]
                inputs = comp[2] if len(comp) > 2 else {}
                outputs = comp[3] if len(comp) > 3 else {}
                version = comp[4] if len(comp) > 4 else "1.3"

                blk_uid = self.uid_gen.next()
                inst_uid = self.uid_gen.next()

                comp_str = "".join([f'<Component Name="{x}" />' for x in db_name.split(".")])
                parts.append(
                    f'<Part Name="{ctype}" Version="{version}" UId="{blk_uid}">'
                    f'<Instance Scope="GlobalVariable" UId="{inst_uid}">'
                    f'{comp_str}</Instance>'
                    f'<TemplateValue Name="remote_type" Type="Type">Remote</TemplateValue>'
                    f'<TemplateValue Name="local_type" Type="Type">Variant</TemplateValue>'
                    f'</Part>'
                )

                # Connect EN from previous block
                w_en = self.uid_gen.next()
                wires.append(f'<Wire UId="{w_en}">{prev_conn_str}<NameCon UId="{blk_uid}" Name="en" /></Wire>')

                # Process inputs
                local_pin_prefix = "RD_" if ctype == "GET" else "SD_"
                all_inputs = ["REQ", "ID",
                              "ADDR_1", "ADDR_2", "ADDR_3", "ADDR_4",
                              f"{local_pin_prefix}1", f"{local_pin_prefix}2", f"{local_pin_prefix}3", f"{local_pin_prefix}4"]
                for pin in all_inputs:
                    if pin in inputs and inputs[pin] is not None and inputs[pin] != "":
                        tag_raw = inputs[pin]
                        tag_uid = self.uid_gen.next()
                        accesses.append(self._get_access_xml(pin, tag_raw, tag_uid))
                        w_in = self.uid_gen.next()
                        wires.append(f'<Wire UId="{w_in}"><IdentCon UId="{tag_uid}" /><NameCon UId="{blk_uid}" Name="{pin}" /></Wire>')
                    else:
                        open_uid = self.uid_gen.next()
                        w_in = self.uid_gen.next()
                        wires.append(f'<Wire UId="{w_in}"><OpenCon UId="{open_uid}" /><NameCon UId="{blk_uid}" Name="{pin}" /></Wire>')

                # Process outputs
                all_outputs = ["NDR" if ctype == "GET" else "DONE", "ERROR", "STATUS"]
                for pin in all_outputs:
                    if pin in outputs and outputs[pin]:
                        tag_raw = outputs[pin]
                        tag_uid = self.uid_gen.next()
                        accesses.append(self._get_access_xml(pin, tag_raw, tag_uid))
                        w_out = self.uid_gen.next()
                        wires.append(f'<Wire UId="{w_out}"><NameCon UId="{blk_uid}" Name="{pin}" /><IdentCon UId="{tag_uid}" /></Wire>')
                    else:
                        open_uid = self.uid_gen.next()
                        w_out = self.uid_gen.next()
                        wires.append(f'<Wire UId="{w_out}"><NameCon UId="{blk_uid}" Name="{pin}" /><OpenCon UId="{open_uid}" /></Wire>')

                prev_uid = blk_uid
                prev_pin = "eno"

        acc_str = "".join(accesses)
        prt_str = "".join(parts)
        wir_str = "".join(wires)

        return f'''
      <SW.Blocks.CompileUnit ID="{net_uid}" CompositionName="CompileUnits">
        <AttributeList>
          <NetworkSource>
            <FlgNet xmlns="http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v4">
              <Parts>{acc_str}{prt_str}</Parts>
              <Wires>{wir_str}</Wires>
            </FlgNet>
          </NetworkSource>
          <ProgrammingLanguage>LAD</ProgrammingLanguage>
        </AttributeList>
        <ObjectList>
          <MultilingualText ID="{self.uid_gen.next()}" CompositionName="Title">
            <ObjectList>
              <MultilingualTextItem ID="{self.uid_gen.next()}" CompositionName="Items">
                <AttributeList>
                  <Culture>en-US</Culture>
                  <Text>{title.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")}</Text>
                </AttributeList>
              </MultilingualTextItem>
            </ObjectList>
          </MultilingualText>
        </ObjectList>
      </SW.Blocks.CompileUnit>'''

    def add_network(self, title, elements):
        self.networks += self._build_network(title, elements)

    def add_pid_mode_network(self, title, enable_tag, instance_name):
        """Add the same PID mode latch network used by the known-good TIA export."""
        net_uid = self.uid_gen.next()
        enable_uid = self.uid_gen.next()
        mode3_uid = self.uid_gen.next()
        auto_target_uid = self.uid_gen.next()
        mode0_uid = self.uid_gen.next()
        stop_target_uid = self.uid_gen.next()
        contact_uid = self.uid_gen.next()
        move3_uid = self.uid_gen.next()
        not_uid = self.uid_gen.next()
        move0_uid = self.uid_gen.next()

        w_power = self.uid_gen.next()
        w_operand = self.uid_gen.next()
        w_contact_out = self.uid_gen.next()
        w_move3_in = self.uid_gen.next()
        w_move3_out = self.uid_gen.next()
        w_not_out = self.uid_gen.next()
        w_move0_in = self.uid_gen.next()
        w_move0_out = self.uid_gen.next()
        title_uid = self.uid_gen.next()
        title_item_uid = self.uid_gen.next()

        target = "".join(f'<Component Name="{x}" />' for x in instance_name.split(".")) + '<Component Name="sRet" /><Component Name="i_Mode" />'
        self.networks += f'''
      <SW.Blocks.CompileUnit ID="{net_uid}" CompositionName="CompileUnits">
        <AttributeList>
          <NetworkSource><FlgNet xmlns="http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v4">
  <Parts>
    <Access Scope="GlobalVariable" UId="{enable_uid}"><Symbol><Component Name="{enable_tag}" /></Symbol></Access>
    <Access Scope="LiteralConstant" UId="{mode3_uid}"><Constant><ConstantType>Int</ConstantType><ConstantValue>3</ConstantValue></Constant></Access>
    <Access Scope="GlobalVariable" UId="{auto_target_uid}"><Symbol>{target}</Symbol></Access>
    <Access Scope="LiteralConstant" UId="{mode0_uid}"><Constant><ConstantType>Int</ConstantType><ConstantValue>0</ConstantValue></Constant></Access>
    <Access Scope="GlobalVariable" UId="{stop_target_uid}"><Symbol>{target}</Symbol></Access>
    <Part Name="Contact" UId="{contact_uid}" />
    <Part Name="Move" UId="{move3_uid}" DisabledENO="true"><TemplateValue Name="Card" Type="Cardinality">1</TemplateValue></Part>
    <Part Name="Not" UId="{not_uid}" />
    <Part Name="Move" UId="{move0_uid}" DisabledENO="true"><TemplateValue Name="Card" Type="Cardinality">1</TemplateValue></Part>
  </Parts>
  <Wires>
    <Wire UId="{w_power}"><Powerrail /><NameCon UId="{contact_uid}" Name="in" /></Wire>
    <Wire UId="{w_operand}"><IdentCon UId="{enable_uid}" /><NameCon UId="{contact_uid}" Name="operand" /></Wire>
    <Wire UId="{w_contact_out}"><NameCon UId="{contact_uid}" Name="out" /><NameCon UId="{move3_uid}" Name="en" /><NameCon UId="{not_uid}" Name="in" /></Wire>
    <Wire UId="{w_move3_in}"><IdentCon UId="{mode3_uid}" /><NameCon UId="{move3_uid}" Name="in" /></Wire>
    <Wire UId="{w_move3_out}"><NameCon UId="{move3_uid}" Name="out1" /><IdentCon UId="{auto_target_uid}" /></Wire>
    <Wire UId="{w_not_out}"><NameCon UId="{not_uid}" Name="out" /><NameCon UId="{move0_uid}" Name="en" /></Wire>
    <Wire UId="{w_move0_in}"><IdentCon UId="{mode0_uid}" /><NameCon UId="{move0_uid}" Name="in" /></Wire>
    <Wire UId="{w_move0_out}"><NameCon UId="{move0_uid}" Name="out1" /><IdentCon UId="{stop_target_uid}" /></Wire>
  </Wires>
</FlgNet></NetworkSource>
          <ProgrammingLanguage>LAD</ProgrammingLanguage>
        </AttributeList>
        <ObjectList>
          <MultilingualText ID="{title_uid}" CompositionName="Title">
            <ObjectList>
              <MultilingualTextItem ID="{title_item_uid}" CompositionName="Items">
                <AttributeList>
                  <Culture>vi-VN</Culture>
                  <Text>{title}</Text>
                </AttributeList>
              </MultilingualTextItem>
            </ObjectList>
          </MultilingualText>
        </ObjectList>
      </SW.Blocks.CompileUnit>'''

    def generate_xml(self):
        static_timers = ""
        for t in self.timers:
            static_timers += f'<Member Name="{t}" Datatype="IEC_TIMER" Accessibility="Public" />\n          '

        interface_str = ""
        if self.block_type == "FB":
            interface_str = f'''<Interface><Sections xmlns="http://www.siemens.com/automation/Openness/SW/Interface/v5">
        <Section Name="Input" />
        <Section Name="Output" />
        <Section Name="InOut" />
        <Section Name="Static">
          {static_timers}
        </Section>
        <Section Name="Temp" />
        <Section Name="Constant" />
      </Sections></Interface>'''
        elif self.block_type == "FC":
            interface_str = f'''<Interface><Sections xmlns="http://www.siemens.com/automation/Openness/SW/Interface/v5">
        <Section Name="Input" />
        <Section Name="Output" />
        <Section Name="InOut" />
        <Section Name="Temp" />
        <Section Name="Constant" />
        <Section Name="Return"><Member Name="Ret_Val" Datatype="Void" Accessibility="Public" /></Section>
      </Sections></Interface>'''
        elif self.block_type == "OB":
            interface_str = f'''<Interface><Sections xmlns="http://www.siemens.com/automation/Openness/SW/Interface/v5">
        <Section Name="Input"><Member Name="Initial_Call" Datatype="Bool" Accessibility="Public" Informative="true" /><Member Name="Remanence" Datatype="Bool" Accessibility="Public" Informative="true" /></Section>
        <Section Name="Temp" />
        <Section Name="Constant" />
      </Sections></Interface>'''

        return f"""<?xml version="1.0" encoding="utf-8"?>
<Document>
  <Engineering version="V18" />
  <DocumentInfo>
    <Created>2026-04-18T00:00:00Z</Created>
    <ExportSetting>WithDefaults</ExportSetting>
  </DocumentInfo>
  <SW.Blocks.{self.block_type} ID="0">
    <AttributeList>
      <AutoNumber>true</AutoNumber>
      <HeaderVersion>0.1</HeaderVersion>
      {interface_str}
      <IsIECCheckEnabled>false</IsIECCheckEnabled>
      {"<IsRetainMemResEnabled>false</IsRetainMemResEnabled>" if self.block_type == "FB" else ""}
      <MemoryLayout>Optimized</MemoryLayout>
      <Name>{self.fb_name}</Name>
      <Namespace />
      <Number>{self.block_id}</Number>
      <ProgrammingLanguage>LAD</ProgrammingLanguage>
      {"<SecondaryType>ProgramCycle</SecondaryType>" if self.block_type == "OB" else ""}
    </AttributeList>
    <ObjectList>
{self.networks}
    </ObjectList>
  </SW.Blocks.{self.block_type}>
</Document>"""
class TIAHmiListBuilder:
    def __init__(self, list_name, list_type="TextList", comment=""):
        self.list_name = list_name
        self.list_type = list_type  # "TextList" or "GraphicList"
        self.comment = comment
        self.items = []
        self.uid_counter = 1

    def add_item(self, value, text_or_graphic, item_comment=""):
        # For TextList, text_or_graphic is the text string.
        # For GraphicList, text_or_graphic is the graphic picture name.
        self.items.append({
            "value": value,
            "target": text_or_graphic,
            "comment": item_comment
        })

    def generate_xml(self):
        root_tag = f"Hmi.TextGraphicList.{self.list_type}"
        entry_tag = f"Hmi.TextGraphicList.{self.list_type}Entry"
        
        entries_xml = ""
        for i, item in enumerate(self.items):
            self.uid_counter += 1
            entry_id = self.uid_counter
            
            # Default entry is true for the first item
            is_default = "true" if i == 0 else "false"
            
            if self.list_type == "TextList":
                self.uid_counter += 1
                text_id = self.uid_counter
                self.uid_counter += 1
                text_item_id = self.uid_counter
                
                # Wrap text inside paragraph tag for WinCC HMI compatibility
                formatted_text = f"<body><p>{item['target']}</p></body>"
                
                entries_xml += f"""      <{entry_tag} ID="{entry_id}" CompositionName="Entries">
        <AttributeList>
          <DefaultEntry>{is_default}</DefaultEntry>
          <EntryType>SingleValue</EntryType>
          <From>{item['value']}</From>
          <To>{item['value']}</To>
        </AttributeList>
        <ObjectList>
          <MultilingualText ID="{text_id}" CompositionName="Text">
            <ObjectList>
              <MultilingualTextItem ID="{text_item_id}" CompositionName="Items">
                <AttributeList>
                  <Culture>en-US</Culture>
                  <Text>{formatted_text}</Text>
                </AttributeList>
              </MultilingualTextItem>
            </ObjectList>
          </MultilingualText>
        </ObjectList>
      </{entry_tag}>
"""
            else:
                # GraphicList
                entries_xml += f"""      <{entry_tag} ID="{entry_id}" CompositionName="Entries">
        <AttributeList>
          <DefaultEntry>{is_default}</DefaultEntry>
          <EntryType>SingleValue</EntryType>
          <FlashingEnabled>false</FlashingEnabled>
          <FlashingRate>Slow</FlashingRate>
          <FlashTransparentColor>0, 0, 0</FlashTransparentColor>
          <From>{item['value']}</From>
          <To>{item['value']}</To>
          <TransparentColor>0, 0, 0</TransparentColor>
          <UseFlashTransparentColor>false</UseFlashTransparentColor>
          <UseTransparentColor>false</UseTransparentColor>
        </AttributeList>
        <LinkList>
          <Picture TargetID="@OpenLink">
            <Name>{item['target']}</Name>
          </Picture>
        </LinkList>
      </{entry_tag}>
"""

        comment_block = ""
        if self.comment:
            self.uid_counter += 1
            comment_id = self.uid_counter
            self.uid_counter += 1
            comment_item_id = self.uid_counter
            comment_block = f"""      <MultilingualText ID="{comment_id}" CompositionName="Comment">
        <ObjectList>
          <MultilingualTextItem ID="{comment_item_id}" CompositionName="Items">
            <AttributeList>
              <Culture>en-US</Culture>
              <Text>{self.comment}</Text>
            </AttributeList>
          </MultilingualTextItem>
        </ObjectList>
      </MultilingualText>"""

        # Extra attribute for GraphicList: Mode
        extra_attr = ""
        if self.list_type == "GraphicList":
            extra_attr = "\n      <Mode>Simple</Mode>"

        return f"""<?xml version="1.0" encoding="utf-8"?>
<Document>
  <Engineering version="V18" />
  <DocumentInfo>
    <Created>{datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')}</Created>
    <ExportSetting>WithDefaults</ExportSetting>
  </DocumentInfo>
  <{root_tag} ID="0">
    <AttributeList>
      <ListRange>Decimal</ListRange>{extra_attr}
      <Name>{self.list_name}</Name>
    </AttributeList>
    <ObjectList>
{comment_block}
{entries_xml}    </ObjectList>
  </{root_tag}>
</Document>"""


# =========================================================
# VÍ DỤ SỬ DỤNG / DRIVER (AI AGENTS SẼ GHI ĐÈ PHƯƠNG THỨC NÀY)
# =========================================================
if __name__ == "__main__":
    # 1. Sinh FB tiêu chuẩn
    builder = TIALadderBuilder(fb_name="FB_Tu_Dong")
    builder.add_network("Khởi động động cơ", [("NO", "AI_Nut_Khoi_Dong"), ("SetCoil", "AI_Dong_Co_Chay")])
    builder.add_network("Trễ mở van", [("NO", "AI_Dong_Co_Chay"), ("TON", "Timer_Van", "T#2S"), ("SetCoil", "AI_Van_Mo")])
    builder.add_network("Dừng chu trình", [("NC", "AI_Nut_Dung"), ("ResetCoil", "AI_Dong_Co_Chay")])
    xml_out = builder.generate_xml()
    with open("Output_FB_Tu_Dong.xml", "w", encoding="utf-8") as f:
        f.write(xml_out)
    print("[SUCCESS] Output_FB_Tu_Dong.xml generated!")

    # 2. Sinh OB30 cyclic interrupt với PID_Compact
    pid_ob = TIALadderBuilder(fb_name="Cyclic interrupt", block_id="30", block_type="OB")
    
    # Network 1: Khối PID Compact
    pid_ob.add_network("Điều khiển PID", [
        ("PID_Compact", "PID_Compact_1", 
         {"Setpoint": "AI_Nhiet_Do_SP", "Input": "AI_Nhiet_Do_PV"}, 
         {"Output": "AI_PID_Output"})
    ])
    
    # Network 2: Chọn chế độ PID
    pid_ob.add_network("Chọn chế độ PID", [
        ("NO", "bDong_Co_Dang_Chay"), 
        ("MOVE", "3", "PID_Compact_1.sRet.i_Mode")
    ])
    
    # Network 3: Mô phỏng quá trình bằng math box
    pid_ob.add_network("Mô phỏng quá trình", [
        ("GENERIC", "Calc", 
         {"in1": "AI_Nhiet_Do_PV", "in2": "0.95", "in3": "AI_PID_Output", "in4": "0.05", "in5": "0.5"},
         {"out": "AI_Nhiet_Do_PV"},
         {"Card": "5", "SrcType": "Real", "Equation": "IN2*IN1 + IN4*(IN3*IN5)"})
    ])

    ob_xml = pid_ob.generate_xml()
    # Ghi chú: OB cần khai báo secondary type
    ob_xml = ob_xml.replace("<SecondaryType>ProgramCycle</SecondaryType>", "<SecondaryType>CyclicInterrupt</SecondaryType>")
    with open("Output_OB30_PID.xml", "w", encoding="utf-8") as f:
        f.write(ob_xml)
    print("[SUCCESS] Output_OB30_PID.xml generated!")

    # 3. Sinh FB truyền thông để test các khối mới
    comm_fb = TIALadderBuilder(fb_name="FB_Comms", block_id="101", block_type="FB")
    
    # Bộ đếm CTU
    comm_fb.add_network("Kiểm tra bộ đếm CTU", [
        ("NO", "AI_Kich_Dem"),
        ("CTU", "IEC_Counter_0_DB", 
         {"R": "AI_Reset_Dem", "PV": "5"}, 
         {"Q": "AI_Dem_Xong", "CV": "AI_Gia_Tri_Dem"})
    ])
    
    # Cấu hình Modbus
    comm_fb.add_network("Kiểm tra cấu hình Modbus", [
        ("NO", "Quet_Dau"),
        ("MB_COMM_LOAD", "MB_COMM_LOAD_DB",
         {"REQ": "Quet_Dau", "PORT": "271", "BAUD": "19200", "MB_DB": "MB_MASTER_DB"},
         {"DONE": "AI_Modbus_Load_Xong", "ERROR": "AI_Modbus_Load_Loi", "STATUS": "AI_Modbus_Load_Trang_Thai"})
    ])
    
    # Modbus Master
    comm_fb.add_network("Kiểm tra Modbus Master", [
        ("NO", "AI_Modbus_Yeu_Cau"),
        ("MB_MASTER", "MB_MASTER_DB",
         {"REQ": "AI_Modbus_Yeu_Cau", "MB_ADDR": "2", "MODE": "1", "DATA_ADDR": "48502", "DATA_LEN": "1", "DATA_PTR": "AI_Modbus_Tu_Dieu_Khien"},
         {"DONE": "AI_Modbus_Master_Xong", "BUSY": "AI_Modbus_Master_Ban", "ERROR": "AI_Modbus_Master_Loi", "STATUS": "AI_Modbus_Master_Trang_Thai"})
    ])
    
    # S7 GET
    comm_fb.add_network("Kiểm tra truyền thông S7 GET", [
        ("NO", "Xung_1Hz"),
        ("GET", "GET_DB",
         {"REQ": "Xung_1Hz", "ID": "W#16#0100", "ADDR_1": "P#DB2.DBX0.0 BYTE 6", "RD_1": "P#DB10.DBX0.0 BYTE 6"},
         {"NDR": "GET_Du_Lieu_Moi", "ERROR": "GET_Loi", "STATUS": "GET_Trang_Thai"})
    ])
    
    # S7 PUT
    comm_fb.add_network("Kiểm tra truyền thông S7 PUT", [
        ("NO", "Xung_1Hz"),
        ("PUT", "PUT_DB",
         {"REQ": "Xung_1Hz", "ID": "W#16#0100", "ADDR_1": "P#DB1.DBX0.0 BYTE 6", "SD_1": "P#DB11.DBX0.0 BYTE 6"},
         {"DONE": "PUT_Xong", "ERROR": "PUT_Loi", "STATUS": "PUT_Trang_Thai"})
    ])

    comm_xml = comm_fb.generate_xml()
    with open("Output_FB_Comms.xml", "w", encoding="utf-8") as f:
        f.write(comm_xml)
    print("[SUCCESS] Output_FB_Comms.xml generated!")

