"""Pruebas de persistencia en bases temporales, nunca en la base real."""
from contextlib import closing
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts/s07"))
import almacen_eventos as m
from contrato_eventos import make_event

NOW="2026-11-24T03:00:00Z"


def event(**kw):
    args=dict(source="FRR_S02",subject="OSPF",resource_id="OSPF-HQ-s1p",
              site="HQ",peer_site="S1",state="NORMAL",available=True,
              observed_at_utc="2026-11-24T02:59:50Z",received_at_utc=NOW,
              details={"neighbor_state":"Full"})
    args.update(kw)
    return make_event(**args)


def batch(*events):
    return {"schema":m.BATCH_SCHEMA,"mode":"READ_ONLY",
            "network_mutations_authorized":False,"events":list(events)}


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/"events.sqlite3"
        self.db=m.open_store(self.path)
        self.addCleanup(self.db.close)

    def test_insert_and_reopen(self):
        e=event()
        self.assertEqual(m.import_batch(self.db,batch(e))["inserted"],1)
        with closing(m.open_store(self.path)) as db:
            self.assertEqual(m.history(db),[e])
            self.assertEqual(m.summary(db)["integrity"],"ok")

    def test_replay_idempotent(self):
        e=event()
        m.import_batch(self.db,batch(e))
        self.assertEqual(m.import_batch(self.db,batch(e)),
                         {"received":1,"inserted":0,"duplicates":1,"late":0})

    def test_repeat_reception_preserves_original(self):
        e=event()
        later=event(received_at_utc="2026-11-24T03:00:01Z")
        self.assertEqual(e["event_id"],later["event_id"])
        m.import_batch(self.db,batch(e,later))
        self.assertEqual(m.history(self.db),[e])

    def test_late_across_batches(self):
        newer=event()
        older=event(observed_at_utc="2026-11-24T02:59:40Z")
        m.import_batch(self.db,batch(newer))
        self.assertEqual(m.import_batch(self.db,batch(older))["late"],1)
        self.assertEqual(m.history(self.db),[older,newer])
        self.assertEqual(m.summary(self.db)["late"],1)

    def test_future_does_not_poison_watermark(self):
        future=event(observed_at_utc="2026-11-24T03:00:10Z")
        m.import_batch(self.db,batch(future))
        self.assertEqual(m.import_batch(self.db,batch(event()))["late"],0)

    def test_conflicting_observations_retained(self):
        a=event()
        b=event(state="DEGRADED",details={"neighbor_state":"Init"})
        self.assertEqual(m.import_batch(self.db,batch(a,b))["inserted"],2)

    def test_tampered_id_rejected(self):
        e=event()
        e["event_id"]="fake"
        with self.assertRaises(ValueError):
            m.import_batch(self.db,batch(e))

    def test_batch_atomic_validation(self):
        e=event()
        bad=dict(e,network_mutations_authorized=True)
        with self.assertRaises(ValueError):
            m.import_batch(self.db,batch(e,bad))
        self.assertEqual(m.summary(self.db)["total"],0)

    def test_sql_failure_rollback(self):
        self.db.execute("CREATE TRIGGER abort_bad BEFORE INSERT ON events "
                        "WHEN NEW.resource_id='OSPF-HQ-s1b' "
                        "BEGIN SELECT RAISE(ABORT,'test'); END")
        self.db.commit()
        import sqlite3
        with self.assertRaises(sqlite3.IntegrityError):
            m.import_batch(self.db,batch(event(),event(resource_id="OSPF-HQ-s1b")))
        self.assertEqual(m.history(self.db),[])

    def test_missing_and_invalid_roundtrip(self):
        a=event(available=False)
        b=event(observed_at_utc="invalid")
        m.import_batch(self.db,batch(a,b))
        self.assertEqual({e["quality"] for e in m.history(self.db)},{"MISSING","INVALID"})

    def test_stale_roundtrip(self):
        e=event(observed_at_utc="2026-11-24T02:58:00Z")
        m.import_batch(self.db,batch(e))
        self.assertEqual(m.history(self.db),[e])
        self.assertEqual(m.summary(self.db)["mode"],"HISTORICAL_NOT_LIVE")

    def test_wrong_batch_authorization(self):
        b=batch(event())
        b["network_mutations_authorized"]=True
        with self.assertRaises(ValueError):
            m.import_batch(self.db,b)

    def test_other_stream_not_late(self):
        m.import_batch(self.db,batch(event()))
        b=event(resource_id="OSPF-HQ-s1b",observed_at_utc="2026-11-24T02:59:40Z")
        self.assertEqual(m.import_batch(self.db,batch(b))["late"],0)

    def test_reject_unrelated_database(self):
        import sqlite3
        other=Path(self.tmp.name)/"other.db"
        with closing(sqlite3.connect(other)) as db:
            db.execute("CREATE TABLE unrelated(x)")
        with self.assertRaisesRegex(ValueError,"UNRECOGNIZED_DATABASE"):
            m.open_store(other)


if __name__=="__main__":
    unittest.main()
