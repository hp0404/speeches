-- public.view_paragraphs source

CREATE OR REPLACE VIEW public.view_sentences AS 
SELECT 
    t2.title,
    t2."date" AS "date_published",
    t2.url,
    t3.theme_arr,
    t1.document_id,
    t1.id AS "sentence_id",
    t1.paragraph_id AS "paragraph_order",
    t1.sentence_id AS "sentence_order",
    t1."text" AS "sentence_contents",
    t1.text_lemmatized AS "sentence_contents_lemmatized"
FROM sentences t1
LEFT JOIN documents_metadata t2 ON t1.document_id = t2.id
LEFT JOIN (
        SELECT document_id, array_agg(theme) AS theme_arr
        FROM themes
        GROUP BY document_id
    ) t3 ON t1.document_id = t3.document_id
ORDER BY t2."date" DESC, document_id, paragraph_id, sentence_id;
