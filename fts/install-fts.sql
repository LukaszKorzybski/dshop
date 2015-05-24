CREATE LANGUAGE plpgsql;

--
-- Return variant names in a form of concatenated string.
--
CREATE OR REPLACE FUNCTION fts_variants_as_str(p_article_id integer) RETURNS text AS $$
DECLARE
    names text;
    variant main_articlevariant%ROWTYPE;
BEGIN
    names := '';
    FOR variant IN SELECT * FROM main_articlevariant v WHERE article_id = p_article_id LOOP
        names := names || variant.variant || '. ';
    END LOOP;
    return names;
END;
$$ LANGUAGE plpgsql;


--
-- Return properties of article in a form of concatenated string.
--
CREATE OR REPLACE FUNCTION fts_properties_as_str(p_article_id integer) RETURNS text AS $$
DECLARE
    props text;
    prop RECORD;
BEGIN
    props := '';
    FOR prop IN SELECT * FROM main_articleproperty c WHERE article_id = p_article_id LOOP
        props := props || prop.value || '. ';
    END LOOP;
    return props;
END;
$$ LANGUAGE plpgsql;


--
-- Articles view for full-text search indexer.
--
CREATE OR REPLACE VIEW fts_articles AS SELECT
    sa.id,
    sa."name" AS "name",
    lower(sa."name") AS sort_name,
    p."name" AS producer,
    sa.short_desc || ' ' || sa."desc" AS "desc",
    fts_variants_as_str(sa.id) AS variants,
    trunc(date_part('epoch', sa.created)) AS created,
    sa.frontpage,
    sa.category_id,
    sa.producer_id,
    sa."new",
    sa.recommended,
    c.r_lid_path AS categories,
    CASE
        WHEN promo.id IS NULL THEN false
        WHEN promo.id IS NOT NULL THEN true
    END AS promotion,
    COALESCE(promo.net, a.net) AS net,
    COALESCE(promo.gross, a.gross) AS gross
FROM
    main_shoparticle sa
    INNER JOIN main_article a ON (sa.article_id = a.id)
    INNER JOIN main_producer p ON (sa.producer_id = p.id)
    INNER JOIN main_category c ON (sa.category_id = c.id)
    LEFT OUTER JOIN main_promotion promo ON (promo.article_id = a.id)

WHERE
    sa.public = true AND
    p.public = true;