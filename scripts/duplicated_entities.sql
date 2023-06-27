WITH duplicated_entities AS (
    SELECT
        ef.id
    FROM
        extracted_features ef
    LEFT JOIN (
            SELECT
                DISTINCT ON
                (
                    sentence_id,
                    entity_type,
                    "label",
                    "match",
                    match_processed,
                    span_location
                ) id
            FROM
                public.extracted_features
        ) subquery ON
        ef.id = subquery.id
    WHERE
        subquery.id IS NULL
)
DELETE FROM extracted_features WHERE id IN (SELECT id FROM duplicated_entities);