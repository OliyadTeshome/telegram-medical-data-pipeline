{{
  config(
    materialized='table'
  )
}}

with raw_messages as (
    select * from {{ ref('stg_raw_messages') }}
),

enriched_messages as (
    select * from {{ ref('stg_enriched_messages') }}
)

select
    rm.id as message_id,
    rm.chat_title,
    rm.sender_username,
    rm.message_text,
    rm.message_date,
    rm.has_media,
    em.medical_entities,
    em.sentiment_score,
    em.urgency_level,
    case 
        when em.sentiment_score > 0.5 then 'positive'
        when em.sentiment_score < -0.5 then 'negative'
        else 'neutral'
    end as sentiment_category,
    case 
        when array_length(em.medical_entities, 1) > 0 then true
        else false
    end as has_medical_content,
    array_length(em.medical_entities, 1) as medical_entity_count
from raw_messages rm
left join enriched_messages em on rm.id = em.raw_message_id 