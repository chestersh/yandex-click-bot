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
-- new fields
alter table adhoc_parser.audit_yandex_bot add column title varchar(255) null;
alter table adhoc_parser.audit_yandex_bot add column ip varchar(255) null;
alter table adhoc_parser.audit_yandex_bot add column meta text null;
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
### RUN:
```shell script
docker build -t image-bot:0.4 . ; \
docker run \
--name yandex-bot-test \
-e TZ=Europe/Moscow \
--shm-size="1g" -d \
--restart=always \
-v /home/www/code/yandex-click-bot/src/logs:/app/src/logs/ image-bot:0.4
```


```shell script
docker build -t image-bot:0.3 . ; \
docker run \
--name yandex-bot-test \
-e TZ=Europe/Moscow \
--shm-size="1g" -d \
--restart=always \
-v /home/ubpc/docker-bot/yandex-click-bot/src/logs:/app/src/logs/ \
--network host \
image-bot:0.3
```


### pip install

```bash
python3 -m venv env
pip install -r req.txt
```