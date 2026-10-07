# check_api.py -- tests every route of the running API and cleans up after itself.
# 1) Start the server:   fastapi dev app.py
# 2) In a 2nd terminal:  python check_api.py      (it asks for the admin login)
import getpass
import os
import sys
from decimal import Decimal

import httpx

BASE = "http://127.0.0.1:8000"
client = httpx.Client(base_url=BASE, timeout=10)
results = []


def check(name, response, expected):
    ok = response.status_code == expected
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name:42} expected {expected}, got {response.status_code}")
    if not ok:
        print("       ", response.text[:300])
    return response


def run():
    username = os.environ.get("ADMIN_USERNAME") or input("Admin username: ")
    password = os.environ.get("ADMIN_PASSWORD") or getpass.getpass("Admin password: ")
    ids = {}
    try:
        check("health (open)", client.get("/health"), 200)

        # ---- auth ----
        check("no token is rejected", client.get("/classes"), 401)
        check("fake token is rejected", client.get("/classes", headers={"Authorization": "Bearer abc.def.ghi"}), 401)
        check("wrong password is rejected", client.post("/auth/login", data={"username": username, "password": password + "x"}), 401)
        r1 = check("login", client.post("/auth/login", data={"username": username, "password": password}), 200)
        r2 = check("login again", client.post("/auth/login", data={"username": username, "password": password}), 200)
        if r1.status_code != 200 or r2.status_code != 200:
            print("Login failed - cannot test the other routes. Run: python create_admin.py")
            return
        different = r1.json()["access_token"] != r2.json()["access_token"]
        results.append(different)
        print(f"{'PASS' if different else 'FAIL'}  every login gives a new token (expires in {r2.json()['expires_in']}s)")
        client.headers["Authorization"] = f"Bearer {r2.json()['access_token']}"
        check("/auth/me", client.get("/auth/me"), 200)

        # ---- classes ----
        r = client.post("/classes", json={"class_name": "ZZ-TEST"})
        if r.status_code == 409:  # left over from an earlier run
            old = [c for c in client.get("/classes?limit=100").json() if c["class_name"] == "ZZ-TEST"]
            client.delete(f"/classes/{old[0]['class_id']}")
            r = client.post("/classes", json={"class_name": "ZZ-TEST"})
        check("create class", r, 201)
        ids["class"] = r.json()["class_id"]
        cid = ids["class"]
        check("duplicate class name", client.post("/classes", json={"class_name": "ZZ-TEST"}), 409)
        check("class name too long", client.post("/classes", json={"class_name": "x" * 21}), 422)
        check("list classes", client.get("/classes"), 200)
        check("get class", client.get(f"/classes/{cid}"), 200)
        check("get missing class", client.get("/classes/999999"), 404)
        check("update class", client.put(f"/classes/{cid}", json={"class_name": "ZZ-TEST-2"}), 200)

        # ---- students ----
        student = {"first_name": "Test", "last_name": "Student", "parent_name": "Test Parent",
                   "phone": "9876543210", "class_id": cid}
        r = check("create student", client.post("/students", json=student), 201)
        ids["student"] = r.json()["student_id"]
        sid = ids["student"]
        check("student missing phone", client.post("/students", json={k: v for k, v in student.items() if k != "phone"}), 422)
        check("student bad class_id", client.post("/students", json={**student, "class_id": 999999}), 404)
        check("list students", client.get("/students"), 200)
        check("list students by class", client.get(f"/students?class_id={cid}"), 200)
        check("get student", client.get(f"/students/{sid}"), 200)
        check("update student", client.put(f"/students/{sid}", json={**student, "first_name": "Changed"}), 200)
        check("get missing student", client.get("/students/999999"), 404)

        # ---- fees ----
        r = check("create fee", client.post("/fees", json={"class_id": cid, "total_amount": "50000.00", "due_date": "2026-12-31"}), 201)
        ids["fee"] = r.json()["fee_id"]
        fid = ids["fee"]
        check("duplicate fee for class", client.post("/fees", json={"class_id": cid, "total_amount": "1", "due_date": "2026-12-31"}), 409)
        check("fee bad class_id", client.post("/fees", json={"class_id": 999999, "total_amount": "1", "due_date": "2026-12-31"}), 404)
        check("fee negative amount", client.post("/fees", json={"class_id": cid, "total_amount": "-5", "due_date": "2026-12-31"}), 422)
        check("list fees", client.get("/fees"), 200)
        check("get fee", client.get(f"/fees/{fid}"), 200)
        check("update fee", client.put(f"/fees/{fid}", json={"total_amount": "60000", "due_date": "2027-01-15"}), 200)

        # ---- payments ----
        r = check("create payment", client.post("/payments", json={"student_id": sid, "amount_paid": "20000", "payment_method": "cash"}), 201)
        ids["payment"] = r.json()["payment_id"]
        pid = ids["payment"]
        check("create 2nd payment", client.post("/payments", json={"student_id": sid, "amount_paid": "10000.50", "payment_method": "upi"}), 201)
        check("payment bad student_id", client.post("/payments", json={"student_id": 999999, "amount_paid": "5", "payment_method": "cash"}), 404)
        check("payment zero amount", client.post("/payments", json={"student_id": sid, "amount_paid": "0", "payment_method": "cash"}), 422)
        check("list payments", client.get(f"/payments?student_id={sid}"), 200)
        check("get payment", client.get(f"/payments/{pid}"), 200)
        check("update payment", client.put(f"/payments/{pid}", json={"amount_paid": "25000", "payment_method": "cash"}), 200)

        r = check("fee summary", client.get(f"/payments/student/{sid}/summary"), 200)
        if r.status_code == 200:
            s = r.json()
            math_ok = Decimal(s["total_fee"]) - Decimal(s["total_paid"]) == Decimal(s["balance_due"])
            results.append(math_ok)
            print(f"{'PASS' if math_ok else 'FAIL'}  summary math: {s['total_fee']} - {s['total_paid']} = {s['balance_due']}")

        # ---- protection rules ----
        check("delete class that has students", client.delete(f"/classes/{cid}"), 409)
    finally:
        # ---- cleanup (children first) ----
        if ids:
            print("--- cleanup ---")
        if "payment" in ids:
            check("delete payment", client.delete(f"/payments/{ids['payment']}"), 204)
        if "student" in ids:
            check("delete student", client.delete(f"/students/{ids['student']}"), 204)
            check("deleted student is gone", client.get(f"/students/{ids['student']}"), 404)
        if "fee" in ids:
            check("delete fee", client.delete(f"/fees/{ids['fee']}"), 204)
        if "class" in ids:
            check("delete class", client.delete(f"/classes/{ids['class']}"), 204)


try:
    run()
except httpx.ConnectError:
    print("Cannot connect. Is the server running?  ->  fastapi dev app.py")
    sys.exit(1)

passed = sum(results)
print(f"\n{passed}/{len(results)} checks passed")
sys.exit(0 if passed == len(results) else 1)