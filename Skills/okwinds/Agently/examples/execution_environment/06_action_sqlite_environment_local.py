import sqlite3
import tempfile
from pathlib import Path
from pprint import pprint

from agently import Agently


ACTION_ID = "query_local_sqlite"


def prepare_database(path: Path):
    connection = sqlite3.connect(path)
    connection.execute("create table issues (id integer primary key, title text, priority integer)")
    connection.executemany(
        "insert into issues (title, priority) values (?, ?)",
        [
            ("Action package examples", 2),
            ("Execution environment health check", 1),
            ("Legacy tool facade docs", 3),
        ],
    )
    connection.commit()
    connection.close()


def main():
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "issues.db"
        prepare_database(db_path)

        agent = Agently.create_agent()
        agent.enable_sqlite(database=str(db_path), action_id=ACTION_ID, expose_to_model=False)

        result = agent.action.execute_action(
            ACTION_ID,
            {
                "query": "select title, priority from issues where priority <= ? order by priority",
                "params": [2],
            },
        )

    print("[ACTION_RESULT]")
    pprint(result)
    assert result.get("status") == "success"
    rows = result.get("data", {}).get("rows", [])
    assert rows == [
        {"title": "Execution environment health check", "priority": 1},
        {"title": "Action package examples", "priority": 2},
    ]
    assert Agently.execution_environment.list(scope="action_call") == []


if __name__ == "__main__":
    main()

# Expected key output:
# [ACTION_RESULT] has status="success".
# data["rows"] contains "Execution environment health check" priority 1 and
# "Action package examples" priority 2.
# Action-call execution environment handles are released after the call.

# How it works:
# agent.enable_sqlite(database=str(db_path), action_id=ACTION_ID) registers a SQLite
# query action backed by a temp-dir database.  execute_action() runs a parameterized
# SELECT with params=[2], returning rows as a list of dicts.  The temp dir is cleaned
# up by the context manager after the assertions run.
#
# Flow:
# prepare_database(db_path): INSERT 3 issues into a temp SQLite file
#   |
#   v
# agent.enable_sqlite(database=str(db_path), action_id=ACTION_ID)
# execute_action(ACTION_ID, {"query":"SELECT... WHERE priority<=?","params":[2]})
#   |
#   v
# SQLiteEnvironment runs query -> rows = [
#   {"title":"Execution environment health check","priority":1},
#   {"title":"Action package examples","priority":2}]
# handle released -> list(scope="action_call") == []
