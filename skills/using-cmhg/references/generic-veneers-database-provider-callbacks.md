# Generic veneers for database provider callbacks

## What they are used for

Database provider modules register generic veneer entries as operation callbacks with DBResultManager. DBResultManager then calls those entries to open/close databases and start/search/end result streams.

Typical entries:

- Database open/close entries: `DBSOpen_Entry/DBSOpen`, `DBSClose_Entry/DBSClose`.
- Search lifecycle entries: `DBSStart_Entry/DBSStart`, `DBSSearch_Entry/DBSSearch`, `DBSEnd_Entry/DBSEnd`.
- Startup service announcement entry: `CallBack_Entry/CallBack`.

## CMHG form

```cmhg
generic-veneers: DBSStart_Entry/DBSStart,
                 DBSSearch_Entry/DBSSearch,
                 DBSEnd_Entry/DBSEnd,
                 DBSOpen_Entry/DBSOpen,
                 DBSClose_Entry/DBSClose
```

## C usage

The provider fills a `dbresultext_t` with entry addresses and workspace:

```c
db.open_func = (void *)DBSOpen_Entry;
db.close_func = (void *)DBSClose_Entry;
db.start_func = (void *)DBSStart_Entry;
db.search_func = (void *)DBSSearch_Entry;
db.end_func = (void *)DBSEnd_Entry;
db.ws = pw;

_swix(DBResultManager_Register, _INR(0,1), 0, &db);
```

The handlers expose a register-based ABI. A typical SQL-backed provider uses:

- `DBSOpen`: `r0` flags, `r1` filename, returns database handle in `r0`.
- `DBSClose`: `r1` database handle.
- `DBSStart`: `r1` database handle, `r2` search string, returns search handle in `r0`.
- `DBSSearch`: `r1` search handle, `r2` buffer, `r3` buffer length, `r4` timeout; returns state in `r0`, flags in `r1`, and used/required length in `r3`.
- `DBSEnd`: ends the search handle.

## Notes

- Deregister by provider ID in finalisation.
- Allocate per-search state in `DBSStart` and free it in `DBSEnd`.
- Preserve the documented register contract; DBResultManager does not know the C types behind the generic veneer.
