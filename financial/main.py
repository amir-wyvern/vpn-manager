from fastapi import FastAPI

from router import (
    user,
    deposit,
    transfer,
    auth
)
from db import models, db_config
from db.database import engine, get_db
from dotenv import load_dotenv
import os
from pathlib import Path

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)

description = """
This api allows you to create a payment gateway on the blockchain platform. 🚀

## Items

* Deposit
* Withdraw
* Local Transfer 

## Users

You will be able to:

* **Create users** 
* **Read users** 
* **Edit users** 
"""
app = FastAPI(    
    title="Tether-GateWay",
    description=description,
    version="0.0.1",
    contact={
        "name": "WyVern",
        "email": "amirhosein_wyvern@yahoo.com"
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },) 
app.include_router(user.router)
app.include_router(deposit.router)
app.include_router(transfer.router)
app.include_router(auth.router)

models.Base.metadata.create_all(engine)
db_config.init_table(get_db().__next__()) 