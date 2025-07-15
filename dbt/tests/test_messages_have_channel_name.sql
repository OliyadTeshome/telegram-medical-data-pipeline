-- Custom test: messages must have channel_name
select *
from {{ ref('stg_telegram_messages') }}
where channel_name is null 