import marimo

__generated_with = "0.16.5"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import micropip
    import json
    import marimo as mo
    PATH_TO_HORUS_ASN1 = mo.notebook_location() / "public" / "HorusBinaryV3.asn1"
    return micropip, mo


@app.cell(hide_code=True)
async def _(micropip, mo):

    await micropip.install("asn1tools")
    await micropip.install("wcwidth")
    await micropip.install(str(mo.notebook_location() / "public" / "blockdiag-3.3.0-py3-none-any.whl" ))
    await micropip.install("sqlite3")
    await micropip.install("nwdiag")
    return


@app.cell(hide_code=True)
def _(mo):
    import requests
    try:
        ASN1_DEF = requests.get(str(mo.notebook_location() / "public" / "HorusBinaryV3.asn1" )).text
    except:
        ASN1_DEF = open(str(mo.notebook_location() / "public" / "HorusBinaryV3.asn1"),"r").read()
    from packetdiag import parser, builder, drawer
    return ASN1_DEF, builder, drawer, parser


@app.cell
def _(mo):
    mo.md(
        r"""
    ## HorusBinaryV3 ASN.1
    ### Importing, Compiling and Encoding with the ASN.1 codec
    """
    )
    return


@app.cell(hide_code=True)
def _(ASN1_DEF, mo):
    MAX_HEIGHT=400
    asn1_editor = mo.ui.code_editor(value=ASN1_DEF,language="asn1",label="HorusBinaryV3.asn1", max_height=MAX_HEIGHT,min_height=MAX_HEIGHT)

    editor = mo.ui.code_editor("""
    data = {
        "payloadCallsign": "VK3FUR",
        "sequenceNumber": 1234,

        "timeOfDaySeconds": 9001,
        "latitude": 123.945893903,
        "longitude": -23.344589499,
        "altitudeMeters": 23000,

        "velocityHorizontalKilometersPerHour": 200,
        "gnssSatellitesVisible": 18,

        "temperatureCelsius": {
            "internal": 10,
            "external": 20
        },
        "milliVolts": {
            "battery": 2300
        },

        "ascentRateCentimetersPerSecond": 1080,
        "humidityPercentage": [10],

        "extraSensors": [
            {
                "name": "rad", 
                "values": ("horusInt", [1,2,3])
            }
        ],

        "safeMode": True,
        "powerSave": True,
        "gpsLock": True,
    }
    """,language="python",label="Data to encode", max_height=MAX_HEIGHT,min_height=MAX_HEIGHT)


    the_stack = mo.hstack([ asn1_editor.style({"width":"50%"}), editor.style({"width":"50%"})])
    the_stack
    return asn1_editor, editor


@app.cell(hide_code=True)
def _(editor, mo):
    return_value=""
    exec_data={}
    try:
        exec("data =" + editor.value,globals=exec_data)
        data = exec_data['data']
    except:
        try:
            exec("data =" + editor.value)
        except:
            data = {"payloadCallsign": "VK3FUR",
        "sequenceNumber": 1234,

        "timeOfDaySeconds": 9001,
        "latitude": 123.945893903,
        "longitude": -23.344589499,
        "altitudeMeters": 23000}
            return_value="""
    <p style="color:red;font-size:12pt">Error parsing encoding data. Ensure that you have a valid python dictonary. Will use demo data for the time being.</p>
    """
    mo.md(return_value)
    return (data,)


@app.cell
def _(asn1_editor, data):
    import asn1tools
    HorusBinaryV3 = asn1tools.compile_string(asn1_editor.value, codec="uper")
    output = HorusBinaryV3.encode('Telemetry', data)
    print(f"{output.hex()}")

    return HorusBinaryV3, asn1tools, output


@app.cell(hide_code=True)
def _(mo, output):
    mo.md(
        f"""
    |    |    |
    | -- | -- |
    | <p align="left"> **Payload data** </p> | `{output.hex()}` |
    | <p align="left"> **Payload bytes** </p> | <p align="left"> {len(output)} </p> |

    ### Packet layout
    """
    )
    return


@app.cell(hide_code=True)
def _(HorusBinaryV3, asn1tools, builder, data, drawer, mo, parser):
    import inspect
    class VizEncoder(asn1tools.codecs.uper.Encoder):
        def __init__(self, *args, **kwargs):
            self.map = []
            self.last_frame = None
            super().__init__(*args, **kwargs)

        def inspect(self, calling_frame):

            try:
                label = calling_frame['self'].type_label()
            except:
                label = f"{calling_frame['self'].name} ({calling_frame['self'].type_name})"

            if inspect.stack()[2] != self.last_frame:
                self.last_frame=inspect.stack()[2]
                if len(self.map)>0:
                    self.map[-1]["end"] = self.number_of_bits-1
                    self.map.append({
                        "label": label,
                        "start": self.number_of_bits
                    })
                else:
                    self.map.append({
                        "label": label,
                        "start": 0
                    })

        def append_bit(self, *args, **kwargs):      
            frame = inspect.currentframe()
            calling_frame=frame.f_back.f_locals
            self.inspect(calling_frame)
            super().append_bit(*args, **kwargs)


        def append_non_negative_binary_integer(self, *args, **kwargs):
            frame = inspect.currentframe()
            calling_frame=frame.f_back.f_locals
            if type(frame.f_back.f_locals['self']) != VizEncoder:
                self.inspect(calling_frame)
                super().append_non_negative_binary_integer(*args, **kwargs)
            else:
                try_back = frame.f_back
                for x in range(0,8):
                    if type(try_back.f_locals['self']) != VizEncoder:
                        self.inspect(try_back.f_locals)
                        super().append_non_negative_binary_integer(*args, **kwargs)
                        return
                    else:
                        try_back = try_back.f_back

        def as_bytearray(self, *args, **kwargs):
            if len(self.map)>0:
                    self.map[-1]["end"] = self.number_of_bits-1
            return super().as_bytearray(*args, **kwargs)



    encoderviz = VizEncoder()
    HorusBinaryV3._types['Telemetry']._type.encode(data,encoderviz)
    output_viz = encoderviz.as_bytearray()

    lines = """
    {
      colwidth = 32
      node_height = 80
      node_width = 38

    """


    for x in encoderviz.map:
        label = x['label'].replace("(",' \\n(')
        output_viz_bytes = output_viz[x['start']//8:x['end']//8+1]
        bin_data = "".join([format(x,'08b') for x in output_viz_bytes])
        offset = x['start'] % 8
        end_offset = 7-(x['end'] % 8)
        lines += f"  {x['start']}-{x['end']}: {label}\\n\\n\\n\\n\\n\\n{bin_data[offset:-end_offset]}\n"
    lines += """
    }
    """

    tree = parser.parse_string(lines)
    diagram = builder.ScreenNodeBuilder(tree)

    draw = drawer.DiagramDraw("SVG", diagram.build(tree),
                                      ignore_pil=True)
    draw.draw()
    import base64
    output_64 = base64.b64encode(draw.save().encode()).decode()
    mo.accordion(items={"Click to show/hide payload layout": mo.image(src=f"data:image/svg+xml;base64,{output_64}")},lazy=False)
    return


@app.cell
def _(mo):
    mo.md(r"""### Decoding""")
    return


@app.cell(hide_code=True)
def _(mo, output):
    text = mo.ui.text(placeholder="Hex data 7bba....", label="Telemetery to decode (in hex): ",value=output.hex(),full_width=True)
    mo.vstack([text])
    return (text,)


@app.cell
def _(HorusBinaryV3, mo, text):
    decoded = HorusBinaryV3.decode('Telemetry', bytes.fromhex(text.value))
    mo.show_code()
    return (decoded,)


@app.cell(hide_code=True)
def _(decoded, mo):
    mo.json(decoded)
    return


if __name__ == "__main__":
    app.run()
