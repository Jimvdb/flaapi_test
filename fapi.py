import uvicorn
from fastapi import FastAPI, Response

app = FastAPI()


@app.get("/")
async def root():
    xml = '''
    <message>
        <text>Hello World</text>
        <text>FAPI power</text>
    </message>
    '''
    return Response(content=xml, media_type="application/xml")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


def start_fapi():
    uvicorn.run(app, host="0.0.0.0", port=8000)


class FAPI:

    def __init__(self):
        print("Thread fapi")

    def start(self):
        start_fapi()
