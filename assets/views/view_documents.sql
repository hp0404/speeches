-- public.view_documents source

CREATE OR REPLACE VIEW public.view_documents AS 
WITH documents AS (
    SELECT
        ordered_sentences.document_id,
        string_agg(ordered_sentences.text::TEXT, ' '::TEXT) AS document_contents,
        string_agg(ordered_sentences.text_lemmatized::TEXT, ' '::TEXT) AS document_contents_lemmatized
    FROM
        (
            SELECT
                s.id,
                s.document_id,
                s.paragraph_id,
                s.sentence_id,
                s.speaker,
                s.text,
                s.text_lemmatized
            FROM sentences s
            ORDER BY
                s.document_id,
                s.paragraph_id,
                s.sentence_id
        ) ordered_sentences
    GROUP BY ordered_sentences.document_id
)
SELECT 
    t1.document_id,
    t2.title,
    t2."date" AS "date_published",
    t2.url,
    t1.document_contents,
    t1.document_contents_lemmatized,
    t3.theme_arr
FROM
    documents t1
LEFT JOIN documents_metadata t2 ON t1.document_id = t2.id
LEFT JOIN (
        SELECT document_id, array_agg(theme) AS theme_arr
        FROM themes
        GROUP BY document_id
    ) t3 ON t1.document_id = t3.document_id
ORDER BY t2."date" DESC;
