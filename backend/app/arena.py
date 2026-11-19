"""Assessment records are private to this service. All scenario content is inert text."""
import json
import os
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Literal
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field, model_validator

router = APIRouter(prefix="/api/v1/arena")
CASES = [
    ("SMS phishing", "A Northstar Parcel text asks for a fee to release a package you never ordered.", "Check your orders in the official app", "Pay the fee in the text"),
    ("WhatsApp scam", "A message from an unfamiliar number claims to be your cousin and asks for emergency money.", "Call your cousin using your saved number", "Transfer the money immediately"),
    ("Banking notification", "An unexpected Riverstone Bank alert asks you to approve a payment.", "Decline and contact the bank independently", "Approve to clear the alert"),
    ("Fake KYC", "A fictional wallet agent asks for your one-time code to renew identity verification.", "End the chat and use the official support channel", "Share the code"),
    ("Email phishing", "An unexpected benefits email from Lumen Works asks you to sign in to claim a refund.", "Contact payroll using the staff directory", "Use the email sign-in prompt"),
    ("Malicious website", "A fictional prize page asks permission to send notifications and install a reward program.", "Close the page and decline its requests", "Install the reward program"),
    ("Password security", "Aster Club needs a new password. Your email account already has a strong password.", "Generate a unique password and enable MFA", "Reuse the email password"),
    ("Social engineering", "A caller claiming to be from Elm IT asks you to approve an unexpected MFA prompt.", "Deny the prompt and alert IT independently", "Approve it to help the caller"),
    ("QR phishing", "A sticker covers the printed payment code on a fictional parking meter.", "Verify payment instructions with the operator", "Trust the sticker and pay"),
    ("Suspicious attachment", "An unexpected invoice from Fern Office asks you to enable document macros.", "Report the message without opening the attachment", "Enable macros to read it"),
]
SCHEMA = """
CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY,email TEXT, batch TEXT DEFAULT '',active INTEGER DEFAULT 1);
CREATE TABLE IF NOT EXISTS instructors(uid TEXT PRIMARY KEY REFERENCES users);
CREATE TABLE IF NOT EXISTS labs(id INTEGER PRIMARY KEY,title TEXT,difficulty TEXT,passmark INTEGER,release TEXT, tasks TEXT,practice INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS assignments(id INTEGER PRIMARY KEY,uid TEXT REFERENCES users,lab INTEGER REFERENCES labs,due INTEGER,start INTEGER, UNIQUE(uid,lab));
CREATE TABLE IF NOT EXISTS results(aid INTEGER PRIMARY KEY REFERENCES assignments,score REAL,elapsed INTEGER,submitted INTEGER,details TEXT,released INTEGER,feedback TEXT DEFAULT '');
CREATE TABLE IF NOT EXISTS drafts(aid INTEGER PRIMARY KEY REFERENCES assignments,answers TEXT);
CREATE TABLE IF NOT EXISTS notices(id INTEGER PRIMARY KEY,uid TEXT REFERENCES users,message TEXT);
"""
@contextmanager
def database():
    path = Path(os.getenv("ARENA_DB", str(Path(__file__).resolve().parents[1] / "data/arena.sqlite")))
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=15)
    db.row_factory = sqlite3.Row
    try:
        db.execute("PRAGMA foreign_keys=ON")
        db.executescript(SCHEMA)
        db.execute("BEGIN IMMEDIATE")
        if not db.execute("SELECT 1 FROM labs WHERE practice=1").fetchone():
            tasks = [dict(category=c,prompt=p,options=[good,bad] if i%2 else [bad,good],correct=0 if i%2 else 1,points=1) for i,(c,p,good,bad) in enumerate(CASES)]
            db.execute("INSERT INTO labs(title,difficulty,passmark,release,tasks,practice) VALUES(?,?,?,?,?,1)",("Field assessment","Foundation",70,"immediate",json.dumps(tasks)))
        if not db.execute("SELECT 1 FROM labs WHERE practice=2").fetchone():
            full = db.execute("SELECT tasks FROM labs WHERE practice=1").fetchone()
            for task in json.loads(full[0]):
                db.execute("INSERT INTO labs(title,difficulty,passmark,release,tasks,practice) VALUES(?,?,?,?,?,2)",
                           (task["category"],"Foundation",100,"immediate",json.dumps([task])))
        yield db
        db.commit()
    finally:
        db.close()

async def identity(authorization: str = Header(default="")):
    from .main import forward
    user = await forward("GET","/auth/v1/user",authorization)
    with database() as db:
        db.execute("INSERT INTO users(id,email) VALUES(?,?) ON CONFLICT(id) DO UPDATE SET email=excluded.email",(user["id"],user.get("email","")))
        if not db.execute("SELECT active FROM users WHERE id=?", (user["id"],)).fetchone()[0]:
            raise HTTPException(403,"Training access suspended")
        owner = user.get("app_metadata",{}).get("role")=="admin"
        instructor = db.execute("SELECT 1 FROM instructors WHERE uid=?", (user["id"],)).fetchone()
    return user["id"],bool(owner or instructor),owner

def admin(user=Depends(identity)):
    if not user[1]:
        raise HTTPException(403,"Administrator required")
    return user

class Task(BaseModel):
    category: str = Field(min_length=1,max_length=80)
    prompt: str = Field(min_length=1,max_length=2000)
    options: list[str] = Field(min_length=2,max_length=6)
    correct: int = Field(ge=0)
    points: int = Field(ge=1,le=100)
    @model_validator(mode="after")
    def check(self):
        if self.correct >= len(self.options) or any(not x.strip() or len(x)>400 for x in self.options) or len(set(self.options))!=len(self.options):
            raise ValueError("Provide distinct choices and a valid correct answer")
        return self

class Lab(BaseModel):
    title: str = Field(min_length=1,max_length=120)
    difficulty: Literal["Foundation","Intermediate","Advanced"]
    passmark: int = Field(ge=0,le=100)
    release: Literal["immediate","manual"]
    tasks: list[Task] = Field(min_length=1,max_length=50)

class Assignment(BaseModel):
    lab: int
    uid: str = ""
    batch: str = ""
    due: int = Field(gt=0,le=253402300799)

class Member(BaseModel):
    batch: str = Field(max_length=80)
    active: bool

class Answers(BaseModel):
    answers: list[int] = Field(min_length=1,max_length=50)

class Review(BaseModel):
    feedback: str = Field(max_length=2000)
    released: bool

def rows(db,sql,args=()):
    return [dict(row) for row in db.execute(sql,args)]

@router.get("")
def dashboard(user=Depends(identity)):
    uid,is_admin,owner=user
    with database() as db:
        labs=rows(db,"SELECT id,title,difficulty,passmark,release,practice FROM labs WHERE practice>0 OR ? OR id IN (SELECT lab FROM assignments WHERE uid=?)",(is_admin,uid))
        records=rows(db,"SELECT a.*,l.title,l.passmark,r.submitted,r.released,r.score,r.elapsed,r.details,r.feedback FROM assignments a JOIN labs l ON l.id=a.lab LEFT JOIN results r ON r.aid=a.id WHERE ? OR a.uid=? ORDER BY a.id DESC",(is_admin,uid))
        for record in records:
            if record["submitted"] and (is_admin or record["released"]):
                record["details"]=json.loads(record["details"])
            else:
                for key in ("score","details","feedback","elapsed"):
                    record.pop(key,None)
        return dict(uid=uid,admin=is_admin,owner=owner,labs=labs,records=records,members=rows(db,"SELECT users.*,EXISTS(SELECT 1 FROM instructors WHERE instructors.uid=users.id) AS instructor FROM users ORDER BY email") if is_admin else [],notices=rows(db,"SELECT message FROM notices WHERE uid=? ORDER BY id DESC LIMIT 25",(uid,)))

@router.post("/labs")
def create(lab:Lab,user=Depends(admin)):
    with database() as db:
        return dict(id=db.execute("INSERT INTO labs(title,difficulty,passmark,release,tasks) VALUES(?,?,?,?,?)",(lab.title,lab.difficulty,lab.passmark,lab.release,json.dumps([t.model_dump() for t in lab.tasks]))).lastrowid)

@router.get("/labs/{lab_id}")
def lab_definition(lab_id:int,user=Depends(admin)):
    with database() as db:
        row=db.execute("SELECT * FROM labs WHERE id=?",(lab_id,)).fetchone()
        if not row:
            raise HTTPException(404,"Unknown lab")
        return {**dict(row),"tasks":json.loads(row["tasks"])}

@router.post("/labs/{lab_id}")
def update_lab(lab_id:int, lab:Lab,user=Depends(admin)):
    with database() as db:
        if db.execute("SELECT 1 FROM assignments WHERE lab=?",(lab_id,)).fetchone():
            raise HTTPException(409,"This lab has assignments. Save a new version to preserve their scoring.")
        changed=db.execute("UPDATE labs SET title=?, difficulty=?, passmark=?, release=?, tasks=? WHERE id=? AND practice=0",
                           (lab.title,lab.difficulty,lab.passmark,lab.release,json.dumps([t.model_dump() for t in lab.tasks]),lab_id))
        if not changed.rowcount:
            raise HTTPException(422,"Choose an authored lab to edit")
        return {"saved":True}

class Deadline(BaseModel):
    due:int = Field(gt=0,le=253402300799)

@router.post("/deadline/{aid}")
def reschedule(aid:int,change:Deadline,user=Depends(admin)):
    with database() as db:
        if change.due <= time.time():
            raise HTTPException(422,"Choose a future deadline")
        if not db.execute("UPDATE assignments SET due=? WHERE id=? AND NOT EXISTS(SELECT 1 FROM results WHERE aid=?)",
                          (change.due,aid,aid)).rowcount:
            raise HTTPException(409,"Choose an outstanding assignment")
        db.execute("INSERT INTO notices(uid,message) SELECT uid,'Assessment deadline changed' FROM assignments WHERE id=?",(aid,))
        return {"saved":True}

class InstructorRole(BaseModel):
    instructor:bool

@router.post("/instructors/{uid}")
def set_instructor(uid:str,role:InstructorRole,user=Depends(admin)):
    if not user[2]:
        raise HTTPException(403,"An account administrator must manage instructor roles")
    with database() as db:
        if not db.execute("SELECT 1 FROM users WHERE id=?",(uid,)).fetchone():
            raise HTTPException(404,"Unknown learner")
        if role.instructor:
            db.execute("INSERT OR IGNORE INTO instructors(uid) VALUES(?)",(uid,))
        else:
            db.execute("DELETE FROM instructors WHERE uid=?",(uid,))
        return {"saved":True}

@router.post("/assign")
def assign(a:Assignment,user=Depends(admin)):
    with database() as db:
        if bool(a.uid)==bool(a.batch) or a.due<=time.time() or not db.execute("SELECT 1 FROM labs WHERE id=?",(a.lab,)).fetchone():
            raise HTTPException(422,"Choose one audience, an existing lab and a future deadline")
        people=rows(db,"SELECT id FROM users WHERE active=1 AND ((?<>'' AND id=?) OR (?<>'' AND batch=?))",(a.uid,a.uid,a.batch,a.batch))
        if not people:
            raise HTTPException(404,"No active learners matched")
        count=0
        for person in people:
            if db.execute("INSERT OR IGNORE INTO assignments(uid,lab,due) VALUES(?,?,?)",(person["id"],a.lab,a.due)).rowcount:
                db.execute("INSERT INTO notices(uid,message) VALUES(?,?)",(person["id"],"New assessment assigned"))
                count+=1
        return dict(assigned=count)

@router.post("/members/{uid}")
def member(uid:str,m:Member,user=Depends(admin)):
    if not user[2]:
        raise HTTPException(403,"An account administrator must manage training access")
    if uid==user[0] and not m.active:
        raise HTTPException(422,"Cannot suspend your own account")
    with database() as db:
        if not db.execute("UPDATE users SET batch=?,active=? WHERE id=?",(m.batch.strip(),m.active,uid)).rowcount:
            raise HTTPException(404,"Unknown learner")
    return {"saved":True}

@router.post("/practice")
def practice(user=Depends(identity)):
    with database() as db:
        db.execute("INSERT OR IGNORE INTO assignments(uid,lab) SELECT ?,id FROM labs WHERE practice=1",(user[0],))
        return dict(id=db.execute("SELECT a.id FROM assignments a JOIN labs l ON l.id=a.lab WHERE uid=? AND practice=1",(user[0],)).fetchone()[0])

@router.post("/practice/{lab_id}")
def practice_scenario(lab_id:int,user=Depends(identity)):
    with database() as db:
        if not db.execute("SELECT 1 FROM labs WHERE id=? AND practice>0",(lab_id,)).fetchone():
            raise HTTPException(404,"Practice scenario unavailable")
        db.execute("INSERT OR IGNORE INTO assignments(uid,lab) VALUES(?,?)",(user[0],lab_id))
        aid = db.execute("SELECT id FROM assignments WHERE uid=? AND lab=?",(user[0],lab_id)).fetchone()[0]
        return {"id":aid}

def available(db,aid,uid):
    row=db.execute("SELECT a.*,l.tasks,l.release FROM assignments a JOIN labs l ON l.id=a.lab WHERE a.id=? AND uid=?",(aid,uid)).fetchone()
    if not row:
        raise HTTPException(404,"Assignment unavailable")
    if db.execute("SELECT 1 FROM results WHERE aid=?",(aid,)).fetchone():
        raise HTTPException(409,"Already submitted")
    if row["due"] and time.time()>row["due"]:
        raise HTTPException(409,"Deadline passed")
    return row

@router.post("/attempt/{aid}")
def start(aid:int,user=Depends(identity)):
    with database() as db:
        row=available(db,aid,user[0])
        db.execute("UPDATE assignments SET start=COALESCE(start,?) WHERE id=?",(int(time.time()),aid))
        return [dict(category=t["category"],prompt=t["prompt"],options=t["options"]) for t in json.loads(row["tasks"])]

@router.get("/draft/{aid}")
def draft(aid:int,user=Depends(identity)):
    with database() as db:
        available(db,aid,user[0])
        row=db.execute("SELECT answers FROM drafts WHERE aid=?",(aid,)).fetchone()
        return json.loads(row[0]) if row else []

@router.post("/draft/{aid}")
def save_draft(aid:int,a:Answers,user=Depends(identity)):
    with database() as db:
        row=available(db,aid,user[0])
        tasks=json.loads(row["tasks"])
        if not row["start"] or len(a.answers)!=len(tasks) or any(not -1<=v<len(t["options"]) for v,t in zip(a.answers,tasks)):
            raise HTTPException(422,"Invalid draft")
        db.execute("INSERT INTO drafts VALUES(?,?) ON CONFLICT(aid) DO UPDATE SET answers=excluded.answers",(aid,json.dumps(a.answers)))
    return {"saved":True}

@router.post("/submit/{aid}")
def submit(aid:int,a:Answers,user=Depends(identity)):
    with database() as db:
        row=available(db,aid,user[0])
        tasks=json.loads(row["tasks"])
        if not row["start"] or len(tasks)!=len(a.answers) or any(not 0<=i<len(t["options"]) for i,t in zip(a.answers,tasks)):
            raise HTTPException(422,"Complete all tasks in a started attempt")
        details=[dict(category=t["category"],prompt=t["prompt"],decision=t["options"][i],safe=t["options"][t["correct"]],ok=i==t["correct"],points=t["points"]) for i,t in zip(a.answers,tasks)]
        score=round(100*sum(d["points"] for d in details if d["ok"])/sum(d["points"] for d in details),2)
        now=int(time.time())
        db.execute("INSERT INTO results(aid,score,elapsed,submitted,details,released) VALUES(?,?,?,?,?,?)",(aid,score,now-row["start"],now,json.dumps(details),row["release"]=="immediate"))
        db.execute("DELETE FROM drafts WHERE aid=?",(aid,))
        return {"submitted":True}

@router.post("/review/{aid}")
def review(aid:int,r:Review,user=Depends(admin)):
    with database() as db:
        if not db.execute("UPDATE results SET feedback=?,released=? WHERE aid=?",(r.feedback,r.released,aid)).rowcount:
            raise HTTPException(404,"Submission unavailable")
        db.execute("INSERT INTO notices(uid,message) SELECT uid,'Assessment review updated' FROM assignments WHERE id=?",(aid,))
    return {"saved":True}
