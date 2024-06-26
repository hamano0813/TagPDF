import sqlite3

from core import functions


def update_database(path: str):
    _update_kw(path)


def _update_kw(path: str):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE pdf ADD COLUMN kw VARCHAR(250)")
        cursor.execute("ALTER TABLE tag ADD COLUMN kw VARCHAR(250)")
        cursor.execute("ALTER TABLE pub ADD COLUMN kw VARCHAR(250)")
        conn.commit()

        cursor.execute("SELECT id, tit, num, rls FROM pdf")
        pdfs = cursor.fetchall()

        for fid, tit, num, rls in pdfs:
            tit_kw = functions.gen_keywords(tit) if tit else ""
            num_kw = functions.gen_keywords(num) if num else ""
            rls_kw = functions.gen_keywords(str(rls)) if rls else ""
            keyword = f"{tit_kw}|{num_kw}|{rls_kw}"
            keyword = keyword.replace("||", "|")
            keyword = keyword.strip("|")
            cursor.execute("UPDATE pdf set kw=? where id=?", (keyword, fid))

        cursor.execute("SELECT tag FROM tag")
        tags = cursor.fetchall()
        for (tag,) in tags:
            tag_kw = functions.gen_keywords(tag)
            cursor.execute("UPDATE tag set kw=? where tag=?", (tag_kw, tag))

        cursor.execute("SELECT pub FROM pub")
        pubs = cursor.fetchall()
        for (pub,) in pubs:
            pub_kw = functions.gen_keywords(pub)
            cursor.execute("UPDATE pub set kw=? where pub=?", (pub_kw, pub))
        print("The software version update with added keyword filtering has been completed.")

    except sqlite3.OperationalError as e:
        print(e)
        print("The software version featuring keyword filtering has been updated.")

    finally:
        cursor.close()
        conn.commit()
