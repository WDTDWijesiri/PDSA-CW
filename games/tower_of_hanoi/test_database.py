from database import init_db, insert_result, fetch_all

def test_db():
    init_db()
    insert_result("Test", 3, 5, 31, 31, 1.2, 0.001)
    rows = fetch_all()
    assert len(rows) >= 1
