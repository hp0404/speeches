-- public.view_paragraphs source

CREATE OR REPLACE VIEW public.view_paragraphs AS 
WITH ordered_sentences AS (
    SELECT
        sentences.id,
        sentences.document_id,
        sentences.paragraph_id,
        sentences.sentence_id,
        sentences.speaker,
        sentences.text,
        sentences.text_lemmatized
    FROM sentences
    ORDER BY
        sentences.document_id,
        sentences.paragraph_id,
        sentences.sentence_id
),
aggregated_paragraphs AS (
    SELECT
        ordered_sentences.document_id,
        ordered_sentences.paragraph_id,
        string_agg(ordered_sentences.text::TEXT, ' '::TEXT) AS paragraph_contents,
        string_agg(ordered_sentences.text_lemmatized::TEXT, ' '::TEXT) AS paragraph_contents_lemmatized
    FROM ordered_sentences
    GROUP BY 
        ordered_sentences.document_id,
        ordered_sentences.paragraph_id
), paragraphs AS (
    SELECT
        t1.document_id,
        t1.paragraph_id,
        t2.speaker,
        t1.paragraph_contents,
        t1.paragraph_contents_lemmatized
    FROM aggregated_paragraphs t1
    LEFT JOIN (
        SELECT DISTINCT ON (
                ordered_sentences.document_id,
                ordered_sentences.paragraph_id
            ) 
            ordered_sentences.document_id,
            ordered_sentences.paragraph_id,
            ordered_sentences.speaker
        FROM ordered_sentences
        ) t2 ON t1.document_id = t2.document_id
        AND t1.paragraph_id = t2.paragraph_id
    ORDER BY
        t1.document_id,
        t1.paragraph_id
)
SELECT 
    t1.document_id,
    t2.title,
    t2."date" AS "date_published",
    t2.url,
    t1.paragraph_id,
    t1.speaker,
    t1.paragraph_contents,
    t1.paragraph_contents_lemmatized,
    t3.theme_arr
FROM paragraphs t1
LEFT JOIN documents_metadata t2 ON t1.document_id = t2.id
LEFT JOIN (
        SELECT document_id, array_agg(theme) AS theme_arr
        FROM themes
        GROUP BY document_id
    ) t3 ON t1.document_id = t3.document_id
ORDER BY t2."date" DESC;
