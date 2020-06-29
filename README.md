# yandex-click-bot


### initialize

```postgres-psql
create table adhoc_parser.audit_yandex_bot (
	id serial,
	url text not null,
	report_date date not null,
	parse_time timestamp not null,
	has_403 varchar(1) not null,
	waste_time integer not null,
	CONSTRAINT audit_pkey PRIMARY KEY (id, report_date)
) partition by range (report_date);
```

### create partitions with T+50

```postgres-psql
do $do$
declare
    d date;
begin
    for d in
        select generate_series(date(now()), date(now())+50, interval '1 day')
    loop
    execute format($f$
        create table adhoc_parser.audit_yandex_bot__%s%s%s partition of adhoc_parser.audit_yandex_bot
        for values from (%L) to (%L)
        $f$, 
        to_char(d, 'YYYY'), to_char(d, 'MM'),to_char(d, 'dd'), d, d+ interval '1 day');
    end loop;
end 
$do$
```

### pip install

```bash
python3 -m venv env

pip install -r req.txt
```