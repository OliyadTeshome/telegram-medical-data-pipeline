{{
  config(
    materialized='view'
  )
}}

select
    id,
    message_id,
    chat_id,
    chat_title,
    sender_id,
    sender_username,
    message_text,
    message_date,
    has_media,
    media_type,
    media_path,
    created_at
from {{ source('raw', 'raw_messages') }} 