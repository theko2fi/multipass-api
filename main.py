from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from multipass_sdk.multipass import MultipassClient

from pydantic import BaseModel

from typing import Union

import uvicorn

class Payload(BaseModel):
    cmd: str

class Instance(BaseModel):
    name: str
    cpu: int = 1
    mem: str = '2G'
    disk: str = '5G'
    cloud_init: Union[str, None] = None
    image: str = 'ubuntu-lts'

app = FastAPI()

@app.middleware("http")
async def middleware(request: Request, call_next):
 try:
   response = await call_next(request)
   return response
 except Exception as e:
   return JSONResponse(status_code=400, content={"message": str(e)})

@app.get("/instances")
def list_instances():
    return MultipassClient().list()

@app.get("/instances/{name}")
def instance_info(name: str):
    return MultipassClient().get_vm(vm_name=name).info()

@app.post("/instances/{name}/exec")
def exec_command(data: Payload, name: str):
    vm = MultipassClient().get_vm(vm_name=name)
    stdout, stderr = vm.exec(cmd_to_execute=data.cmd)
    return {"result": stdout, "error": stderr}

@app.post("/instances/{name}/recover")
def recover_instance(name: str):
    return MultipassClient().recover(vm_name=name)

@app.delete("/instances/{name}")
def delete_instance(name: str, purge: bool = False):
    return MultipassClient().get_vm(vm_name=name).delete(purge=purge)

@app.post("/instances/{name}/stop")
def stop_instance(name: str):
    vm = MultipassClient().get_vm(vm_name=name)
    return vm.stop()
    #return {"result": f"instance {name} has been stopped successfully"}

@app.post("/instances/{name}/start")
def start_instance(name: str):
    vm = MultipassClient().get_vm(vm_name=name)
    return vm.start()
    #return {"result": f"instance {name} has been started successfully"}

@app.post("/instances/{name}/restart")
def restart_instance(name: str):
    return MultipassClient().get_vm(vm_name=name).restart()

@app.post("/instances")
def launch_instance(data: Instance):
    vm_data = data.dict()
    vm_data["vm_name"] = vm_data.pop("name")  # Renaming 'name' back to 'vm_name'
    return MultipassClient().launch(**vm_data)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9990, reload=True)