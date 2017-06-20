import pytest
from time import sleep
from bson import objectid, errors, json_util

from models.clients import blockchain_watcher as bw
from core.utils import *

from core import base_orga, base_project

from tests.fixtures import *

from ethjsonrpc import wei_to_ether

password = "simon"

def test_create_project(miner, testOrga):
	ret = base_orga.createProjectFromOrga(miner, password, testOrga.get('_id'), {"name": "kawa_bunga_project", "description": "This project aims to promote the culture of kawa bungo around the world", "invited_users": {}})
	assert ret.get('status') == 200
	assert ret.get('data').startswith('0x')
	bw.waitTx(ret.get('data'))
	sleep(0.5)
	testOrga.reload()
	assert len(testOrga["projects"]) == 1

def test_join_project(miner, testProject):
	ret = base_project.joinProject(miner, password, testProject.get('_id'), tag="member")
	assert ret.get('status') == 200
	assert ret.get('data').startswith('0x')
	bw.waitTx(ret.get('data'))
	sleep(0.5)
	testProject.reload()
	miner.reload()
	assert len(testProject["members"]) == 1
	assert len(miner["projects"]) == 1

def test_create_poll(miner, testOrga):
	bw.stop()
	pass
	