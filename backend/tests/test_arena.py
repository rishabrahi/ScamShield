import time
from fastapi.testclient import TestClient
from app import main

def test_assessment_lifecycle(monkeypatch,tmp_path):
    monkeypatch.setenv("ARENA_DB",str(tmp_path/"training.sqlite"))
    async def identity(method,path,token,payload=None):
        uid=token.split()[-1]
        return {"id":uid,"email":uid+"@example.test","app_metadata":{"role":"admin" if uid=="teacher" else "learner"}}
    monkeypatch.setattr(main,"forward",identity)
    client=TestClient(main.app)
    def req(uid,route="",body=None):
        return client.request("GET" if body is None else "POST","/api/v1/arena"+route,headers={"Authorization":"Bearer "+uid},json=body)
    for uid in ("teacher","alice","bob"):
        assert req(uid).is_success
    lab={"title":"Check first","difficulty":"Intermediate","passmark":75,"release":"manual","tasks":[{"category":"QR phishing","prompt":"A parking code is covered by a sticker.","options":["Verify with operator","Pay immediately"],"points":3,"correct":0}]}
    assert req("alice","/labs",lab).status_code==403
    lid=req("teacher","/labs",lab).json()["id"]
    assert req("teacher",f"/labs/{lid}").json()["tasks"]==lab["tasks"]
    assert req("teacher",f"/labs/{lid}",lab).is_success
    assert req("teacher","/instructors/bob",{"instructor":True}).is_success
    assert req("bob").json()["admin"]
    assert req("bob","/instructors/alice",{"instructor":True}).status_code==403
    assert req("bob","/members/teacher",{"batch":"","active":False}).status_code==403
    assert req("teacher","/instructors/bob",{"instructor":False}).is_success
    assert not req("bob").json()["admin"]
    req("teacher","/members/alice",{"active":True,"batch":"first"})
    allocation={"lab":lid,"batch":"first","due":int(time.time())+300}
    assert req("teacher","/assign",allocation).json()["assigned"]==1
    assert req("teacher","/assign",allocation).json()["assigned"]==0
    aid=req("alice").json()["records"][0]["id"]
    assert req("teacher",f"/labs/{lid}",lab).status_code==409
    assert req("teacher",f"/deadline/{aid}",{"due":int(time.time())+600}).is_success
    assert req("bob",f"/attempt/{aid}",{}).status_code==404
    assert "correct" not in req("alice",f"/attempt/{aid}",{}).json()[0]
    assert req("alice",f"/submit/{aid}",{"answers":[17]}).status_code==422
    assert req("alice",f"/submit/{aid}",{"answers":[0]}).is_success
    assert req("alice",f"/submit/{aid}",{"answers":[0]}).status_code==409
    assert "score" not in req("alice").json()["records"][0]
    assert req("teacher",f"/review/{aid}",{"feedback":"Well verified","released":True}).is_success
    assert req("alice").json()["records"][0]["score"]==100
    practice=[l for l in req("bob").json()["labs"] if l["practice"]==2]
    assert len(practice)==10
    for scenario in practice:
        url=f"/practice/{scenario['id']}"
        exercise=req("bob",url,{}).json()["id"]
        assert req("bob",url,{}).json()["id"]==exercise
        task=req("bob",f"/attempt/{exercise}",{}).json()
        assert len(task)==1 and task[0]["category"]==scenario["title"]
        assert req("bob",f"/draft/{exercise}",{"answers":[0]}).is_success
        assert req("bob",f"/draft/{exercise}").json()==[0]
        assert req("bob",f"/submit/{exercise}",{"answers":[0]}).is_success
    assert req("bob",f"/practice/{lid}",{}).status_code==404
    arena=req("bob","/practice",{}).json()["id"]
    assert len(req("bob",f"/attempt/{arena}",{}).json())==10
    assert req("teacher","/assign",{**allocation,"due":1}).status_code==422
    assert req("teacher","/members/bob",{"active":False,"batch":""}).is_success
    assert req("bob").status_code==403
