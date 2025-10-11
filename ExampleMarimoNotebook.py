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
async def _(micropip):

    await micropip.install("asn1tools")
    await micropip.install("wcwidth")
    await micropip.install("sqlite3")
    return


@app.cell(hide_code=True)
def _(mo):
    import requests
    try:
        ASN1_DEF = requests.get(str(mo.notebook_location() / "public" / "HorusBinaryV3.asn1" )).text
    except:
        ASN1_DEF = open(str(mo.notebook_location() / "public" / "HorusBinaryV3.asn1"),"r").read()
    return (ASN1_DEF,)


@app.cell(hide_code=True)
def _(ASN1_DEF, mo):
    mo.md(
        f"""
    ### HorusBinaryV3 ASN.1
    ```asn1
    {ASN1_DEF}
    ```
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""### Importing and Compiling the ASN.1 codec""")
    return


@app.cell
def _(ASN1_DEF, mo):
    import asn1tools
    HorusBinaryV3 = asn1tools.compile_string(ASN1_DEF, codec="uper")
    mo.show_code()
    return (HorusBinaryV3,)


@app.cell
def _(mo):
    mo.md(r"""### Encoding""")
    return


@app.cell
def _(mo):
    editor = mo.ui.code_editor("""
    data = {
        "payloadCallsign": "VK3FUR",
        "sequenceNumber": 1234,

        "timeOfDaySeconds": 9001,
        "latitude": 123.945893903,
        "longitude": -23.344589499,
        "altitudeMeters": 23000,

        "velocityHorizontalMetersPerSecond": 200,
        "gnssSatellitesVisible": 18,

        "temperatureCelsius": [-120, 20],
        "milliVolts": [2300],

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
        "gpsLock": True
    }
    """,language="python")
    editor
    return (editor,)


@app.cell
def _(editor):
    exec_data={}
    try:
        exec(editor.value,globals=exec_data)
        data = exec_data['data']
    except:
        exec(editor.value)

    return (data,)


@app.cell
def _(HorusBinaryV3, data, mo):
    output = HorusBinaryV3.encode('Telemetry', data)
    print(f"{output.hex()}")
    mo.show_code()
    return (output,)


@app.cell(hide_code=True)
def _(mo, output):
    mo.md(
        f"""
    ```
    {output.hex()}
    ```
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""### Decoding""")
    return


@app.cell(hide_code=True)
def _(mo, output):
    text = mo.ui.text(placeholder="Hex data 7bba....", label="Decode Telemetery Hex: ",value=output.hex())
    mo.vstack([text])
    return (text,)


@app.cell
def _(HorusBinaryV3, mo, text):
    decoded = HorusBinaryV3.decode('Telemetry', bytes.fromhex(text.value))
    mo.show_code()
    return (decoded,)


@app.cell(hide_code=True)
def _(decoded, mo):
    mo.inspect(decoded, docs=False)
    return


if __name__ == "__main__":
    app.run()
